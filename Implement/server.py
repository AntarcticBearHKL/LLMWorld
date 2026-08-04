















import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
WORLDS_DIR = os.path.join(PROJECT_ROOT, "worlds")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")


sys.path.insert(0, os.path.join(PROJECT_ROOT, "Implement"))
import background_runner as _br






def list_worlds():

    worlds = []
    if not os.path.isdir(WORLDS_DIR):
        return worlds
    for name in sorted(os.listdir(WORLDS_DIR)):
        wdir = os.path.join(WORLDS_DIR, name)
        if not os.path.isdir(wdir):
            continue
        world = {"id": name, "households": [], "scenarios": [], "days": []}

        meta_path = os.path.join(wdir, "world.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                world["households"] = meta.get("households", [])
                world["district"] = meta.get("district", {})
            except Exception:
                pass

        world.update(scan_world(name))
        worlds.append(world)


    real_ids = {w["id"] for w in worlds}
    if os.path.isdir(OUTPUTS_DIR):
        for name in sorted(os.listdir(OUTPUTS_DIR)):
            if name in real_ids:
                continue
            out_world_dir = os.path.join(OUTPUTS_DIR, name)
            if not os.path.isdir(out_world_dir):
                continue
            if not os.path.isdir(os.path.join(out_world_dir, "population")):
                continue
            world = {"id": name, "households": [], "scenarios": [], "days": [],
                     "virtual": True}
            world.update(scan_world(name))
            if world["scenarios"]:
                worlds.append(world)
    return worlds


def scan_world(world_id):

    result = {"scenarios": [], "days": []}
    out_dir = os.path.join(OUTPUTS_DIR, world_id, "population")
    if os.path.isdir(out_dir):
        for scenario in sorted(os.listdir(out_dir)):
            sdir = os.path.join(out_dir, scenario)
            if os.path.isdir(sdir):
                dates = sorted(d for d in os.listdir(sdir)
                               if os.path.isdir(os.path.join(sdir, d)))
                if dates:
                    result["scenarios"].append({
                        "name": scenario, "dates": dates,
                        "latest": dates[-1],
                    })
                result["days"].extend(f"{scenario}/{d}" for d in dates)
    return result


def load_profile(world_id, scenario, date):

    path = os.path.join(OUTPUTS_DIR, world_id, "population", scenario, date,
                        "population_profile_1440min.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_clusters(world_id, scenario, date):

    date_tag = _dir_date(date) if date else "latest"
    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"clusters_{scenario}_{date_tag}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_variability(world_id, scenario):

    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"variability_{scenario}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_behavior_patterns(world_id, scenario):

    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"patterns_{scenario}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_groups(world_id, source="awareness"):

    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"groups_{source}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_event_response(world_id, scenario="baseline"):

    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"event_response_{scenario}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_anomalies(world_id, scenario="baseline"):

    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"anomalies_{scenario}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_behavior_load(world_id, scenario, date):

    date_tag = date.replace("-", "") if date else "latest"
    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"behavior_load_{scenario}_{date_tag}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_solar(world_id, scenario, date):

    date_tag = date.replace("-", "") if date else "latest"
    path = os.path.join(OUTPUTS_DIR, world_id, "analysis",
                        f"solar_{scenario}_{date_tag}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_worlds_matrix():

    path = os.path.join(OUTPUTS_DIR, "comparison", "worlds_matrix.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_timeline(world_id):

    events = load_events(world_id)
    by_date = {}
    for item in events.get("events", []):
        date = item.get("date", "")
        if date:
            by_date.setdefault(date, []).append(item)
    timeline = []
    pop_dir = os.path.join(OUTPUTS_DIR, world_id, "population")
    if os.path.isdir(pop_dir):
        for scenario in sorted(os.listdir(pop_dir)):
            sdir = os.path.join(pop_dir, scenario)
            if not os.path.isdir(sdir):
                continue
            for date_dir in sorted(os.listdir(sdir)):
                path = os.path.join(sdir, date_dir,
                                    "population_profile_1440min.json")
                if not os.path.exists(path):
                    continue
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    continue
                timeline.append({
                    "date": date_dir,
                    "scenario": scenario,
                    "policy": data.get("day_policy") or data.get("policy", ""),
                    "kwh": data.get("total_energy_kwh"),
                    "events": by_date.get(date_dir, []),
                })
    timeline.sort(key=lambda t: (t["date"], t["scenario"]))
    return timeline


def load_matrix(world_id):

    path = os.path.join(OUTPUTS_DIR, world_id, "comparison", "policy_matrix.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_analysis(world_id, scenario="baseline"):

    path = os.path.join(OUTPUTS_DIR, world_id, "analysis", f"population_{scenario}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_households_profile(world_id):

    base = os.path.join(WORLDS_DIR, world_id, "3168")
    if not os.path.isdir(base):
        return []
    households = []
    for house_id in sorted(os.listdir(base)):
        hpath = os.path.join(base, house_id, "household.json")
        if not os.path.isfile(hpath):
            continue
        try:
            with open(hpath, "r", encoding="utf-8") as f:
                household = json.load(f)
            members = []
            for m in household.get("members", []):
                pers = m.get("personality", {})
                members.append({
                    "name": m.get("name"),
                    "age": m.get("age"),
                    "occupation": m.get("occupation"),
                    "traits": pers.get("traits", []),
                    "big_five": pers.get("big_five", {}),
                    "news_sensitivity": pers.get("news_sensitivity"),
                })
            households.append({
                "house_id": house_id,
                "type": household.get("type"),
                "members": members,
            })
        except Exception:
            continue
    return households


def load_world_state(world_id):

    path = os.path.join(WORLDS_DIR, world_id, "state.json")
    if not os.path.exists(path):
        return {"has_state": False}
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)
    return {
        "has_state": True,
        "date": state.get("date"),
        "memory_days": len(state.get("memory_days", [])),
    }


def delete_job(job_id):

    jobs = load_jobs()
    job = next((j for j in jobs if j["job_id"] == job_id), None)
    if not job:
        raise ValueError(f"任务 {job_id} 不存在")
    if job["status"] == "running":
        raise ValueError(f"任务 {job_id} 运行中，请先停止再删除")
    deleted = []
    for ext in (".json", ".out"):
        p = os.path.join(PROJECT_ROOT, "logs", "jobs", job_id + ext)
        if os.path.exists(p):
            os.remove(p)
            deleted.append(os.path.basename(p))
    return deleted


def load_jobs():

    jobs_dir = os.path.join(PROJECT_ROOT, "logs", "jobs")
    if not os.path.isdir(jobs_dir):
        return []
    jobs = []
    for name in sorted(os.listdir(jobs_dir)):
        if not name.endswith(".json") or name.startswith("server"):
            continue
        try:
            with open(os.path.join(jobs_dir, name), "r", encoding="utf-8") as f:
                meta = json.load(f)

            prog = _br.parse_progress(meta["out"])
            jobs.append({
                "job_id": meta["job_id"],
                "status": prog["status"],
                "progress": prog["detail"],
                "command": meta["command"],
                "started_at": meta["started_at"],
                "log_tail": _br.tail_text(meta["out"], 800),
            })
        except Exception:
            continue
    return jobs


def build_sim_args(world_id, body):
    from engine.policy import Policy
    policy = body.get("policy") or ""
    days = body.get("days") or 1
    date = body.get("date") or ""
    scenario = body.get("scenario") or ""
    sim_args = [world_id, "--days", str(days)]
    if date:
        from engine.world import validate_start_date
        validate_start_date(world_id, date)
        sim_args += ["--date", str(date)]
    if policy:
        Policy.from_name(policy)
        sim_args += ["--policy", str(policy)]
    if scenario:
        sim_args += ["--scenario", str(scenario)]
    if body.get("peer_nudge"):
        sim_args += ["--peer-nudge"]
    return sim_args


def validate_create_args(world_id, count):
    import re
    if not world_id or not str(world_id).strip():
        raise ValueError("世界 ID 不能为空")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", str(world_id).strip()):
        raise ValueError("世界 ID 只能含字母/数字/下划线/连字符")
    if os.path.isdir(os.path.join(WORLDS_DIR, world_id)):
        raise ValueError(f"世界 {world_id} 已存在")
    try:
        count = int(count)
    except (TypeError, ValueError):
        raise ValueError("家庭数必须是整数")
    if count < 1 or count > 10:
        raise ValueError("家庭数需在 1-10 之间（世界级约束 ≤10 户）")
    return world_id.strip(), count


def create_world(world_id, count, seed=42):
    world_id, count = validate_create_args(world_id, count)
    import population
    world_meta = population.build_population(world_id, count, int(seed))
    return world_meta


def load_templates():

    from engine.news_templates import template_names, build_template
    items = []
    for name in sorted(template_names()):
        try:
            sample = build_template(name, "2026-05-01")
        except Exception:
            continue
        items.append({
            "name": name,
            "title": getattr(sample, "title", ""),
            "content": getattr(sample, "content", ""),
        })
    return items


def load_events(world_id):

    path = os.path.join(WORLDS_DIR, world_id, "events.json")
    if not os.path.exists(path):
        return {"events": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_event_to_script(world_id, event):

    path = os.path.join(WORLDS_DIR, world_id, "events.json")
    data = load_events(world_id)
    item = {
        "date": event["date"], "time": event.get("time", "07:00"),
        "title": event["title"], "content": event["content"],
        "source": event.get("source", "上帝"), "type": event.get("type", "一般"),
    }
    data.setdefault("events", []).append(item)
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def _dir_date(date_str):

    return date_str.replace("-", "") if date_str else date_str


def load_house_profile(world_id, postcode, house_id, scenario, date):

    path = os.path.join(OUTPUTS_DIR, world_id, postcode, house_id, scenario,
                        _dir_date(date), "用电信息", "house_load_profile_1440min.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_house_summary(world_id, postcode, house_id, scenario, date):

    path = os.path.join(OUTPUTS_DIR, world_id, postcode, house_id, scenario,
                        _dir_date(date), "用电信息", "总用电汇总.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)






class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _send_file(self, path):
        if not os.path.exists(path):
            self._send_json({"error": "not found"}, 404)
            return
        with open(path, "rb") as f:
            body = f.read()
        ext = os.path.splitext(path)[1]
        ctype = {"html": "text/html; charset=utf-8", "js": "text/javascript",
                 "css": "text/css"}.get(ext.lstrip("."), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        parts = [p for p in path.split("/") if p]

        try:

            if not parts or parts[0] == "index.html":
                self._send_file(os.path.join(FRONTEND_DIR, "index.html"))
                return
            if parts[0].startswith("static"):
                self._send_file(os.path.join(FRONTEND_DIR, *parts[1:]))
                return


            if parts == ["api", "worlds"]:
                self._send_json(list_worlds())
                return
            if len(parts) >= 3 and parts[:2] == ["api", "worlds"]:
                world_id = parts[2]
                if len(parts) == 3:
                    world = next((w for w in list_worlds() if w["id"] == world_id), None)
                    self._send_json(world or {"error": "world not found"}, 200 if world else 404)
                    return
                if parts[3] == "profile" and len(parts) >= 5:
                    data = load_profile(world_id, parts[4], parts[5] if len(parts) > 5 else None)
                    self._send_json(data or {"error": "profile not found"}, 200 if data else 404)
                    return
                if parts[3] == "matrix":
                    data = load_matrix(world_id)
                    self._send_json(data or {"error": "no matrix"}, 200 if data else 404)
                    return
                if parts[3] == "analysis" and len(parts) >= 5:
                    data = load_analysis(world_id, parts[4])
                    self._send_json(data or {"error": "no analysis"}, 200 if data else 404)
                    return
                if parts[3] == "clusters" and len(parts) >= 5:
                    data = load_clusters(world_id, parts[4], parts[5] if len(parts) > 5 else None)
                    self._send_json(data or {"error": "no clusters"}, 200 if data else 404)
                    return
                if parts[3] == "variability" and len(parts) >= 5:
                    data = load_variability(world_id, parts[4])
                    self._send_json(data or {"error": "no variability"}, 200 if data else 404)
                    return
                if parts[3] == "patterns" and len(parts) >= 5:
                    data = load_behavior_patterns(world_id, parts[4])
                    self._send_json(data or {"error": "no patterns"}, 200 if data else 404)
                    return
                if parts[3] == "groups" and len(parts) >= 4:
                    source = parts[4] if len(parts) > 4 else "awareness"
                    data = load_groups(world_id, source)
                    self._send_json(data or {"error": "no groups"}, 200 if data else 404)
                    return
                if parts[3] == "event-response" and len(parts) >= 5:
                    data = load_event_response(world_id, parts[4])
                    self._send_json(data or {"error": "no event response"}, 200 if data else 404)
                    return
                if parts[3] == "anomalies" and len(parts) >= 5:
                    data = load_anomalies(world_id, parts[4])
                    self._send_json(data or {"error": "no anomalies"}, 200 if data else 404)
                    return
                if parts[3] == "behavior-load" and len(parts) >= 6:
                    data = load_behavior_load(world_id, parts[4], parts[5])
                    self._send_json(data or {"error": "no behavior load"}, 200 if data else 404)
                    return
                if parts[3] == "solar" and len(parts) >= 6:
                    data = load_solar(world_id, parts[4], parts[5])
                    self._send_json(data or {"error": "no solar"}, 200 if data else 404)
                    return
                if parts[3] == "events":
                    self._send_json(load_events(world_id))
                    return
                if parts[3] == "state":
                    self._send_json(load_world_state(world_id))
                    return
                if parts[3] == "households":
                    self._send_json(load_households_profile(world_id))
                    return
                if parts[3] == "house" and len(parts) >= 6:

                    house_id, sub, scenario, date = parts[4], parts[5], parts[6], parts[7]
                    postcode = None
                    world = next((w for w in list_worlds() if w["id"] == world_id), None)
                    district = (world or {}).get("district") or {}
                    postcode = district.get("postcode")
                    if not postcode:
                        self._send_json({"error": "unknown postcode"}, 404)
                        return
                    if sub == "summary":
                        data = load_house_summary(world_id, postcode, house_id, scenario, date)
                    else:
                        data = load_house_profile(world_id, postcode, house_id, scenario, date)
                    self._send_json(data or {"error": "house data not found"}, 200 if data else 404)
                    return
            if parts == ["api", "compare"]:
                self._send_json({"worlds": [w["id"] for w in list_worlds()]})
                return
            if parts == ["api", "worlds-matrix"]:
                data = load_worlds_matrix()
                self._send_json(data or {"error": "no worlds matrix"}, 200 if data else 404)
                return
            if len(parts) == 4 and parts[:3] == ["api", "worlds"] and parts[3] == "timeline":
                data = load_timeline(parts[2])
                self._send_json({"timeline": data})
                return
            if parts == ["api", "news-templates"]:
                self._send_json({"templates": load_templates()})
                return
            if parts == ["api", "jobs"]:
                self._send_json(load_jobs())
                return

            self._send_json({"error": f"unknown api: {path}"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        parts = [p for p in path.split("/") if p]
        try:
            if len(parts) == 4 and parts[:2] == ["api", "worlds"] and parts[3] == "events":
                world_id = parts[2]
                body = self._read_json_body()
                missing = [k for k in ("date", "title", "content") if not body.get(k)]
                if missing:
                    self._send_json({"error": f"缺少字段: {missing}"}, 400)
                    return
                events = add_event_to_script(world_id, body)
                self._send_json(events)
                return
            if len(parts) == 4 and parts[:2] == ["api", "worlds"] and parts[3] == "analyze":
                world_id = parts[2]
                import io
                from contextlib import redirect_stdout
                import make_analysis_all
                buf = io.StringIO()
                try:
                    with redirect_stdout(buf):
                        make_analysis_all.run_all(world_id)
                    self._send_json({"ok": True, "output": buf.getvalue()})
                except Exception as e:
                    self._send_json({"error": str(e)}, 500)
                return
            if len(parts) == 4 and parts[:2] == ["api", "worlds"] and parts[3] == "simulate":
                world_id = parts[2]
                body = self._read_json_body()
                try:
                    sim_args = build_sim_args(world_id, body)
                    job_id = _br.cmd_start(
                        argparse.Namespace(sim_args=sim_args))
                    self._send_json({"ok": True, "job_id": job_id,
                                     "command": " ".join(sim_args)})
                except ValueError as e:
                    self._send_json({"error": str(e)}, 400)
                except Exception as e:
                    self._send_json({"error": str(e)}, 500)
                return
            if parts == ["api", "worlds", "create"]:
                body = self._read_json_body()
                try:
                    world_id = str(body.get("world_id", "")).strip()
                    meta = create_world(world_id, body.get("count", 3),
                                        body.get("seed", 42))
                    self._send_json({"ok": True,
                                     "world_id": world_id,
                                     "households": len(meta.get("households", []))})
                except ValueError as e:
                    self._send_json({"error": str(e)}, 400)
                except Exception as e:
                    self._send_json({"error": str(e)}, 500)
                return
            if len(parts) == 4 and parts[:3] == ["api", "jobs", "delete"]:
                job_id = parts[3]
                deleted = delete_job(job_id)
                self._send_json({"deleted": deleted})
                return
            if len(parts) == 4 and parts[:3] == ["api", "jobs", "stop"]:
                job_id = parts[3]
                try:
                    _br.cmd_stop(argparse.Namespace(job_id=job_id))
                    self._send_json({"stopped": job_id})
                except SystemExit:
                    self._send_json({"error": f"任务 {job_id} 不存在"}, 404)
                return
            self._send_json({"error": f"unknown api: {path}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def log_message(self, format, *args):
        pass


def serve(port=8080):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"模拟世界可视化服务已启动：http://localhost:{port}")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()






def query_cli(args):
    if args.query == "worlds":
        for w in list_worlds():
            hh = len(w["households"])
            sc = ", ".join(s["name"] for s in w["scenarios"]) or "-"
            print(f"{w['id']}：{hh} 户 | 场景: {sc}")
        return

    if args.query == "days":
        for w in list_worlds():
            if w["id"] == args.world:
                for s in w["scenarios"]:
                    for d in s["dates"]:
                        print(f"{s['name']}/{d}")
                return
        print(f"世界 {args.world} 未找到")
        return

    if args.query == "profile":
        data = load_profile(args.world, args.scenario, args.date)
        if not data:
            print("未找到聚合曲线（检查场景/日期）")
            return
        print(f"[{args.world}/{args.scenario}/{args.date}]")
        print(f"  总用电 {data['total_energy_kwh']} kWh | 户均 {data['mean_household_kwh']} | "
              f"峰值 {data['peak_watts']} W @ {data['peak_time']}")
        for h in data["per_house"]:
            print(f"  {h['house_id']}: {h['total_energy_kwh']} kWh @ {h['peak_time']}")
        return

    if args.query == "matrix":
        m = load_matrix(args.world)
        if not m:
            print("无对比矩阵（先跑 compare_policies --all）")
            return
        for s in m["scenarios"]:
            print(" | ".join(str(s.get(k, "")) for k in s.keys()))
        return

    if args.query == "events":
        e = load_events(args.world)
        for item in e.get("events", []):
            print(f"[{item['date']} {item['time']}]（{item.get('source','')}）{item['title']}")
            print(f"  {item['content']}")
        return

    print(f"未知查询: {args.query}")


def parse_args():
    parser = argparse.ArgumentParser(description="模拟世界可视化后端")
    parser.add_argument("--port", type=int, default=8080, help="HTTP 端口")
    parser.add_argument("--query", default=None, help="命令行查询: worlds/days/profile/matrix/events")
    parser.add_argument("--world", default=None, help="查询用的世界ID")
    parser.add_argument("--scenario", default="baseline", help="查询用的场景")
    parser.add_argument("--date", default=None, help="查询用的日期(YYYY-MM-DD)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.query:
        query_cli(args)
    else:
        serve(args.port)
