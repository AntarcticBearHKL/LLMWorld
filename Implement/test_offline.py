







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

    def test_group_stats_dynamic_labels(self):
        from analyze_groups import group_stats
        labels = {"h1": "规律", "h2": "规律", "h3": "波动"}
        scenarios = {"baseline": {"h1": 10.0, "h2": 14.0, "h3": 8.0},
                     "tou": {"h1": 9.5, "h2": 13.0, "h3": 6.0}}
        rows = {r["group"]: r for r in group_stats(labels, scenarios)}
        self.assertEqual(set(rows.keys()), {"规律", "波动"})
        self.assertAlmostEqual(rows["波动"]["tou_change_pct"], -25.0, places=2)
        self.assertAlmostEqual(rows["规律"]["tou_change_pct"], -6.25, places=2)

    def test_load_variability_labels_mapping(self):
        from analyze_groups import load_variability_labels
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            import os
            real_path = os.path.join("outputs", "__fake_world", "analysis",
                                     "variability_baseline.json")
            if os.path.exists(real_path):
                os.makedirs(os.path.dirname(real_path), exist_ok=True)
                with open(real_path, "w", encoding="utf-8") as f:
                    json.dump({"regular_half": ["h1"], "variable_half": ["h2", "h3"]}, f)
                labels = load_variability_labels("__fake_world")
                self.assertEqual(labels["h1"], "规律")
                self.assertEqual(labels["h2"], "波动")
                os.remove(real_path)
                try:
                    os.rmdir(os.path.dirname(real_path))
                    os.rmdir(os.path.dirname(os.path.dirname(real_path)))
                except OSError:
                    pass


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

    def test_peak_demand_render(self):
        from engine.policy import Policy
        text = Policy.peak_demand(rate_per_kw=12.0).render()
        self.assertIn("需量电价", text)
        self.assertIn("12.0 澳元/kW", text)
        self.assertIn("最高", text)

    def test_ev_delay_render_menu(self):
        from engine.policy import Policy
        text = Policy.ev_delay().render()
        self.assertIn("延迟激励", text)
        self.assertIn("每延迟 1 小时", text)
        self.assertIn("0.39", text)
        self.assertIn("0.55", text)

    def test_ev_delay_custom_params(self):
        from engine.policy import Policy
        text = Policy.ev_delay(max_delay_hours=4, incentive_per_hour=0.05,
                               flat_rate=0.5).render()
        self.assertIn("0.30", text)

    def test_from_name_new_policies(self):
        from engine.policy import Policy
        self.assertEqual(Policy.from_name("peak_demand").type, "peak_demand")
        self.assertEqual(Policy.from_name("ev_delay").type, "ev_delay")
        with self.assertRaises(ValueError):
            Policy.from_name("no_such_policy")

    def test_night_setback_render(self):
        from engine.policy import Policy
        text = Policy.night_setback().render()
        self.assertIn("夜间降暖", text)
        self.assertIn("23:00-06:00", text)
        self.assertIn("16-18°C", text)
        self.assertIn("5-10%", text)
        self.assertEqual(Policy.from_name("night_setback").type,
                         "night_setback")

    def test_in_home_display_render(self):
        from engine.policy import Policy
        text = Policy.in_home_display().render()
        self.assertIn("智能电表实时反馈", text)
        self.assertIn("瞬时功率", text)
        self.assertIn("近 7 日", text)
        self.assertEqual(Policy.from_name("in_home_display").type,
                         "in_home_display")

    def test_combined_policy_render(self):
        from engine.policy import Policy
        combined = Policy.from_name("tou,nudge")
        self.assertEqual(combined.type, "tou+nudge")
        text = combined.render()
        self.assertIn("政策组合", text)
        self.assertIn("分时电价", text)
        self.assertIn("社会规范", text)
        self.assertIn("tou + nudge", text)

    def test_combined_policy_triple(self):
        from engine.policy import Policy
        combined = Policy.combine("peak_demand,ev_delay,subsidy")
        text = combined.render()
        self.assertEqual(combined.type, "peak_demand+ev_delay+subsidy")
        self.assertIn("需量电价", text)
        self.assertIn("延迟激励", text)
        self.assertIn("低谷充电补贴", text)

    def test_combined_policy_unknown_raises(self):
        from engine.policy import Policy
        with self.assertRaises(ValueError):
            Policy.from_name("tou,no_such")

    def test_combined_policy_whitespace(self):
        from engine.policy import Policy
        combined = Policy.from_name("tou, nudge")
        self.assertEqual(combined.type, "tou+nudge")

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

    def test_prompt_template_has_routine_anchor(self):

        from engine.prompt import Prompt
        rendered = Prompt().load("simulate_step1_macro_plan",
            member_name="Alice", member_age=28, member_occupation="软件工程师",
            member_personality="细心", date="2026年4月21日", day_type="工作日",
            time_context="日期：2026年4月21日（工作日）",
            home_structure="{}", members_info="[]", memory_context="")
        self.assertIn("典型作息锚点", rendered)
        self.assertIn("6:30-7:30", rendered)
        self.assertIn("22:30-23:30", rendered)

    def test_prompt_step4_has_appliance_time_anchor(self):

        from engine.prompt import Prompt
        rendered = Prompt().load("simulate_step4_batch_appliance_decision",
            member_name="Alice", member_age=28, member_occupation="软件工程师",
            member_habits="按时作息", member_timeline="[]",
            home_structure_with_appliances="{}",
            season="夏天", weather="晴天", temperature=28,
            policy_context="", world_news="")
        self.assertIn("典型使用时段", rendered)
        self.assertIn("22:30-07:00", rendered)
        self.assertIn("电动汽车充电", rendered)




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

    def test_build_report_empty_world_no_crash(self):
        from make_report import build_report
        report_path, content = build_report("__no_such_world")
        self.assertTrue(report_path.endswith("paper_material___no_such_world.md"))
        self.assertIn("行为聚类", content)
        self.assertIn("行为变异性", content)
        self.assertIn("多世界对比", content)
        self.assertIn("无 clusters_", content)


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
        rng = np.random.default_rng(3)
        shapes = []
        for _ in range(n_per):
            noise_a = rng.normal(0, 0.02, 24)
            noise_b = rng.normal(0, 0.02, 24)
            noise_c = rng.normal(0, 0.02, 24)
            shapes.append([0.6 + 0.4 * np.sin(np.pi * h / 10) + noise_a[h] for h in range(24)])
            shapes.append([0.8 - 0.5 * abs(h - 18) / 12 + noise_b[h] for h in range(24)])
            shapes.append([0.5 + 0.5 * np.sin(np.pi * (h + 6) / 8) + noise_c[h] for h in range(24)])
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

    def test_kmeans_duplicate_shapes_raise(self):
        from engine.load_features import kmeans
        with self.assertRaises(ValueError):
            kmeans([[1.0] * 24, [1.0] * 24, [1.0] * 24], 2)

    def test_elbow_breaks_on_degenerate(self):
        from engine.load_features import elbow_scores
        shapes = [[1.0] * 24, [1.0] * 24, [1.0] * 24]
        self.assertEqual(elbow_scores(shapes), [])

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


