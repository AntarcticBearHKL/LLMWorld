







import os
import sys
import json
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPLEMENT_DIR = os.path.join(PROJECT_ROOT, "Implement")
sys.path.insert(0, IMPLEMENT_DIR)

from engine import utils, Home, Room, Member
from engine.energy_calculator import EnergyCalculator
from engine.timeline import Timeline
from engine.subagent import SubAgent
from engine.memory import HouseholdMemory
from engine.prompt import Prompt
from population import _build_template
from population_runner import aggregate_population
from validate_baseline import hourly_normalized, compare_curves, pearson
from make_report import price_elasticity, tou_elasticity, parse_kwh


class FakeEnergyCalculator:
    def __init__(self, loads):
        self.household_load_watts = loads


class TestBaseline(unittest.TestCase):


    def test_hourly_normalized(self):
        loads = [50.0] * 1440
        loads[19 * 60:20 * 60] = [2050.0] * 60
        curve = hourly_normalized(loads)
        self.assertEqual(len(curve), 24)
        mean = sum(curve) / 24
        self.assertAlmostEqual(mean, 1.0)
        self.assertEqual(curve.index(max(curve)), 19)

    def test_pearson_identical_is_one(self):
        a = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(pearson(a, a), 1.0)

    def test_compare_curves_same_shape(self):
        sim = [0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 1.3, 1.0, 0.7, 0.6, 0.5, 0.5] * 2
        real = [0.55, 0.65, 0.85, 1.05, 1.25, 1.45, 1.35, 1.05, 0.75, 0.65, 0.55, 0.5] * 2
        report = compare_curves(sim, real)
        self.assertEqual(report["sim_peak_hour"], 5)
        self.assertEqual(report["real_peak_hour"], 5)
        self.assertEqual(report["peak_hour_offset"], 0)
        self.assertGreater(report["correlation"], 0.9)


class TestGroupAnalysis(unittest.TestCase):


    def test_group_stats(self):
        from analyze_groups import group_stats
        labels = {"h1": "高", "h2": "高", "h3": "低"}
        scenarios = {
            "baseline": {"h1": 10.0, "h2": 14.0, "h3": 8.0},
            "tou": {"h1": 8.0, "h2": 12.0, "h3": 8.2},
            "nudge": {"h1": 9.0, "h2": 13.0, "h3": 7.9},
        }
        rows = {r["group"]: r for r in group_stats(labels, scenarios)}

        self.assertEqual(rows["高"]["households"], 2)
        self.assertAlmostEqual(rows["高"]["baseline_mean_kwh"], 12.0)

        self.assertAlmostEqual(rows["高"]["tou_mean_kwh"], 10.0)
        self.assertAlmostEqual(rows["高"]["tou_change_pct"], -16.67, places=2)

        self.assertAlmostEqual(rows["低"]["tou_change_pct"], 2.5, places=2)


class TestNewsBoard(unittest.TestCase):


    def test_filter_by_date(self):
        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-21", "07:00", "征税", "内容A"))
        board.add_event(NewsItem("2026-04-22", "07:00", "返利", "内容B"))

        self.assertEqual(len(board.available_on("2026-04-20")), 0)
        self.assertEqual(len(board.available_on("2026-04-21")), 1)
        self.assertEqual(len(board.available_on("2026-04-23")), 2)

    def test_render_empty_when_no_news(self):
        from engine.news import NewsBoard
        self.assertEqual(NewsBoard().render_for_prompt("2026-04-21"), "")

    def test_render_contains_news_and_personality_instruction(self):
        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-21", "07:00", "战争爆发", "能源紧张", source="新闻媒体"))
        text = board.render_for_prompt("2026-04-21")
        self.assertIn("今日外界信息", text)
        self.assertIn("战争爆发", text)
        self.assertIn("性格", text)

    def test_inline_event_parsing(self):
        from engine.news import NewsBoard
        board = NewsBoard()
        board.add_inline_event("2026-04-21|新税|内容|政府公告")
        self.assertEqual(len(board.items), 1)
        self.assertEqual(board.items[0].title, "新税")
        self.assertEqual(board.items[0].source, "政府公告")

    def test_inline_event_bad_format_raises(self):
        from engine.news import NewsBoard
        with self.assertRaises(ValueError):
            NewsBoard().add_inline_event("只有两个字段")


class TestServerData(unittest.TestCase):
    _OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

    @unittest.skipUnless(os.path.isdir(os.path.join(_OUT, "pop04")), "需要 pop04 模拟数据")
    def test_list_worlds_contains_pop04(self):
        import server
        worlds = server.list_worlds()
        ids = [w["id"] for w in worlds]
        self.assertIn("pop04", ids)

    @unittest.skipUnless(os.path.isdir(os.path.join(_OUT, "pop04")), "需要 pop04 模拟数据")
    def test_load_profile_known_scenario(self):
        import server
        data = server.load_profile("pop04", "baseline", "2026-04-21")
        self.assertIsNotNone(data)
        self.assertEqual(len(data["load_profile_watts"]), 1440)

    @unittest.skipUnless(os.path.isdir(os.path.join(_OUT, "pop04")), "需要 pop04 模拟数据")
    def test_load_events_pop04(self):
        import server
        events = server.load_events("pop04")
        self.assertGreaterEqual(len(events.get("events", [])), 1)


