"""L1 offline tests for the district lifecycle state machine (DESIGN.md §18).

Zero LLM calls, zero network, temp directories only. Covers the derived status
(uninitialized / initialized / locked), lock idempotency + the no-unlock rule,
PATCH (409 when locked, rename with metadata sync, 409 on a taken name), copy
(initialized, unlocked, zero household data) and the household/home build gate
on both the Steps sheet (BuildState) and the job HTTP path.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import importlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest import mock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
DASHBOARD = os.path.join(PROJECT_ROOT, "dashboard")
for _path in (SRC, DASHBOARD):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import generate_world as gw  # noqa: E402
from fastapi import HTTPException  # noqa: E402

from backend import build as build_module  # noqa: E402
from backend import districts as districts_service  # noqa: E402
from backend import models, world_admin  # noqa: E402
from backend.routers import build as build_router  # noqa: E402


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class DistrictLifecycleBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        self.trash = os.path.join(self._tmp.name, "_trash")
        os.makedirs(self.worlds, exist_ok=True)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", self.worlds),
            mock.patch.object(gw, "TRASH_DIR", self.trash),
            mock.patch.object(world_admin, "WORLDS_DIR", self.worlds),
            mock.patch.object(world_admin, "TRASH_DIR", self.trash),
        ]
        for patch in self._patches:
            patch.start()
        os.makedirs(self.world_dir(), exist_ok=True)
        _write_json(self.world_json(), {"world_id": "w1", "districts": []})

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    # -- layout helpers ---------------------------------------------------
    def world_dir(self, world_id="w1"):
        return os.path.join(self.worlds, world_id)

    def world_json(self, world_id="w1"):
        return os.path.join(self.world_dir(world_id), "world.json")

    def district_path(self, name, world_id="w1"):
        return os.path.join(self.world_dir(world_id), name)

    def district_json(self, name, world_id="w1"):
        return os.path.join(self.district_path(name, world_id), "district.json")

    def lock_marker(self, name, world_id="w1"):
        return os.path.join(self.district_path(name, world_id), ".locked")

    def add_district(self, name="clayton", description=None, postcode=None, location=None):
        gw.add_district("w1", name)
        meta = _read_json(self.district_json(name))
        if description is not None:
            meta["description"] = description
        if postcode is not None:
            meta["postcode"] = postcode
        if location is not None:
            meta["location"] = location
        _write_json(self.district_json(name), meta)
        if description:
            _write_text(os.path.join(self.district_path(name), "description.md"), description + "\n")
        return name

    def add_house(self, name, label="house_0001", household=None):
        house = os.path.join(self.district_path(name), label)
        os.makedirs(house, exist_ok=True)
        _write_json(os.path.join(house, "household.json"), household or {"home": {}, "members": []})
        return house

    # -- router helpers (the frozen HTTP contract) ------------------------
    def list_districts(self):
        return build_router.world_districts_list("w1")

    def create_district(self, name):
        return build_router.world_districts_create("w1", models.DistrictCreateRequest(name=name))

    def patch_district(self, name, new_name=None, description=None):
        return build_router.world_districts_patch(
            "w1", name, models.DistrictPatchRequest(name=new_name, description=description)
        )

    def lock_district(self, name):
        return build_router.world_districts_lock("w1", name)

    def copy_district(self, name, new_name=None):
        return build_router.world_districts_copy(
            "w1", name, models.DistrictCopyRequest(name=new_name)
        )

    def assert_http_error(self, status, fn, *args, **kwargs):
        with self.assertRaises(HTTPException) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.status_code, status)
        self.assertTrue(str(ctx.exception.detail))
        return ctx.exception


class StatusDerivationTests(DistrictLifecycleBase):
    def test_new_district_is_uninitialized(self):
        self.add_district("clayton")
        record = self.list_districts()[0]
        self.assertEqual(record.name, "clayton")
        self.assertFalse(record.has_description)
        self.assertEqual(record.status, "uninitialized")
        self.assertIsNone(record.locked_at)
        self.assertEqual(world_admin.district_status(False, False), "uninitialized")

    def test_description_makes_it_initialized(self):
        self.add_district("clayton", description="A student suburb.")
        record = self.list_districts()[0]
        self.assertTrue(record.has_description)
        self.assertEqual(record.description, "A student suburb.")
        self.assertEqual(record.status, "initialized")
        self.assertIsNone(record.locked_at)
        self.assertEqual(world_admin.district_status(True, False), "initialized")

    def test_lock_marker_makes_it_locked(self):
        self.add_district("clayton", description="A student suburb.")
        info = self.lock_district("clayton")
        self.assertEqual(info.status, "locked")
        self.assertTrue(info.locked_at)
        self.assertEqual(world_admin.district_status(True, True), "locked")
        self.assertEqual(self.list_districts()[0].status, "locked")

    def test_status_is_derived_not_stored(self):
        self.add_district("clayton")
        self.add_district("dockside", description="Docks.")
        _write_text(self.lock_marker("dockside"), "2026-01-02T03:04:05\n")
        statuses = {info.name: info.status for info in self.list_districts()}
        self.assertEqual(
            statuses, {"clayton": "uninitialized", "dockside": "locked"}
        )

    def test_district_json_has_no_persisted_status_field(self):
        self.add_district("clayton", description="A student suburb.")
        self.lock_district("clayton")
        meta = _read_json(self.district_json("clayton"))
        self.assertNotIn("status", meta)
        self.assertNotIn("locked_at", meta)


class LockTests(DistrictLifecycleBase):
    def test_lock_writes_iso_timestamp_into_marker_file(self):
        self.add_district("clayton", description="A student suburb.")
        info = self.lock_district("clayton")
        self.assertTrue(os.path.isfile(self.lock_marker("clayton")))
        with open(self.lock_marker("clayton"), encoding="utf-8") as fh:
            stored = fh.read().strip()
        self.assertEqual(stored, info.locked_at)
        self.assertEqual(datetime.fromisoformat(stored).year, datetime.now().year)

    def test_lock_is_idempotent_and_keeps_the_first_timestamp(self):
        self.add_district("clayton", description="A student suburb.")
        first = self.lock_district("clayton")
        _write_text(self.lock_marker("clayton"), "2001-01-01T00:00:00\n")
        second = self.lock_district("clayton")
        self.assertEqual(second.locked_at, "2001-01-01T00:00:00")
        self.assertNotEqual(second.locked_at, first.locked_at)
        self.assertEqual(second.status, "locked")

    def test_lock_missing_district_is_400(self):
        self.assert_http_error(400, self.lock_district, "ghost")

    def test_lock_missing_world_is_404(self):
        self.assert_http_error(404, build_router.world_districts_lock, "nope", "clayton")

    def test_there_is_no_unlock_surface(self):
        paths = [getattr(route, "path", "") for route in build_router.router.routes]
        self.assertEqual([p for p in paths if "unlock" in p.lower()], [])
        self.assertEqual([n for n in dir(world_admin) if "unlock" in n.lower()], [])
        self.assertEqual([n for n in dir(models) if "unlock" in n.lower()], [])


class PatchTests(DistrictLifecycleBase):
    def test_description_is_replaced_and_status_flips(self):
        self.add_district("clayton")
        info = self.patch_district("clayton", description="Rewritten brief.")
        self.assertEqual(info.description, "Rewritten brief.")
        self.assertTrue(info.has_description)
        self.assertEqual(info.status, "initialized")
        self.assertEqual(_read_json(self.district_json("clayton"))["description"], "Rewritten brief.")
        with open(os.path.join(self.district_path("clayton"), "description.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read().strip(), "Rewritten brief.")

    def test_empty_description_returns_to_uninitialized(self):
        self.add_district("clayton", description="A student suburb.")
        info = self.patch_district("clayton", description="   ")
        self.assertFalse(info.has_description)
        self.assertEqual(info.status, "uninitialized")

    def test_patch_is_refused_with_409_when_locked(self):
        self.add_district("clayton", description="A student suburb.")
        self.lock_district("clayton")
        self.assert_http_error(409, self.patch_district, "clayton", description="no")
        self.assert_http_error(409, self.patch_district, "clayton", new_name="other")
        self.assertEqual(self.list_districts()[0].status, "locked")

    def test_service_raises_locked_error_without_touching_disk(self):
        self.add_district("clayton", description="A student suburb.")
        world_admin.lock_district("w1", "clayton")
        with self.assertRaises(world_admin.DistrictLockedError):
            world_admin.edit_district("w1", "clayton", description="no")
        self.assertEqual(_read_json(self.district_json("clayton"))["description"], "A student suburb.")

    def test_rename_moves_directory_and_syncs_metadata(self):
        self.add_district(
            "clayton",
            description="A student suburb.",
            postcode="3168",
            location={"district": "clayton", "state": "VIC"},
        )
        self.add_house("clayton")
        _write_text(os.path.join(self.district_path("clayton"), "notes.txt"), "keep me")

        info = self.patch_district("clayton", new_name="clayton_north")

        self.assertEqual(info.name, "clayton_north")
        self.assertEqual(info.status, "initialized")
        self.assertFalse(os.path.isdir(self.district_path("clayton")))
        self.assertTrue(os.path.isdir(self.district_path("clayton_north")))
        self.assertTrue(os.path.isfile(os.path.join(self.district_path("clayton_north"), "notes.txt")))

        meta = _read_json(self.district_json("clayton_north"))
        self.assertEqual(meta["name"], "clayton_north")
        self.assertEqual(meta["postcode"], "clayton_north")
        self.assertEqual(meta["location"], {"district": "clayton_north", "state": "VIC"})
        self.assertEqual(meta["description"], "A student suburb.")

        world = _read_json(self.world_json())
        self.assertEqual([entry["name"] for entry in world["districts"]], ["clayton_north"])
        self.assertEqual(world["districts"][0]["postcode"], "clayton_north")

        self.assertTrue(
            os.path.isfile(
                os.path.join(self.district_path("clayton_north"), "house_0001", "household.json")
            )
        )

    def test_rename_leaves_other_districts_and_their_order_intact(self):
        self.add_district("clayton", description="A student suburb.")
        self.add_district("dockside", description="Docks.")
        self.assertEqual(self.patch_district("clayton", new_name="clayton_north").name,
                         "clayton_north")
        self.assertEqual(
            [info.name for info in self.list_districts()],
            ["clayton_north", "dockside"],
        )
        self.assertEqual(_read_json(self.district_json("dockside"))["description"], "Docks.")

    def test_rename_is_refused_with_409_when_target_exists(self):
        self.add_district("clayton", description="A student suburb.")
        self.add_district("dockside", description="Docks.")
        self.assert_http_error(409, self.patch_district, "clayton", new_name="dockside")
        self.assertTrue(os.path.isdir(self.district_path("clayton")))
        self.assertEqual(_read_json(self.world_json())["districts"][0]["name"], "clayton")

    def test_rename_to_the_same_name_is_a_noop(self):
        self.add_district("clayton", description="A student suburb.")
        info = self.patch_district("clayton", new_name="clayton")
        self.assertEqual(info.name, "clayton")
        self.assertTrue(os.path.isdir(self.district_path("clayton")))

    def test_patch_missing_district_is_400(self):
        self.assert_http_error(400, self.patch_district, "ghost", description="x")

    def test_rename_updates_legacy_string_entries(self):
        self.add_district("clayton", description="A student suburb.")
        _write_json(self.world_json(), {"world_id": "w1", "districts": ["clayton"]})
        info = self.patch_district("clayton", new_name="clayton_north")
        self.assertEqual(info.name, "clayton_north")
        self.assertEqual(
            _read_json(self.world_json())["districts"],
            [{"name": "clayton_north", "postcode": "clayton_north"}],
        )
        self.assertEqual([item.name for item in self.list_districts()], ["clayton_north"])


class CopyTests(DistrictLifecycleBase):
    def _source(self):
        self.add_district(
            "clayton",
            description="A student suburb.",
            postcode="3168",
            location={"district": "clayton"},
        )
        meta = _read_json(self.district_json("clayton"))
        meta["economic_level"] = "low"
        _write_json(self.district_json("clayton"), meta)
        self.add_house("clayton")
        _write_json(
            os.path.join(self.district_path("clayton"), "households.json"),
            {"households": [{"house": "house_0001"}]},
        )
        return "clayton"

    def test_copy_is_initialized_unlocked_and_holds_no_households(self):
        source = self._source()
        source_description = _read_json(self.district_json(source))["description"]

        info = self.copy_district(source)

        self.assertEqual(info.name, "clayton_copy")
        self.assertTrue(info.has_description)
        self.assertEqual(info.status, "initialized")
        self.assertIsNone(info.locked_at)
        self.assertEqual(info.description, source_description)
        self.assertEqual(info.house_count, 0)

        copied = self.district_path("clayton_copy")
        self.assertEqual(
            sorted(os.listdir(copied)),
            ["description.md", "district.json"],
        )
        self.assertFalse(os.path.isfile(self.lock_marker("clayton_copy")))

    def test_copy_carries_the_brief_keys_only(self):
        self._source()
        self.copy_district("clayton")
        meta = _read_json(self.district_json("clayton_copy"))
        self.assertEqual(meta["description"], "A student suburb.")
        self.assertEqual(meta["postcode"], "3168")
        self.assertEqual(meta["location"], {"district": "clayton"})
        self.assertEqual(meta["economic_level"], "low")
        self.assertEqual(meta["copied_from"], "clayton")
        self.assertEqual(meta["name"], "clayton_copy")

    def test_copy_default_name_increments(self):
        self._source()
        self.assertEqual(self.copy_district("clayton").name, "clayton_copy")
        self.assertEqual(self.copy_district("clayton").name, "clayton_copy2")
        self.assertEqual(self.copy_district("clayton").name, "clayton_copy3")

    def test_copy_accepts_an_explicit_free_name(self):
        self._source()
        self.assertEqual(self.copy_district("clayton", new_name="clayton_v2").name, "clayton_v2")

    def test_copy_explicit_taken_name_is_409(self):
        self._source()
        self.add_district("taken", description="Docks.")
        self.assert_http_error(409, self.copy_district, "clayton", new_name="taken")

    def test_copy_of_a_locked_source_is_unlocked(self):
        self._source()
        self.lock_district("clayton")
        info = self.copy_district("clayton")
        self.assertEqual(info.status, "initialized")
        self.assertIsNone(info.locked_at)
        self.assertFalse(os.path.isfile(self.lock_marker("clayton_copy")))
        self.assertEqual(self.list_districts()[0].name, "clayton")
        self.assertEqual(self.list_districts()[0].status, "locked")

    def test_copy_leaves_the_source_untouched(self):
        self._source()
        self.copy_district("clayton")
        self.assertTrue(os.path.isdir(os.path.join(self.district_path("clayton"), "house_0001")))
        self.assertTrue(os.path.isfile(os.path.join(self.district_path("clayton"), "households.json")))

    def test_copy_missing_district_is_400(self):
        self.assert_http_error(400, self.copy_district, "ghost")


class GateTests(DistrictLifecycleBase):
    def _district_with_household(self):
        self.add_district("clayton", description="A student suburb.")
        self.add_house("clayton")
        return "clayton"

    def _steps(self):
        return {step.step: step for step in world_admin.build_state("w1").steps}

    def test_household_and_home_are_blocked_before_lock(self):
        self._district_with_household()
        steps = self._steps()
        for name in ("household", "home"):
            self.assertFalse(steps[name].runnable)
            self.assertEqual(steps[name].blocked_reason, world_admin.LOCK_REQUIRED_REASON)
        self.assertIn("Lock the district first", steps["household"].blocked_reason)

    def test_household_is_blocked_before_lock_even_with_no_houses(self):
        self.add_district("clayton", description="A student suburb.")
        steps = self._steps()
        self.assertFalse(steps["household"].runnable)
        self.assertEqual(steps["household"].blocked_reason, world_admin.LOCK_REQUIRED_REASON)

    def test_household_is_runnable_after_lock_with_no_houses(self):
        self.add_district("clayton", description="A student suburb.")
        world_admin.lock_district("w1", "clayton")
        steps = self._steps()
        self.assertTrue(steps["household"].runnable)
        self.assertIsNone(steps["household"].blocked_reason)
        self.assertFalse(steps["household"].done)

    def test_home_stays_blocked_after_lock_with_no_houses(self):
        self.add_district("clayton", description="A student suburb.")
        world_admin.lock_district("w1", "clayton")
        steps = self._steps()
        self.assertFalse(steps["home"].runnable)
        self.assertEqual(steps["home"].blocked_reason, "no households yet; run 'household' first")

    def test_gate_is_visible_on_the_build_state_http_payload(self):
        self._district_with_household()
        state = build_router.world_build_state("w1")
        steps = {step.step: step for step in state.steps}
        self.assertFalse(steps["household"].runnable)
        self.assertFalse(steps["home"].runnable)
        self.assertIn("Lock the district first", steps["household"].blocked_reason)

    def test_district_step_is_not_gated(self):
        self.add_district("clayton", description="A student suburb.")
        self.assertTrue(self._steps()["district"].runnable)
        world_admin.lock_district("w1", "clayton")
        self.assertTrue(self._steps()["district"].runnable)

    def test_both_steps_become_runnable_after_lock(self):
        self._district_with_household()
        world_admin.lock_district("w1", "clayton")
        steps = self._steps()
        for name in ("household", "home"):
            self.assertTrue(steps[name].runnable, name)
            self.assertIsNone(steps[name].blocked_reason, name)

    def test_build_job_argv_refuses_before_lock_and_allows_after(self):
        self._district_with_household()
        request = models.JobRequest(
            kind="build", step="household", world="w1", district="clayton", confirm=True
        )
        with self.assertRaises(ValueError) as ctx:
            build_module.build_step_argv(request)
        self.assertEqual(str(ctx.exception), world_admin.LOCK_REQUIRED_REASON)

        world_admin.lock_district("w1", "clayton")
        argv, _warnings = build_module.build_step_argv(request)
        self.assertIn("clayton", argv)

    def test_build_job_argv_refuses_home_before_lock(self):
        self._district_with_household()
        request = models.JobRequest(
            kind="build", step="home", world="w1", district="clayton", confirm=True
        )
        with self.assertRaises(ValueError) as ctx:
            build_module.build_step_argv(request)
        self.assertEqual(str(ctx.exception), world_admin.LOCK_REQUIRED_REASON)

    def test_build_job_argv_leaves_the_district_step_alone(self):
        self.add_district("clayton")
        request = models.JobRequest(
            kind="build",
            step="district",
            world="w1",
            district="clayton",
            preset="clayton_3168",
            confirm=True,
        )
        argv, _warnings = build_module.build_step_argv(request)
        self.assertIn("s1_district_description.py", argv[1])

    def test_direct_job_http_call_is_refused_before_lock(self):
        self._district_with_household()
        routers_jobs = self._import_jobs_with_temp_queue()
        request = models.JobRequest(
            kind="build", step="household", world="w1", district="clayton", confirm=True
        )
        error = self.assert_http_error(400, routers_jobs.jobs_create, request)
        self.assertEqual(str(error.detail), world_admin.LOCK_REQUIRED_REASON)

    def _import_jobs_with_temp_queue(self):
        import backend.paths as backend_paths

        temp_jobs = os.path.join(self._tmp.name, "jobs")
        with mock.patch.object(backend_paths, "JOBS_DIR", temp_jobs):
            jobs_module = importlib.import_module("backend.jobs")
        self.addCleanup(setattr, jobs_module, "JOBS_DIR", backend_paths.JOBS_DIR)
        jobs_module.JOBS_DIR = temp_jobs
        return importlib.import_module("backend.routers.jobs")


class ContractShapeTests(DistrictLifecycleBase):
    def test_district_info_schema_exposes_status_and_locked_at(self):
        schema = models.DistrictInfo.model_json_schema()
        self.assertIn("status", schema["properties"])
        self.assertIn("locked_at", schema["properties"])
        self.assertEqual(
            sorted(schema["properties"]["status"]["enum"]),
            ["initialized", "locked", "uninitialized"],
        )

    def test_every_district_mutation_route_responds_with_district_info(self):
        expected = {
            ("POST", "/worlds/{world}/districts"): models.DistrictCreateResult,
            ("PATCH", "/worlds/{world}/districts/{district}"): models.DistrictInfo,
            ("POST", "/worlds/{world}/districts/{district}/lock"): models.DistrictInfo,
            ("POST", "/worlds/{world}/districts/{district}/copy"): models.DistrictInfo,
        }
        found = {}
        for route in build_router.router.routes:
            for method in sorted(getattr(route, "methods", set())):
                key = (method, route.path)
                if key in expected:
                    found[key] = route.response_model
        self.assertEqual(found, expected)

    def test_create_route_reports_whether_it_created_the_district(self):
        first = build_router.world_districts_create(
            "w1", models.DistrictCreateRequest(name="dockside")
        )
        self.assertTrue(first.created)
        self.assertEqual(first.status, "uninitialized")

        second = build_router.world_districts_create(
            "w1", models.DistrictCreateRequest(name="dockside")
        )
        self.assertFalse(second.created)
        self.assertEqual(second.status, "uninitialized")

    def test_create_result_schema_exposes_created(self):
        schema = models.DistrictCreateResult.model_json_schema()
        self.assertIn("created", schema["properties"])
        self.assertIn("status", schema["properties"])

    def test_list_route_responds_with_district_info(self):
        list_routes = [
            route
            for route in build_router.router.routes
            if route.path == "/worlds/{world}/districts"
            and "GET" in getattr(route, "methods", set())
        ]
        self.assertEqual(len(list_routes), 1)
        self.assertEqual(
            getattr(list_routes[0].response_model, "__args__", (None,))[0],
            models.DistrictInfo,
        )

    def test_create_and_list_agree_with_the_service(self):
        info = self.create_district("dockside")
        self.assertEqual(info.status, "uninitialized")
        self.assertEqual(info.name, "dockside")
        listed = districts_service.list_districts("w1")
        self.assertEqual([item.name for item in listed], ["dockside"])
        self.assertEqual(listed[0].status, "uninitialized")


if __name__ == "__main__":
    unittest.main()