class TestPeakShape(unittest.TestCase):


    def test_peak_plateau_minutes(self):
        from compare_policies import peak_plateau_minutes
        watts = [100.0] * 1440
        watts[0:600] = [900.0] * 600
        self.assertEqual(peak_plateau_minutes(watts, ratio=0.8), 600)

    def test_peak_plateau_zero_curve(self):
        from compare_policies import peak_plateau_minutes
        self.assertEqual(peak_plateau_minutes([0.0] * 1440), 0)

    def test_peak_to_mean_ratio(self):
        from compare_policies import peak_to_mean_ratio
        watts = [100.0] * 1440
        watts[0:1440] = [100.0] * 1440
        watts[100] = 300.0
        self.assertAlmostEqual(peak_to_mean_ratio(watts), 3.0, places=2)
        self.assertIsNone(peak_to_mean_ratio([0.0] * 1440))

    def test_high_overlap_minutes(self):
        from compare_policies import high_overlap_minutes
        watts = [1000.0] * 1440
        watts[0:30] = [32000.0] * 30
        self.assertEqual(high_overlap_minutes(watts, threshold=30000), 30)

    def test_compare_includes_peak_shape_fields(self):
        from compare_policies import compare
        baseline = {"policy": "baseline", "load_profile_watts": [500.0] * 1440,
                    "total_energy_kwh": 12.0}
        watts = [500.0] * 1440
        watts[700:760] = [9000.0] * 60
        intervention = {"policy": "tou", "load_profile_watts": watts,
                        "total_energy_kwh": 11.0}
        report = compare(baseline, intervention)
        self.assertIn("peak_plateau_minutes_baseline", report)
        self.assertGreater(report["peak_plateau_minutes_intervention"], 0)
        self.assertIn("peak_to_mean_intervention", report)
        self.assertIn("high_overlap_minutes_intervention", report)