class TestEnvironmentInterface(unittest.TestCase):


    def setUp(self):
        import config as cfg
        self._saved_mode = cfg.ENV_MODE
        self._saved_file = cfg.ENV_MANUAL_FILE

    def tearDown(self):
        import config as cfg
        cfg.ENV_MODE = self._saved_mode
        cfg.ENV_MANUAL_FILE = self._saved_file

    def test_config_mode_temp_within_season_range(self):

        import config as cfg
        cfg.ENV_MODE = "config"
        from engine.environment_interface import EnvironmentInterface
        lo, hi = cfg.MELBOURNE_CLIMATE["冬天"]["temp_range"]
        for _ in range(30):
            w = EnvironmentInterface.get_weather({"coordinates": {}}, "", "冬天")
            avg = w["temperature"]["avg"]
            self.assertGreaterEqual(avg, lo)
            self.assertLessEqual(avg, hi)
            self.assertIn("mode", w)

    def test_config_mode_seeded_reproducible(self):

        import config as cfg
        cfg.ENV_MODE = "config"
        from engine.environment_interface import EnvironmentInterface
        import random
        random.seed(7)
        w1 = EnvironmentInterface.get_weather({}, "", "春天")
        random.seed(7)
        w2 = EnvironmentInterface.get_weather({}, "", "春天")
        self.assertEqual(w1["temperature"]["avg"], w2["temperature"]["avg"])
        self.assertEqual(w1["condition"], w2["condition"])

    def test_manual_mode_fixed_value(self):

        import config as cfg
        cfg.ENV_MODE = "manual"
        from engine.environment_interface import EnvironmentInterface
        w = EnvironmentInterface.get_weather({}, "2026-04-21", "春天")
        self.assertEqual(w["mode"], "manual")
        self.assertIn("condition", w)

    def test_manual_missing_file_raises(self):

        import config as cfg
        cfg.ENV_MODE = "manual"
        cfg.ENV_MANUAL_FILE = "不存在的文件.json"
        from engine.environment_interface import EnvironmentInterface
        with self.assertRaises(FileNotFoundError):
            EnvironmentInterface.get_weather({}, "2026-04-21", "春天")


class TestPopulationAnalysis(unittest.TestCase):


    def test_group_mean(self):
        from analyze_population import group_mean
        result = group_mean([("高", 10), ("高", 20), ("低", 4)])
        self.assertEqual(result["高"], 15.0)
        self.assertEqual(result["低"], 4.0)

    def test_household_features(self):
        from analyze_population import household_features
        h = {"type": "有孩家庭", "members": [
            {"age": 35, "personality": {"energy_awareness": "高",
                                         "big_five": {"conscientiousness": 8}}},
            {"age": 33, "personality": {}},
        ]}
        f = household_features(h)
        self.assertEqual(f["members_count"], 2)
        self.assertEqual(f["energy_awareness"], "高")
        self.assertEqual(f["big_five"]["conscientiousness"], 8)

    def test_pearson_sign(self):
        from analyze_population import pearson
        self.assertGreater(pearson([1, 2, 3], [2, 4, 6]), 0.99)
        self.assertLess(pearson([1, 2, 3], [6, 4, 2]), -0.99)
        self.assertIsNone(pearson([1], [2]))


class TestCombineWorlds(unittest.TestCase):
    _OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

    @unittest.skipUnless(os.path.isdir(os.path.join(_OUT, "pop04", "population", "baseline")),
                         "需要 pop04 模拟数据")
    def test_combine_math(self):

        from combine_worlds import combine


        data = combine(["pop04"], "baseline", "2026-04-21")
        self.assertEqual(data["households"], 10)
        self.assertEqual(len(data["load_profile_watts"]), 1440)
        single = combine(["pop04"], "baseline", "2026-04-21")
        self.assertAlmostEqual(data["total_energy_kwh"], single["total_energy_kwh"], places=2)