class TestPeakOverlap(unittest.TestCase):

    def test_single_overlap_event(self):
        from engine.load_features import peak_overlap_events
        watts = [500.0] * 1440
        watts[510:570] = [8500.0] * 60
        events = peak_overlap_events(watts, threshold=8000)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["start_minute"], 510)
        self.assertEqual(events[0]["end_minute"], 569)
        self.assertEqual(events[0]["duration_minutes"], 60)
        self.assertEqual(events[0]["peak_watts"], 8500.0)
        self.assertEqual(events[0]["start_time"], "08:30")

    def test_two_separate_events(self):
        from engine.load_features import peak_overlap_events
        watts = [500.0] * 1440
        watts[100:110] = [9000.0] * 10
        watts[700:720] = [8200.0] * 20
        events = peak_overlap_events(watts, threshold=8000)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["start_minute"], 100)
        self.assertEqual(events[1]["start_minute"], 700)

    def test_below_threshold_no_event(self):
        from engine.load_features import peak_overlap_events
        watts = [500.0] * 1440
        watts[100:110] = [7999.0] * 10
        self.assertEqual(peak_overlap_events(watts, threshold=8000), [])

    def test_count_and_minutes(self):
        from engine.load_features import peak_overlap_count, peak_overlap_minutes
        watts = [500.0] * 1440
        watts[100:110] = [9000.0] * 10
        self.assertEqual(peak_overlap_count(watts), 1)
        self.assertEqual(peak_overlap_minutes(watts), 10)

    def test_summary_contains_overlap(self):
        import tempfile
        from engine.energy_calculator import EnergyCalculator
        with tempfile.TemporaryDirectory() as tmp:
            calc = EnergyCalculator(None, tmp)
            calc.household_load_watts = [500.0] * 1440
            calc.household_load_watts[510:570] = [8500.0] * 60
            calc._finalize_statistics()
            self.assertEqual(len(calc.peak_overlap_events), 1)


class TestBehaviorPatterns(unittest.TestCase):


    def _samples(self):
        import numpy as np
        def shape(peak_h):
            return [0.6 + 0.4 * np.sin(np.pi * h / 10) if h < 12 else
                    0.6 + 0.4 * np.exp(-((h - peak_h) ** 2) / 4) for h in range(24)]
        samples = []
        for day in range(3):
            samples.append({"house_id": "fixed", "date": f"2026042{day + 1}",
                            "kwh": 10.0, "shape": shape(19), "hourly": [1.0] * 24})
        for day in range(3):
            samples.append({"house_id": "switch", "date": f"2026041{day + 1}",
                            "kwh": 12.0, "shape": shape(8 if day == 0 else 19),
                            "hourly": [1.0] * 24})
        return samples

    def test_transitions_counted(self):
        from analyze_behavior_patterns import build_report
        report = build_report(self._samples(), 2)
        by_house = {h["house_id"]: h for h in report["per_house"]}
        self.assertEqual(by_house["fixed"]["transitions"], 0)
        self.assertGreater(by_house["switch"]["transitions"], 0)
        self.assertEqual(report["k"], 2)

    def test_dominant_cluster(self):
        from analyze_behavior_patterns import build_report
        report = build_report(self._samples(), 2)
        by_house = {h["house_id"]: h for h in report["per_house"]}
        seq = by_house["switch"]["cluster_sequence"]
        counts = {}
        for c in seq:
            counts[c] = counts.get(c, 0) + 1
        dominant = max(counts, key=counts.get)
        self.assertEqual(by_house["switch"]["dominant_cluster"], dominant)

    def test_cluster_centers_count(self):
        from analyze_behavior_patterns import build_report
        report = build_report(self._samples(), 2)
        self.assertEqual(len(report["clusters"]), 2)
        self.assertEqual(len(report["clusters"][0]["center_shape"]), 24)
        self.assertEqual(report["samples"], 6)

    def test_empty_samples_raise(self):
        from analyze_behavior_patterns import build_report
        with self.assertRaises(ValueError):
            build_report([], 2)