class TestNewsMemoryProgressive(unittest.TestCase):


    def test_delivery_first_day_only_new(self):

        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-21", "07:00", "新闻A", "内容A"))
        board.add_event(NewsItem("2026-04-22", "07:00", "新闻B", "内容B"))

        day1 = board.get_new_for("2026-04-21")
        self.assertEqual(len(day1), 1)
        self.assertEqual(day1[0].title, "新闻A")

        self.assertEqual(len(board.get_new_for("2026-04-21")), 0)

    def test_delivery_day2_only_new(self):

        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-21", "07:00", "新闻A", "内容A"))
        board.add_event(NewsItem("2026-04-22", "07:00", "新闻B", "内容B"))
        board.get_new_for("2026-04-21")

        day2 = board.get_new_for("2026-04-22")
        self.assertEqual(len(day2), 1)
        self.assertEqual(day2[0].title, "新闻B")

    def test_backfilled_old_news_considered_new(self):

        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-22", "07:00", "新闻B", "内容B"))
        board.get_new_for("2026-04-22")

        board.add_event(NewsItem("2026-04-21", "09:00", "后补旧闻", "内容"))
        day2b = board.get_new_for("2026-04-22")
        self.assertEqual(len(day2b), 1)
        self.assertEqual(day2b[0].title, "后补旧闻")

    def test_delivery_state_roundtrip(self):

        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-21", "07:00", "新闻A", "内容A"))
        board.add_event(NewsItem("2026-04-22", "07:00", "新闻B", "内容B"))
        board.get_new_for("2026-04-21")
        state = board.to_state()

        board2 = NewsBoard(delivered_ids=state["delivered_ids"])
        board2.add_event(NewsItem("2026-04-21", "07:00", "新闻A", "内容A"))
        board2.add_event(NewsItem("2026-04-22", "07:00", "新闻B", "内容B"))
        day2 = board2.get_new_for("2026-04-22")
        self.assertEqual([n.title for n in day2], ["新闻B"])

    def test_memory_news_rolling_keep(self):

        from engine.news import NewsItem
        from engine.memory import HouseholdMemory
        mem = HouseholdMemory()
        for i in range(8):
            mem.add_news([NewsItem(f"2026-04-{20+i}", "07:00", f"新闻{i}", "x")], keep=5)
        self.assertEqual(len(mem.news_memory), 5)
        self.assertEqual(mem.news_memory[-1]["title"], "新闻7")
        self.assertEqual(mem.news_memory[0]["title"], "新闻3")

    def test_prompt_context_contains_news_review(self):

        from engine.news import NewsItem
        from engine.memory import HouseholdMemory
        mem = HouseholdMemory()
        mem.add_news([NewsItem("2026-04-21", "07:00", "昨日新闻标题", "x")], keep=5)
        ctx = mem.get_prompt_context()
        self.assertIn("近期外界信息回顾", ctx)
        self.assertIn("昨日新闻标题", ctx)

    @unittest.skipUnless(os.path.isdir(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "worlds", "pop05")),
        "需要 pop05 世界")
    def test_world_state_news_roundtrip(self):

        import json, os, tempfile
        from engine.world import World
        from simulate import load_world, create_home_from_household
        from engine.news import NewsItem

        wmeta, d, hs = load_world("pop05")
        home = create_home_from_household(hs[0]["household"])
        w = World(home, world_id="pop05", postcode="3168", house_id="house_0001",
                  start_date="2026年4月21日")
        w.news.add_event(NewsItem("2026-04-21", "07:00", "新闻A", "内容A"))
        w.news.get_new_for("2026-04-21")
        w.memory.add_news(w.news.delivered_on("2026-04-21"), keep=5)
        w.save_state()


        w2 = World(home, world_id="pop05", postcode="3168", house_id="house_0001")

        w2.news.add_event(NewsItem("2026-04-21", "07:00", "新闻A", "内容A"))

        self.assertEqual(len(w2.news.get_new_for("2026-04-21")), 0)
        self.assertEqual(len(w2.memory.news_memory), 1)
        self.assertEqual(w2.memory.news_memory[0]["title"], "新闻A")


        sp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "worlds", "pop05", "state.json")
        if os.path.exists(sp):
            os.remove(sp)


class TestPolicySchedule(unittest.TestCase):

    def test_date_in_range(self):
        from population_runner import _policy_for_date
        sched = [("2026-04-25", "2026-04-28", "tou")]
        self.assertEqual(_policy_for_date(sched, "2026-04-25"), "tou")
        self.assertEqual(_policy_for_date(sched, "2026-04-28"), "tou")
        self.assertIsNone(_policy_for_date(sched, "2026-04-24"))
        self.assertIsNone(_policy_for_date(sched, "2026-04-29"))

    def test_open_end(self):
        from population_runner import _policy_for_date
        sched = [("2026-04-25", "", "nudge_loss")]
        self.assertEqual(_policy_for_date(sched, "2026-04-25"), "nudge_loss")
        self.assertEqual(_policy_for_date(sched, "2026-12-31"), "nudge_loss")
        self.assertIsNone(_policy_for_date(sched, "2026-04-24"))

    def test_multiple_segments_first_match(self):
        from population_runner import _policy_for_date
        sched = [("2026-04-20", "2026-04-22", "tou"),
                 ("2026-04-23", "2026-04-25", "subsidy")]
        self.assertEqual(_policy_for_date(sched, "2026-04-21"), "tou")
        self.assertEqual(_policy_for_date(sched, "2026-04-24"), "subsidy")
        self.assertIsNone(_policy_for_date(sched, "2026-04-26"))