class TestCompareWorlds(unittest.TestCase):


    def _write_matrix(self, world_id, scenarios):
        import os
        path = os.path.join("outputs", world_id, "comparison",
                            "policy_matrix.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"scenarios": scenarios}, f)

    def test_load_world_policies_parses_matrix(self):
        from compare_worlds import load_world_policies, _to_float
        self.assertEqual(_to_float("30.0 (+0.0%)"), 0.0)
        self.assertEqual(_to_float("20.5 (-8.5%)"), -8.5)
        self.assertIsNone(_to_float(None))
        self.assertIsNone(_to_float("no-data"))
        rows = load_world_policies("__no_such_world")
        self.assertEqual(rows, {})

    def test_build_matrix_shape(self):
        from compare_worlds import build_matrix
        import os
        self._write_matrix("__cw_a", [
            {"场景": "baseline"}, {"场景": "tou",
             "总kWh": "10.0 (-8.5%)", "晚峰16-21点kWh": "5.0 (-15.0%)",
             "峰值W": "3000 (-20.0%)", "峰值平台分钟": "60 (-30.0%)"}])
        self._write_matrix("__cw_b", [
            {"场景": "baseline"}, {"场景": "tou",
             "总kWh": "11.0 (-5.0%)", "晚峰16-21点kWh": "5.5 (-10.0%)",
             "峰值W": "3200 (-12.0%)", "峰值平台分钟": "90 (-20.0%)"}])
        try:
            matrix = build_matrix(["__cw_a", "__cw_b"])
            self.assertEqual(matrix["worlds"], ["__cw_a", "__cw_b"])
            self.assertEqual(matrix["scenarios"], ["tou"])
            self.assertAlmostEqual(
                matrix["cells"]["__cw_a"]["tou"]["total_change_pct"], -8.5)
            self.assertAlmostEqual(
                matrix["cells"]["__cw_b"]["tou"]["peak_hours_change_pct"], -10.0)
        finally:
            import shutil
            for w in ("__cw_a", "__cw_b"):
                path = os.path.join("outputs", w)
                if os.path.isdir(path):
                    shutil.rmtree(path)

    def test_build_matrix_no_worlds_raise(self):
        from compare_worlds import build_matrix
        with self.assertRaises(ValueError):
            build_matrix(["__no_such_world_a", "__no_such_world_b"])


class TestSimArgs(unittest.TestCase):


    def test_baseline_args(self):
        from server import build_sim_args
        args = build_sim_args("pop06", {"policy": "", "days": 1, "date": ""})
        self.assertEqual(args, ["pop06", "--days", "1"])

    def test_policy_and_date(self):
        from server import build_sim_args
        args = build_sim_args("pop06", {"policy": "tou", "days": 3,
                                        "date": "2026-04-21"})
        self.assertIn("--policy", args)
        self.assertIn("tou", args)
        self.assertIn("--date", args)
        self.assertIn("2026-04-21", args)

    def test_combined_policy(self):
        from server import build_sim_args
        args = build_sim_args("pop06", {"policy": "tou,nudge", "days": 1,
                                        "date": ""})
        self.assertIn("tou,nudge", args)

    def test_invalid_policy_raises(self):
        from server import build_sim_args
        with self.assertRaises(ValueError):
            build_sim_args("pop06", {"policy": "no_such_policy",
                                     "days": 1, "date": ""})

    def test_scenario_override(self):
        from server import build_sim_args
        args = build_sim_args("pop06", {"policy": "tou", "days": 1,
                                        "date": "", "scenario": "my_run"})
        self.assertIn("--scenario", args)
        self.assertIn("my_run", args)

    def test_create_world_validation(self):
        from server import validate_create_args
        with self.assertRaises(ValueError):
            validate_create_args("", 3)
        with self.assertRaises(ValueError):
            validate_create_args("bad/name", 3)
        with self.assertRaises(ValueError):
            validate_create_args("__x", 11)
        with self.assertRaises(ValueError):
            validate_create_args("__x", "not-a-number")
        world_id, count = validate_create_args("__ok_world", "3")
        self.assertEqual((world_id, count), ("__ok_world", 3))


class TestPeerNudge(unittest.TestCase):


    def test_neighbor_mean_excludes_self(self):
        from population_runner import neighbor_mean_kwh
        kwhs = {"h1": 10.0, "h2": 14.0, "h3": 18.0}
        self.assertEqual(neighbor_mean_kwh(kwhs, "h1"), 16.0)
        self.assertEqual(neighbor_mean_kwh(kwhs, "h3"), 12.0)

    def test_neighbor_mean_no_others(self):
        from population_runner import neighbor_mean_kwh
        self.assertIsNone(neighbor_mean_kwh({"h1": 10.0}, "h1"))
        self.assertIsNone(neighbor_mean_kwh({}, "h1"))

    def test_neighbor_mean_rounding(self):
        from population_runner import neighbor_mean_kwh
        kwhs = {"h1": 10.0, "h2": 11.0, "h3": 12.0, "h4": 13.0}
        self.assertEqual(neighbor_mean_kwh(kwhs, "h1"), 12.0)


class TestEventResponse(unittest.TestCase):


    def _samples(self):
        import numpy as np
        def shape(peak_h):
            return [0.6 + 0.4 * np.exp(-((h - peak_h) ** 2) / 4) for h in range(24)]
        samples = []
        for house_id in ("h1", "h2"):
            for day, ph in enumerate((19, 8, 8, 8)):
                samples.append({
                    "house_id": house_id, "date": f"2026050{day + 1}",
                    "kwh": 10.0 if day != 1 else 8.0,
                    "shape": shape(ph), "hourly": [1.0] * 24})
        return samples

    def test_event_day_moves_more(self):
        from analyze_event_response import build_event_response
        events = {"2026-05-02": [{"title": "电价上涨"}]}
        report = build_event_response(self._samples(), events)
        by_date = {e["date"]: e for e in report["per_event"]}
        self.assertGreater(report["event_move_rate"], report["non_event_move_rate"])
        self.assertEqual(by_date["2026-05-02"]["kwh_change_pct"], -20.0)

    def test_no_events(self):
        from analyze_event_response import build_event_response
        report = build_event_response(self._samples(), {})
        self.assertEqual(report["event_days"], 0)
        self.assertEqual(report["per_event"], [])

    def test_empty_samples_raise(self):
        from analyze_event_response import build_event_response
        with self.assertRaises(ValueError):
            build_event_response([], {})


class TestTimelineServer(unittest.TestCase):


    def test_load_timeline_merges(self):
        from server import load_timeline
        import os, shutil
        base = os.path.join("outputs", "__tl_world")
        pop = os.path.join(base, "population", "tou", "20260501")
        os.makedirs(pop, exist_ok=True)
        with open(os.path.join(pop, "population_profile_1440min.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"day_policy": "tou", "policy": "tou",
                       "total_energy_kwh": 55.0}, f)
        ev_dir = os.path.join("worlds", "__tl_world")
        os.makedirs(ev_dir, exist_ok=True)
        with open(os.path.join(ev_dir, "events.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"events": [{"date": "20260501",
                                   "title": "电价上涨", "content": "x"}]}, f)
        try:
            rows = load_timeline("__tl_world")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["policy"], "tou")
            self.assertEqual(rows[0]["kwh"], 55.0)
            self.assertEqual(rows[0]["events"][0]["title"], "电价上涨")
        finally:
            shutil.rmtree(base)
            shutil.rmtree(ev_dir)

    def test_load_timeline_empty_world(self):
        from server import load_timeline
        self.assertEqual(load_timeline("__no_such_world"), [])

    def test_load_templates_nonempty(self):
        from server import load_templates
        items = load_templates()
        self.assertGreaterEqual(len(items), 10)
        for item in items:
            self.assertTrue(item["name"])
            self.assertTrue(item["title"])
            self.assertTrue(item["content"])