class TestSeasonAuto(unittest.TestCase):

    def test_southern_hemisphere_seasons(self):
        from engine import utils
        self.assertEqual(utils.season_for_date("2026-01-15"), "夏天")
        self.assertEqual(utils.season_for_date("2026-04-21"), "秋天")
        self.assertEqual(utils.season_for_date("2026-07-01"), "冬天")
        self.assertEqual(utils.season_for_date("2026-10-01"), "春天")
        self.assertEqual(utils.season_for_date("2026-12-25"), "夏天")


class TestNewsTemplates(unittest.TestCase):

    def test_build_heatwave(self):
        from engine.news_templates import build_template
        item = build_template("heatwave", "2026-01-15")
        self.assertEqual(item.date, "2026-01-15")
        self.assertIn("高温", item.title)
        self.assertEqual(item.news_type, "环境")

    def test_build_unknown_raises(self):
        from engine.news_templates import build_template
        with self.assertRaises(ValueError):
            build_template("不存在的模板", "2026-01-15")

    def test_all_templates_valid(self):
        from engine.news_templates import TEMPLATES
        self.assertGreaterEqual(len(TEMPLATES), 8)
        for name, t in TEMPLATES.items():
            self.assertTrue(t["title"])
            self.assertTrue(t["content"])
            self.assertTrue(t["source"])


class TestPolicy(unittest.TestCase):


    def test_render_empty_when_no_policy(self):
        from engine.policy import Policy
        self.assertEqual(Policy("none").render(), "")

    def test_tou_render(self):
        from engine.policy import Policy
        text = Policy.tou().render()
        self.assertIn("分时电价", text)
        self.assertIn("0.55", text)
        self.assertIn("谷时段 22:00-07:00", text)

    def test_subsidy_and_nudge_render(self):
        from engine.policy import Policy
        self.assertIn("低谷充电补贴", Policy.subsidy().render())
        self.assertIn("社会规范", Policy.nudge().render())
        loss_text = Policy.nudge_loss().render()
        self.assertIn("损失", loss_text)
        self.assertIn("返利", loss_text)

    def test_compare_metrics(self):

        from compare_policies import compare
        from population_runner import aggregate_population

        def make_profile(peak_watts, valley_extra):
            loads = [50.0] * 1440
            for h in range(17, 20):
                loads[h * 60:(h + 1) * 60] = [peak_watts] * 60
            for h in range(23, 24):
                loads[h * 60:(h + 1) * 60] = [valley_extra] * 60
            return loads

        baseline = aggregate_population([("h1", {
            "energy_calculator": FakeEnergyCalculator(make_profile(2000, 0)),
            "energy_summary": {"total_energy_kwh": 12.0}})])

        intervention = aggregate_population([("h1", {
            "energy_calculator": FakeEnergyCalculator(make_profile(1500, 500)),
            "energy_summary": {"total_energy_kwh": 12.0}})])

        report = compare(baseline, intervention)
        self.assertLess(report["peak_hours_change_pct"], 0)
        self.assertGreater(report["valley_hours_change_pct"], 0)
        self.assertAlmostEqual(report["total_change_pct"], 0.0, places=1)


class TestPopulationV2(unittest.TestCase):


    def test_big_five_to_news_sensitivity(self):

        from population import big_five_to_news_sensitivity
        self.assertEqual(big_five_to_news_sensitivity(
            {"openness": 3, "conscientiousness": 5, "extraversion": 5,
             "agreeableness": 6, "neuroticism": 8}), "高")

    def test_no_energy_awareness_in_generation(self):

        import random
        from population import _build_template
        h = _build_template("young_couple", random.Random(9))
        blob = json.dumps(h, ensure_ascii=False)
        self.assertNotIn("energy_awareness", blob)
        self.assertNotIn("电动汽车", blob)
        self.assertNotIn("省电", blob)
        self.assertNotIn("关灯", blob)
        self.assertNotIn("节能", blob)

    def test_big_five_to_text_describes_high(self):
        from population import big_five_to_text
        text = big_five_to_text({"openness": 9, "conscientiousness": 5,
                                 "extraversion": 5, "agreeableness": 5,
                                 "neuroticism": 5})
        self.assertIn("开放性高", text)
        self.assertIn("新鲜事物", text)

    def test_quota_distribution_covers_all_types(self):

        import random
        from population import _quota_distribution
        counts = _quota_distribution(100, random.Random(1))
        self.assertEqual(sum(counts.values()), 100)
        self.assertEqual(len(counts), 8)

    def test_couple_age_association(self):

        import random
        from population import _build_template
        h = _build_template("young_couple", random.Random(7))
        ages = sorted(m["age"] for m in h["members"])
        self.assertLessEqual(ages[1] - ages[0], 5)

    def test_multigenerational_age_order(self):

        import random
        from population import _build_template
        h = _build_template("multigenerational", random.Random(3))
        ages = sorted(m["age"] for m in h["members"])

        self.assertLessEqual(ages[3] - ages[2], 5)
        self.assertGreaterEqual(ages[2] - ages[1], 20)
        self.assertGreaterEqual(ages[1] - ages[0], 18)

    def test_big_five_field_in_household(self):

        import random
        from population import _build_template
        h = _build_template("single_living", random.Random(5))
        pers = h["members"][0]["personality"]
        self.assertIn("big_five", pers)
        self.assertEqual(len(pers["big_five"]), 5)
        self.assertIn("behavior_text", pers)
        self.assertIn("news_sensitivity", pers)

    def test_dedupe_names(self):

        import random
        from population import _build_template, _dedupe_names
        h = _build_template("multigenerational", random.Random(3))
        _dedupe_names(h)
        names = [m["name"] for m in h["members"]]
        self.assertEqual(len(names), len(set(names)))


class TestPopulation(unittest.TestCase):


    def test_builder_deterministic(self):

        import random
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        h1 = _build_template("young_couple", rng1)
        h2 = _build_template("young_couple", rng2)
        self.assertEqual(json.dumps(h1, ensure_ascii=False), json.dumps(h2, ensure_ascii=False))

    def test_builder_heterogeneous(self):

        import random
        a = _build_template("young_couple", random.Random(1))
        b = _build_template("family_with_kids", random.Random(2))
        self.assertNotEqual(a["type"], b["type"])
        self.assertEqual(len(b["members"]), 3)

    def test_aggregation_math(self):

        house_results = []
        for i, watts in enumerate([(100.0, 500.0), (150.0, 700.0)]):
            loads = [watts[0]] * 1440
            loads[1200] = watts[1]

            day_result = {
                "energy_calculator": FakeEnergyCalculator(loads),
                "energy_summary": {"total_energy_kwh": watts[1] * 0.06},
            }
            house_results.append((f"house_{i}", day_result))

        pop = aggregate_population(house_results)

        self.assertEqual(pop["households"], 2)
        self.assertAlmostEqual(pop["load_profile_watts"][0], 250.0)
        self.assertAlmostEqual(pop["load_profile_watts"][1200], 1200.0)
        self.assertEqual(pop["peak_time"], "20:00")
        self.assertAlmostEqual(pop["mean_household_kwh"], (500.0 * 0.06 + 700.0 * 0.06) / 2, places=4)
        self.assertGreater(pop["std_household_kwh"], 0)


class TestMemory(unittest.TestCase):


    def _make_day_result(self):
        tl = Timeline("Alice")
        tl.load_from_activities([
            {"time": "00:00-07:30", "location": "主卧", "activity": "睡觉"},
            {"time": "07:30-08:30", "location": "厨房", "activity": "吃早餐"},
            {"time": "09:00-17:30", "location": "外出", "activity": "工作"},
            {"time": "18:00-20:00", "location": "客厅", "activity": "看电视"},
            {"time": "22:30-23:59", "location": "主卧", "activity": "睡觉"},
        ])

        class FakePlanner:
            timelines = {"Alice": tl}

        loads = [50.0] * 1440
        loads[1200] += 2000.0

        return {
            "date": "2026年4月20日",
            "planner": FakePlanner(),
            "energy_summary": {
                "total_energy_kwh": 5.6,
                "baseline_kwh": 1.2,
                "decision_kwh": 4.4,
                "appliances": [
                    {"name": "空调", "total_energy_kwh": 2.0},
                    {"name": "电磁炉", "total_energy_kwh": 1.5},
                    {"name": "电视", "total_energy_kwh": 0.3},
                ],
            },
            "energy_calculator": FakeEnergyCalculator(loads),
        }

    def test_empty_when_no_memory(self):
        self.assertEqual(HouseholdMemory().get_prompt_context(), "")

    def test_summary_extracts_rhythm_and_electricity(self):
        mem = HouseholdMemory()
        mem.update_from_day(self._make_day_result())

        summary = mem.last
        alice = summary["members"]["Alice"]
        self.assertEqual(alice["wake_time"], "07:30")
        self.assertEqual(alice["sleep_time"], "23:59")
        self.assertIn("吃早餐", alice["activities"][0])
        self.assertGreaterEqual(len(alice["activities"]), 3)

        self.assertAlmostEqual(summary["electricity"]["total_kwh"], 5.6)
        self.assertEqual(summary["electricity"]["peak_time"], "20:00")
        self.assertEqual(summary["electricity"]["peak_watts"], 2050)

    def test_prompt_context_contains_memory(self):
        mem = HouseholdMemory()
        mem.update_from_day(self._make_day_result())
        ctx = mem.get_prompt_context()

        self.assertIn("昨日记忆", ctx)
        self.assertIn("起床 07:30", ctx)
        self.assertIn("入睡 23:59", ctx)
        self.assertIn("高峰 20:00（2050 W）", ctx)
        self.assertIn("空调 2.0 kWh", ctx)

    def test_prompt_template_renders_with_empty_memory(self):

        from engine.prompt import Prompt
        rendered = Prompt().load("simulate_step1_macro_plan",
            member_name="Alice", member_age=28, member_occupation="软件工程师",
            member_personality="细心", date="2026年4月21日", day_type="工作日",
            time_context="日期：2026年4月21日（工作日）",
            home_structure="{}", members_info="[]", memory_context="")
        self.assertNotIn("memory_context", rendered)