class TestTimelineGuard(unittest.TestCase):


    def _write_state(self, world_id, date_str):
        import os, shutil
        path = os.path.join("worlds", world_id, "state.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"date": date_str, "memory_days": {}}, f)

    def test_unstarted_any_date(self):
        from engine.world import validate_start_date, get_world_last_date
        self.assertIsNone(get_world_last_date("__guard_new"))
        self.assertEqual(validate_start_date("__guard_new", "2026-05-01"),
                         "2026年05月01日")
        self.assertIsNone(validate_start_date("__guard_new", None))

    def test_started_exact_next_day(self):
        from engine.world import validate_start_date
        import os, shutil
        self._write_state("__guard_w", "2026年4月21日")
        try:
            self.assertEqual(validate_start_date("__guard_w", "2026-04-22"),
                             "2026年04月22日")
            self.assertEqual(validate_start_date("__guard_w", None),
                             "2026年04月22日")
        finally:
            shutil.rmtree(os.path.join("worlds", "__guard_w"))

    def test_started_rewind_rejected(self):
        from engine.world import validate_start_date
        import os, shutil
        self._write_state("__guard_w2", "2026年4月21日")
        try:
            with self.assertRaises(ValueError):
                validate_start_date("__guard_w2", "2026-04-21")
            with self.assertRaises(ValueError):
                validate_start_date("__guard_w2", "2026-04-01")
        finally:
            shutil.rmtree(os.path.join("worlds", "__guard_w2"))

    def test_started_skip_day_rejected(self):
        from engine.world import validate_start_date
        import os, shutil
        self._write_state("__guard_w3", "2026年4月21日")
        try:
            with self.assertRaises(ValueError):
                validate_start_date("__guard_w3", "2026-04-23")
        finally:
            shutil.rmtree(os.path.join("worlds", "__guard_w3"))

    def test_parse_world_date_formats(self):
        from engine.world import parse_world_date
        self.assertEqual(parse_world_date("2026年4月21日").day, 21)
        self.assertEqual(parse_world_date("2026-04-21").day, 21)
        self.assertEqual(parse_world_date("20260421").day, 21)
        self.assertIsNone(parse_world_date(None))
        with self.assertRaises(ValueError):
            parse_world_date("not-a-date")


class TestAnomalies(unittest.TestCase):


    def _profiles(self):
        import math
        def curve(kwh_scale, peak_w, overlap):
            watts = []
            for m in range(1440):
                h = m // 60
                base = kwh_scale * 100
                v = base + peak_w * math.exp(-((h - 19) ** 2) / 3)
                watts.append(round(v, 2))
            if overlap:
                watts[510:570] = [9000.0] * 60
            return watts
        profiles = []
        for i in range(5):
            profiles.append({"house_id": f"h{i + 1}", "total_energy_kwh": 10.0 + i,
                             "load_profile_watts": curve(1.0 + i * 0.05, 800, False)})
        profiles.append({"house_id": "h6", "total_energy_kwh": 45.0,
                         "load_profile_watts": curve(4.5, 2000, True)})
        return profiles

    def test_high_consumer_flagged(self):
        from analyze_anomalies import build_report
        report = build_report(self._profiles())
        by_house = {r["house_id"]: r for r in report["per_house"]}
        self.assertGreater(by_house["h6"]["z_total_kwh"], 2)
        self.assertIn("total_kwh", " ".join(by_house["h6"]["anomaly_flags"]))
        self.assertGreater(by_house["h6"]["max_abs_z"], 2)
        self.assertEqual(by_house["h1"]["anomaly_flags"], [])

    def test_overlap_counted_in_flags(self):
        from analyze_anomalies import build_report
        report = build_report(self._profiles())
        h6 = next(r for r in report["per_house"] if r["house_id"] == "h6")
        self.assertGreater(h6["overlap_count"], 0)
        self.assertEqual(report["anomaly_count"], 1)
        self.assertEqual(report["anomalies"][0]["house_id"], "h6")

    def test_empty_profiles_raise(self):
        from analyze_anomalies import build_report
        with self.assertRaises(ValueError):
            build_report([])

    def test_zscore_few_samples(self):
        from analyze_anomalies import zscore
        self.assertEqual(zscore([1.0, 2.0]), [None, None])


class TestBehaviorLoad(unittest.TestCase):


    def _house_result(self, activities, loads):
        return {"house_id": "h1", "member_count": 2, "activities": activities,
                "load_profile_watts": loads}

    def test_at_home_higher_load(self):
        from analyze_behavior_load import build_report, _parse_minutes
        loads = [100.0] * 1440
        loads[18 * 60:21 * 60] = [800.0] * (3 * 60)
        activities = [
            {"time": "09:00-17:00", "start": 540, "end": 1020,
             "location": "公司", "activity": "上班", "at_home": False},
            {"time": "18:00-22:00", "start": 1080, "end": 1320,
             "location": "厨房", "activity": "晚餐", "at_home": True},
        ]
        report = build_report([self._house_result(activities, loads)])
        r = report["per_house"][0]
        self.assertGreater(r["at_home_mean_watts"], r["away_mean_watts"])
        self.assertTrue(r["load_consistent"])
        self.assertTrue(r["peak_aligned"])
        self.assertEqual(report["anomaly_count"], 0)

    def test_away_high_load_flagged(self):
        from analyze_behavior_load import build_report
        loads = [100.0] * 1440
        loads[10 * 60:14 * 60] = [3000.0] * (4 * 60)
        activities = [
            {"time": "09:00-17:00", "start": 540, "end": 1020,
             "location": "公司", "activity": "上班", "at_home": False},
            {"time": "18:00-22:00", "start": 1080, "end": 1320,
             "location": "客厅", "activity": "休息", "at_home": True},
        ]
        report = build_report([self._house_result(activities, loads)])
        r = report["per_house"][0]
        self.assertFalse(r["load_consistent"])
        self.assertEqual(report["anomaly_count"], 1)

    def test_peak_alignment(self):
        from analyze_behavior_load import build_report
        loads = [50.0] * 1440
        loads[20 * 60:21 * 60] = [4000.0] * 60
        activities = [
            {"time": "19:00-22:00", "start": 1140, "end": 1320,
             "location": "客厅", "activity": "看电视", "at_home": True},
        ]
        report = build_report([self._house_result(activities, loads)])
        r = report["per_house"][0]
        self.assertTrue(r["peak_aligned"])

    def test_empty_raise(self):
        from analyze_behavior_load import build_report
        with self.assertRaises(ValueError):
            build_report([])


class TestSolar(unittest.TestCase):


    def test_curve_shape_summer_clear(self):
        from analyze_solar import solar_generation_curve
        curve = solar_generation_curve("夏天", "晴天", capacity=5000)
        self.assertEqual(len(curve), 1440)
        self.assertEqual(curve[0], 0.0)
        peak_minute = max(range(1440), key=lambda m: curve[m])
        self.assertLessEqual(abs(peak_minute / 60 - 13.5), 1.5)
        self.assertGreater(curve[peak_minute], 4000)

    def test_curve_zero_at_night(self):
        from analyze_solar import solar_generation_curve
        curve = solar_generation_curve("冬天", "晴天", capacity=5000)
        for m in range(0, 7 * 60):
            self.assertEqual(curve[m], 0.0)
        for m in range(17 * 60, 1440):
            self.assertEqual(curve[m], 0.0)

    def test_weather_factor(self):
        from analyze_solar import solar_generation_curve
        clear = solar_generation_curve("夏天", "晴天", capacity=5000)
        rain = solar_generation_curve("夏天", "雨天", capacity=5000)
        self.assertGreater(sum(clear), sum(rain) * 5)

    def test_self_consumption_math(self):
        from analyze_solar import build_report
        loads = [500.0] * 1440
        profiles = [{"house_id": "h1", "total_energy_kwh": 12.0,
                     "load_profile_watts": loads, "weather": "晴天"}]
        report = build_report(profiles, 5000, "夏天")
        r = report["per_house"][0]
        self.assertGreater(r["solar_gen_kwh"], 0)
        self.assertGreaterEqual(r["self_consumption_rate"], 0.0)
        self.assertLessEqual(r["self_consumption_rate"], 1.0)
        self.assertLessEqual(r["grid_import_kwh"], r["total_load_kwh"])

    def test_empty_raise(self):
        from analyze_solar import build_report
        with self.assertRaises(ValueError):
            build_report([], 5000, "夏天")

    def test_battery_charges_surplus(self):
        from analyze_solar import battery_operation
        gen = [0.0] * 1440
        gen[10 * 60:14 * 60] = [6000.0] * (4 * 60)
        load = [500.0] * 1440
        charge, discharge = battery_operation(load, gen, 10.0, 3.0)
        self.assertGreater(sum(charge), 0)
        self.assertGreater(sum(discharge), 0)

    def test_battery_discharges_evening(self):
        from analyze_solar import battery_operation
        gen = [0.0] * 1440
        gen[10 * 60:14 * 60] = [6000.0] * (4 * 60)
        load = [500.0] * 1440
        charge, discharge = battery_operation(load, gen, 10.0, 3.0)
        discharge_start = next(m for m in range(1440) if discharge[m] > 0)
        self.assertGreaterEqual(discharge_start, 17 * 60)
        self.assertLess(discharge_start, 22 * 60)
        self.assertGreater(sum(discharge), 0)

    def test_battery_capacity_limited(self):
        from analyze_solar import battery_operation
        gen = [0.0] * 1440
        gen[8 * 60:18 * 60] = [5000.0] * (10 * 60)
        load = [100.0] * 1440
        charge, _ = battery_operation(load, gen, 5.0, 3.0)
        charged_kwh = sum(charge) / 60000
        self.assertLessEqual(charged_kwh, 5.0 + 1e-6)

    def test_battery_improves_self_consumption(self):
        from analyze_solar import build_report
        loads = [300.0] * 1440
        loads[18 * 60:22 * 60] = [2000.0] * (4 * 60)
        profiles = [{"house_id": "h1", "total_energy_kwh": 15.0,
                     "load_profile_watts": loads, "weather": "晴天"}]
        without = build_report(profiles, 5000, "夏天", 0.0)
        with_batt = build_report(profiles, 5000, "夏天", 10.0, 3.0)
        self.assertGreater(
            with_batt["per_house"][0]["self_consumption_rate"],
            without["per_house"][0]["self_consumption_rate"])


class TestElectrification(unittest.TestCase):


    def test_ev_curve_night(self):
        from analyze_electrification import ev_curve
        curve = ev_curve(power_watts=7000, hours=3, start_hour=22)
        self.assertEqual(sum(1 for w in curve if w > 0), 180)
        self.assertEqual(curve[22 * 60], 7000)
        self.assertEqual(curve[6 * 60], 0)

    def test_ev_curve_crosses_midnight(self):
        from analyze_electrification import ev_curve
        curve = ev_curve(power_watts=7000, hours=4, start_hour=22)
        self.assertEqual(sum(1 for w in curve if w > 0), 240)
        self.assertEqual(curve[1 * 60], 7000)

    def test_heat_pump_curve(self):
        from analyze_electrification import heat_pump_curve
        curve = heat_pump_curve(power_watts=3000)
        self.assertEqual(curve[7 * 60], 3000)
        self.assertEqual(curve[12 * 60], 0)
        self.assertEqual(curve[20 * 60], 3000)

    def test_hp_peak_impact(self):
        from analyze_electrification import build_report
        loads = [300.0] * 1440
        loads[18 * 60:21 * 60] = [1200.0] * (3 * 60)
        profiles = [{"house_id": "h1", "total_energy_kwh": 10.0,
                     "load_profile_watts": loads}]
        report = build_report(profiles)
        by_name = {r["scenario"]: r for r in report["scenarios"]}
        self.assertLess(by_name["ev"]["total_change_pct"],
                        by_name["hp"]["total_change_pct"])
        self.assertGreater(by_name["hp"]["evening_change_pct"],
                           by_name["ev"]["evening_change_pct"])
        self.assertGreater(by_name["ev"]["peak_change_pct"],
                           by_name["hp"]["peak_change_pct"])
        self.assertEqual(by_name["ev_hp"]["scenario"], "ev_hp")

    def test_empty_raise(self):
        from analyze_electrification import build_report
        with self.assertRaises(ValueError):
            build_report([])


class TestAdvice(unittest.TestCase):


    def _profiles(self):
        import math
        def curve(base, peak_w, overlap=False):
            watts = []
            for m in range(1440):
                h = m // 60
                v = base + peak_w * math.exp(-((h - 19) ** 2) / 3)
                watts.append(round(v, 2))
            if overlap:
                watts[510:570] = [9000.0] * 60
            return watts
        return [
            {"house_id": "h1", "total_energy_kwh": 10.0, "load_profile_watts": curve(100, 800)},
            {"house_id": "h2", "total_energy_kwh": 11.0, "load_profile_watts": curve(100, 800)},
            {"house_id": "h3", "total_energy_kwh": 12.0, "load_profile_watts": curve(100, 800)},
            {"house_id": "h4", "total_energy_kwh": 13.0, "load_profile_watts": curve(100, 800)},
            {"house_id": "h5", "total_energy_kwh": 14.0, "load_profile_watts": curve(100, 800)},
            {"house_id": "h6", "total_energy_kwh": 45.0, "load_profile_watts": curve(400, 2500, True)},
        ]

    def test_high_consumer_advice(self):
        from analyze_advice import build_report
        report = build_report(self._profiles())
        by_house = {r["house_id"]: r for r in report["per_house"]}
        joined = " ".join(by_house["h6"]["advice"])
        self.assertIn("高于社区平均", joined)
        self.assertIn("叠加", joined)

    def test_evening_peak_advice(self):
        from analyze_advice import build_report
        report = build_report(self._profiles())
        h1 = next(r for r in report["per_house"] if r["house_id"] == "h1")
        self.assertTrue(any("晚峰" in a for a in h1["advice"]))

    def test_healthy_household(self):
        from analyze_advice import advice_for
        advice = advice_for({"total_kwh_z": 0.5, "overlap_count": 0,
                             "peak_hour": 12, "peak_to_mean": 2.0})
        self.assertEqual(advice, [])


class TestSeasonal(unittest.TestCase):


    def _per_house(self):
        summer_day = {"date": "20260115", "kwh": 20.0,
                      "hourly": [400.0 + 1500.0 * (h == 14) for h in range(24)]}
        winter_day = {"date": "20260715", "kwh": 25.0,
                      "hourly": [400.0 + 1800.0 * (h == 19) for h in range(24)]}
        return [{"house_id": "h1", "days": [summer_day, winter_day, summer_day]}]

    def test_season_grouping(self):
        from analyze_seasonal import build_report, season_of
        self.assertEqual(season_of("20260115"), "夏天")
        self.assertEqual(season_of("20260715"), "冬天")
        report = build_report(self._per_house())
        by_name = {r["season"]: r for r in report["seasons"]}
        self.assertEqual(by_name["夏天"]["samples"], 2)
        self.assertEqual(by_name["冬天"]["samples"], 1)
        self.assertAlmostEqual(by_name["夏天"]["mean_kwh"], 20.0)
        self.assertAlmostEqual(by_name["冬天"]["mean_kwh"], 25.0)

    def test_season_peak_hour(self):
        from analyze_seasonal import build_report
        report = build_report(self._per_house())
        by_name = {r["season"]: r for r in report["seasons"]}
        self.assertAlmostEqual(by_name["夏天"]["mean_peak_hour"], 14)
        self.assertAlmostEqual(by_name["冬天"]["mean_peak_hour"], 19)

    def test_empty_raise(self):
        from analyze_seasonal import build_report
        with self.assertRaises(ValueError):
            build_report([])


class TestWeatherSensitivity(unittest.TestCase):


    def _points(self, temps, kwhs, conditions=None):
        points = []
        for i, (t, k) in enumerate(zip(temps, kwhs)):
            points.append({"date": f"2026010{i + 1}", "temperature": t,
                           "kwh": k, "conditions": {conditions[i]} if conditions else {"晴天"}})
        return points

    def test_positive_correlation(self):
        from analyze_weather_sensitivity import build_report
        report = build_report(self._points(
            [20, 22, 25, 28, 31], [12, 13, 15, 18, 22]))
        self.assertGreater(report["temperature_kwh_corr"], 0.9)
        self.assertGreater(report["kwh_per_degree"], 0)

    def test_negative_correlation(self):
        from analyze_weather_sensitivity import build_report
        report = build_report(self._points(
            [8, 10, 12, 14, 16], [20, 18, 16, 14, 12]))
        self.assertLess(report["temperature_kwh_corr"], -0.9)
        self.assertLess(report["kwh_per_degree"], 0)

    def test_by_weather_grouping(self):
        from analyze_weather_sensitivity import build_report
        report = build_report(self._points(
            [20, 22, 24, 26, 28], [10, 11, 12, 14, 16],
            ["晴天", "晴天", "雨天", "雨天", "雨天"]))
        rows = {r["condition"]: r for r in report["by_weather"]}
        self.assertEqual(rows["晴天"]["samples"], 2)
        self.assertEqual(rows["雨天"]["samples"], 3)

    def test_empty_raise(self):
        from analyze_weather_sensitivity import build_report
        with self.assertRaises(ValueError):
            build_report([])


class TestNilm(unittest.TestCase):


    def test_find_plateaus(self):
        from analyze_nilm import find_plateaus
        watts = [0.0] * 1440
        watts[600:660] = [2000.0] * 60
        plateaus = find_plateaus(watts)
        self.assertEqual(len(plateaus), 1)
        self.assertEqual(plateaus[0]["watts"], 2000.0)
        self.assertEqual(plateaus[0]["start"], 600)

    def test_match_appliances(self):
        from analyze_nilm import build_report
        watts = [100.0] * 1440
        watts[600:660] = [2100.0] * 60
        appliances = [
            {"unique_id": "kitchen_cooker", "name": "电磁炉",
             "power_watts": 2000, "total_energy_kwh": 2.0},
            {"unique_id": "living_light", "name": "灯",
             "power_watts": 100, "total_energy_kwh": 2.4},
        ]
        report = build_report(watts, appliances)
        by_name = {r["name"]: r for r in report["per_appliance"]}
        self.assertAlmostEqual(by_name["电磁炉"]["estimated_kwh"], 2.0, places=2)
        self.assertAlmostEqual(by_name["灯"]["estimated_kwh"], 2.3, places=2)
        self.assertGreater(report["disaggregation_rate"], 0.9)

    def test_empty_raise(self):
        from analyze_nilm import build_report
        with self.assertRaises(ValueError):
            build_report([0.0] * 1440, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