def build_test_home():
    home = Home("测试之家")

    kitchen = Room("厨房")
    kitchen.add_appliance_by_name("冰箱")
    home.add_room(kitchen)

    living = Room("客厅")
    living.add_appliance_by_name("电视")
    home.add_room(living)

    alice = Member("Alice", 28, "软件工程师", "细心", {"wake_time": "07:00"})
    alice.add_personal_appliance_by_name("手机")
    home.add_member(alice)

    return home


class TestTimeParsing(unittest.TestCase):
    def test_parse_time_normal(self):
        self.assertEqual(utils.parse_time("07:30"), 450)

    def test_parse_time_bad_returns_zero(self):
        self.assertEqual(utils.parse_time("abc"), 0)

    def test_parse_time_range_normal(self):
        self.assertEqual(utils.parse_time_range("08:00-09:00"), (480, 540))

    def test_parse_time_range_cross_midnight(self):
        self.assertEqual(utils.parse_time_range("22:00-02:00"), (1320, 1560))

    def test_parse_time_range_bad_returns_fallback(self):

        self.assertEqual(utils.parse_time_range("not-a-range"), (0, 1440))

    def test_parse_time_range_multi_dash_repair(self):

        self.assertEqual(utils.parse_time_range("18:00-19:00-20:00"), (1080, 1200))


class TestTimeline(unittest.TestCase):
    def test_load_and_sort(self):
        tl = Timeline("Alice")
        tl.load_from_activities([
            {"time": "19:00-22:00", "location": "客厅", "activity": "看电视"},
            {"time": "08:00-09:00", "location": "厨房", "activity": "吃早餐"},
        ])
        self.assertEqual(len(tl.slots), 2)
        self.assertEqual(tl.slots[0].activity, "吃早餐")
        self.assertTrue(tl.slots[0].overlaps(480, 500))

    def test_load_bad_activity_skipped(self):
        tl = Timeline("Alice")
        tl.load_from_activities([
            {"time": "08:00-09:00", "location": "厨房", "activity": "吃早餐"},
            {"bad": "data"},
        ])
        self.assertEqual(len(tl.slots), 1)


class TestEnergyCalculator(unittest.TestCase):
    def setUp(self):
        self.home = build_test_home()
        self.tmpdir = tempfile.mkdtemp()

    def _write_decision(self, decision_data):
        path = os.path.join(self.tmpdir, f"04_第四层_批量用电决策_{decision_data['member']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(decision_data, f, ensure_ascii=False, indent=2)

    def test_baseline_included_in_total(self):


        self._write_decision({
            "member": "Alice",
            "appliance_decisions": [
                {
                    "time": "20:00-21:00",
                    "location": "客厅",
                    "activity": "看电视",
                    "operations": [{"unique_id": "客厅_电视", "action": "use"}]
                }
            ]
        })

        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()


        self.assertAlmostEqual(calc.baseline_kwh, 1.2, places=4)
        self.assertAlmostEqual(calc.decision_kwh, 0.15, places=4)
        self.assertAlmostEqual(calc.baseline_kwh + calc.decision_kwh, 1.35, places=4)


        profile = calc.household_load_watts
        self.assertEqual(len(profile), 1440)
        self.assertAlmostEqual(profile[0], 50.0, places=2)
        self.assertAlmostEqual(profile[1200], 200.0, places=2)
        self.assertEqual(calc.validation_warnings, [])

    def test_always_on_usage_recorded(self):
        self._write_decision({
            "member": "Alice",
            "appliance_decisions": []
        })
        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()

        fridge = calc.appliance_usage.get("厨房_冰箱")
        self.assertIsNotNone(fridge)
        self.assertAlmostEqual(fridge["total_energy_kwh"], 1.2, places=4)
        self.assertEqual(fridge["total_minutes"], 1440)

    def test_invalid_appliance_and_action_warned(self):

        self._write_decision({
            "member": "Alice",
            "appliance_decisions": [
                {
                    "time": "20:00-21:00",
                    "location": "客厅",
                    "activity": "看电视",
                    "operations": [
                        {"unique_id": "客厅_电视", "action": "use"},
                        {"unique_id": "不存在的电器", "action": "use"},
                        {"unique_id": "客厅_电视", "action": "launch_nuclear"},
                    ]
                }
            ]
        })

        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()

        self.assertEqual(len(calc.validation_warnings), 2)

        self.assertAlmostEqual(calc.decision_kwh, 0.15, places=4)

    def test_profile_file_saved(self):
        self._write_decision({"member": "Alice", "appliance_decisions": []})
        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()

        profile_path = os.path.join(self.tmpdir, "用电信息", "house_load_profile_1440min.json")
        self.assertTrue(os.path.exists(profile_path))

        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        self.assertEqual(len(profile["load_profile_watts"]), 1440)
        self.assertEqual(profile["unit"], "watts")
        self.assertAlmostEqual(profile["total_energy_kwh"], 1.2, places=4)
        self.assertAlmostEqual(profile["peak_watts"], 50.0, places=4)

    def test_daily_cap_truncates_ev_overcharge(self):


        self.home.get_room("厨房").appliances
        garage = Room("车库")
        garage.add_appliance_by_name("电动汽车")
        self.home.add_room(garage)

        self._write_decision({
            "member": "Alice",
            "appliance_decisions": [
                {
                    "time": "20:00-08:00",
                    "location": "车库",
                    "activity": "充电",
                    "operations": [{"unique_id": "车库_电动汽车", "action": "charge_home"}],
                }
            ]
        })

        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()

        ev = calc.appliance_usage["车库_电动汽车"]

        self.assertAlmostEqual(ev["total_energy_kwh"], 28.0, places=4)
        self.assertEqual(ev["usage_segments"][0]["duration_minutes"], 240)
        self.assertTrue(ev["usage_segments"][0]["capped"])
        self.assertTrue(any("超限截断" in w for w in calc.validation_warnings))


class TestSubAgent(unittest.TestCase):
    def test_parallel_call_empty(self):
        self.assertEqual(SubAgent.parallel_call([]), [])

    def test_retry_config_limits(self):

        import config as cfg
        self.assertGreaterEqual(cfg.MAX_RETRIES, 1)
        self.assertFalse(hasattr(cfg, "MAX_WORKERS"))

    def test_reasoning_effort_lowest(self):

        import config as cfg
        self.assertEqual(cfg.REASONING_EFFORT, "low")
        self.assertIn(cfg.REASONING_EFFORT, ("low", "high", "max"))

    def test_concurrency_stats_reset(self):

        SubAgent.reset_tokens()
        current, peak = SubAgent.get_concurrency_stats()
        self.assertEqual(peak, 0)


class TestReport(unittest.TestCase):


    def test_price_elasticity_typical(self):

        self.assertAlmostEqual(price_elasticity(-9.2, 57.1), -0.161, places=3)

    def test_price_elasticity_zero_price_change(self):

        self.assertIsNone(price_elasticity(-5.0, 0))

    def test_price_elasticity_positive_demand_growth(self):

        self.assertEqual(price_elasticity(10.0, 20.0), 0.5)

    def test_tou_elasticity_real_values(self):

        elasticity, q_change = tou_elasticity(56.5, 51.3, 0.55, 0.35)
        self.assertAlmostEqual(q_change, -9.2035, places=3)
        self.assertAlmostEqual(elasticity, -0.161, places=3)
        self.assertLess(elasticity, 0)

    def test_tou_elasticity_zero_baseline(self):

        self.assertEqual(tou_elasticity(0.0, 10.0, 0.55, 0.35), (None, None))

    def test_tou_elasticity_no_response(self):

        elasticity, q_change = tou_elasticity(50.0, 50.0, 0.55, 0.35)
        self.assertEqual(q_change, 0.0)
        self.assertEqual(elasticity, 0.0)

    def test_parse_kwh_plain_and_suffixed(self):

        self.assertEqual(parse_kwh("56.5"), 56.5)
        self.assertEqual(parse_kwh("51.3 (-9.1%)"), 51.3)
        self.assertEqual(parse_kwh("+151.3 (+6.9%)"), 151.3)

    def test_parse_kwh_invalid_returns_none(self):

        self.assertIsNone(parse_kwh("无数据"))
        self.assertIsNone(parse_kwh(None))


class TestLoadFeatures(unittest.TestCase):


    def test_hourly_means_shape(self):
        from engine.load_features import hourly_means
        loads = [100.0] * 1440
        hourly = hourly_means(loads)
        self.assertEqual(len(hourly), 24)
        self.assertTrue(all(v == 100.0 for v in hourly))

    def test_hourly_means_peak_bucket(self):
        from engine.load_features import hourly_means
        loads = [50.0] * 1440
        loads[19 * 60:20 * 60] = [2050.0] * 60
        hourly = hourly_means(loads)
        self.assertEqual(hourly.index(max(hourly)), 19)

    def test_hourly_means_too_short(self):
        from engine.load_features import hourly_means
        with self.assertRaises(ValueError):
            hourly_means([1.0] * 100)

    def test_normalize_shape_sums_to_one(self):
        from engine.load_features import normalize_shape
        shape = normalize_shape([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(sum(shape), 1.0)
        self.assertAlmostEqual(shape[-1], 0.4)

    def test_normalize_shape_zero_total(self):
        from engine.load_features import normalize_shape
        self.assertEqual(normalize_shape([0.0, 0.0]), [0.0, 0.0])

    def test_load_factor_and_peak_to_mean(self):
        from engine.load_features import load_factor, peak_to_mean
        hourly = [100.0, 200.0, 300.0]
        self.assertAlmostEqual(load_factor(hourly), 200.0 / 300.0)
        self.assertAlmostEqual(peak_to_mean(hourly), 300.0 / 200.0)

    def test_peak_and_valley_hour(self):
        from engine.load_features import peak_hour, valley_hour
        hourly = [10.0, 40.0, 20.0, 5.0]
        self.assertEqual(peak_hour(hourly), 1)
        self.assertEqual(valley_hour(hourly), 3)


class TestClustering(unittest.TestCase):


    def _three_shapes(self, n_per=6):
        import numpy as np
        shapes = []
        for _ in range(n_per):
            shapes.append([0.6 + 0.4 * np.sin(np.pi * h / 10) for h in range(24)])
            shapes.append([0.8 - 0.5 * abs(h - 18) / 12 for h in range(24)])
            shapes.append([0.5 + 0.5 * np.sin(np.pi * (h + 6) / 8) for h in range(24)])
        return shapes

    def test_kmeans_recovers_three_clusters(self):
        from engine.load_features import kmeans
        shapes = self._three_shapes()
        labels, centers, wcss = kmeans(shapes, 3, seed=7)
        counts = {}
        for lab in labels:
            counts[lab] = counts.get(lab, 0) + 1
        self.assertEqual(sorted(counts.values()), [6, 6, 6])
        self.assertGreater(wcss, 0)
        self.assertEqual(len(centers), 3)
        self.assertEqual(len(centers[0]), 24)

    def test_kmeans_fewer_samples_than_k(self):
        from engine.load_features import kmeans
        with self.assertRaises(ValueError):
            kmeans([[1.0] * 24, [2.0] * 24], 3)

    def test_kmeans_deterministic(self):
        from engine.load_features import kmeans
        shapes = self._three_shapes()
        l1, c1, _ = kmeans(shapes, 3, seed=42)
        l2, c2, _ = kmeans(shapes, 3, seed=42)
        self.assertEqual(l1, l2)
        self.assertEqual(c1, c2)

    def test_elbow_scores_monotonic(self):
        from engine.load_features import elbow_scores
        shapes = self._three_shapes()
        scores = elbow_scores(shapes)
        self.assertEqual(len(scores), 7)
        self.assertEqual(scores[0]["k"], 2)
        self.assertEqual(scores[-1]["k"], 8)
        wcss_list = [s["wcss"] for s in scores]
        self.assertEqual(wcss_list, sorted(wcss_list, reverse=True))

    def test_auto_k_on_three_separable_shapes(self):
        from engine.load_features import auto_k
        shapes = self._three_shapes()
        self.assertEqual(auto_k(shapes), 3)


class TestVariability(unittest.TestCase):


    def test_identical_days_zero_variability(self):
        from engine.load_features import variability_index, peak_hour_shift
        day = [100.0] * 24
        daily = [day, day, day]
        self.assertEqual(variability_index(daily), 0.0)
        self.assertEqual(peak_hour_shift(daily), 0.0)

    def test_peak_shift_detected(self):
        from engine.load_features import peak_hour_shift
        base = [50.0] * 24
        day1 = list(base)
        day2 = list(base)
        day1[8] = 500.0
        day2[19] = 500.0
        self.assertAlmostEqual(peak_hour_shift([day1, day2]), 5.5, places=2)

    def test_daily_kwh_cv(self):
        from engine.load_features import daily_kwh_cv
        self.assertEqual(daily_kwh_cv([10.0, 10.0, 10.0]), 0.0)
        self.assertAlmostEqual(daily_kwh_cv([10.0, 30.0]), 0.5, places=4)
        self.assertEqual(daily_kwh_cv([]), 0.0)

    def test_hourly_cv_curve_shape(self):
        from engine.load_features import hourly_cv_curve
        day1 = [100.0] * 24
        day2 = [100.0] * 24
        day2[12] = 300.0
        curve = hourly_cv_curve([day1, day2])
        self.assertEqual(len(curve), 24)
        self.assertAlmostEqual(curve[0], 0.0)
        self.assertAlmostEqual(curve[12], 0.5, places=4)

    def test_zero_mean_hour_safe(self):
        from engine.load_features import hourly_cv_curve
        curve = hourly_cv_curve([[0.0] * 24, [0.0] * 24])
        self.assertEqual(curve, [0.0] * 24)

    def test_variability_index_between(self):
        from engine.load_features import variability_index
        stable = [[100.0] * 24, [100.0] * 24, [100.0] * 24]
        wild = [[100.0] * 24, [900.0] * 24, [100.0] * 24]
        self.assertLess(variability_index(stable), variability_index(wild))


if __name__ == "__main__":
    unittest.main(verbosity=2)
