"""离线单元测试：不调用任何 LLM API，只测纯逻辑。

运行方式（在 LLMWorld 根目录）：
    python Implement/test_offline.py

覆盖：时间解析、时间线装载、能耗计算（含常开基载）、分钟负荷曲线、决策校验、并发层空输入。
"""

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
    """基线对比指标（计划5）。"""

    def test_hourly_normalized(self):
        loads = [50.0] * 1440
        loads[19 * 60:20 * 60] = [2050.0] * 60   # 19 点整点高峰
        curve = hourly_normalized(loads)
        self.assertEqual(len(curve), 24)
        mean = sum(curve) / 24
        self.assertAlmostEqual(mean, 1.0)        # 归一化后均值 = 1
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
        self.assertGreater(report["correlation"], 0.9)   # 同形状 → 高相关


class TestGroupAnalysis(unittest.TestCase):
    """节能意识分组（计划10）。"""

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
        # 高意识组 TOU 响应为负（节电）
        self.assertAlmostEqual(rows["高"]["tou_mean_kwh"], 10.0)
        self.assertAlmostEqual(rows["高"]["tou_change_pct"], -16.67, places=2)
        # 低意识组几乎不响应
        self.assertAlmostEqual(rows["低"]["tou_change_pct"], 2.5, places=2)


class TestNewsBoard(unittest.TestCase):
    """新闻台（计划13：上帝模式）。"""

    def test_filter_by_date(self):
        from engine.news import NewsBoard, NewsItem
        board = NewsBoard()
        board.add_event(NewsItem("2026-04-21", "07:00", "征税", "内容A"))
        board.add_event(NewsItem("2026-04-22", "07:00", "返利", "内容B"))

        self.assertEqual(len(board.available_on("2026-04-20")), 0)   # 未来事件不可见
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
        self.assertIn("性格", text)   # 个性分析指令

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
    """可视化后端数据层（计划18）。"""

    def test_list_worlds_contains_pop02(self):
        import server
        worlds = server.list_worlds()
        ids = [w["id"] for w in worlds]
        self.assertIn("pop02", ids)

    def test_load_profile_known_scenario(self):
        import server
        data = server.load_profile("pop02", "tou", "2026-04-21")
        self.assertIsNotNone(data)
        self.assertEqual(len(data["load_profile_watts"]), 1440)
        self.assertGreater(data["total_energy_kwh"], 0)

    def test_load_events_pop02(self):
        import server
        events = server.load_events("pop02")
        self.assertGreaterEqual(len(events.get("events", [])), 1)


class TestEnvironmentInterface(unittest.TestCase):
    """环境信息开放接口（计划23）。"""

    def setUp(self):
        import config as cfg
        self._saved_mode = cfg.ENV_MODE
        self._saved_file = cfg.ENV_MANUAL_FILE

    def tearDown(self):
        import config as cfg
        cfg.ENV_MODE = self._saved_mode
        cfg.ENV_MANUAL_FILE = self._saved_file

    def test_config_mode_temp_within_season_range(self):
        """config 模式：温度落在该季节范围内。"""
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
        """同种子 → 同天气（实验可复现）。"""
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
        """manual 模式：读配置文件固定值。"""
        import config as cfg
        cfg.ENV_MODE = "manual"
        from engine.environment_interface import EnvironmentInterface
        w = EnvironmentInterface.get_weather({}, "2026-04-21", "春天")
        self.assertEqual(w["mode"], "manual")
        self.assertIn("condition", w)

    def test_manual_missing_file_raises(self):
        """manual 模式但文件不存在 → 显式报错（不静默）。"""
        import config as cfg
        cfg.ENV_MODE = "manual"
        cfg.ENV_MANUAL_FILE = "不存在的文件.json"
        from engine.environment_interface import EnvironmentInterface
        with self.assertRaises(FileNotFoundError):
            EnvironmentInterface.get_weather({}, "2026-04-21", "春天")


class TestPolicy(unittest.TestCase):
    """政策渲染与对比指标（计划8）。"""

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
        """干预把 2 kWh 从晚峰挪到谷段 → 晚峰变化 -X%、谷段 +X%。"""
        from compare_policies import compare
        from population_runner import aggregate_population

        def make_profile(peak_watts, valley_extra):
            loads = [50.0] * 1440
            for h in range(17, 20):           # 晚峰 17-19 点
                loads[h * 60:(h + 1) * 60] = [peak_watts] * 60
            for h in range(23, 24):           # 谷段 23 点
                loads[h * 60:(h + 1) * 60] = [valley_extra] * 60
            return loads

        baseline = aggregate_population([("h1", {
            "energy_calculator": FakeEnergyCalculator(make_profile(2000, 0)),
            "energy_summary": {"total_energy_kwh": 12.0}})])

        intervention = aggregate_population([("h1", {
            "energy_calculator": FakeEnergyCalculator(make_profile(1500, 500)),
            "energy_summary": {"total_energy_kwh": 12.0}})])

        report = compare(baseline, intervention)
        self.assertLess(report["peak_hours_change_pct"], 0)     # 晚峰削减
        self.assertGreater(report["valley_hours_change_pct"], 0)  # 谷段上升
        self.assertAlmostEqual(report["total_change_pct"], 0.0, places=1)  # 总量近似不变


class TestPopulationV2(unittest.TestCase):
    """世界生成 v2（计划22：Big Five + 垂直家庭 + 关联）。"""

    def test_big_five_to_energy_awareness(self):
        """心理学映射：尽责性高 → 节能意识高。"""
        from population import big_five_to_energy_awareness
        self.assertEqual(big_five_to_energy_awareness(
            {"conscientiousness": 9, "openness": 3, "extraversion": 5,
             "agreeableness": 6, "neuroticism": 4}), "高")
        self.assertEqual(big_five_to_energy_awareness(
            {"conscientiousness": 2, "openness": 3, "extraversion": 5,
             "agreeableness": 6, "neuroticism": 4}), "低")

    def test_big_five_to_text_describes_high(self):
        from population import big_five_to_text
        text = big_five_to_text({"openness": 9, "conscientiousness": 5,
                                 "extraversion": 5, "agreeableness": 5,
                                 "neuroticism": 5})
        self.assertIn("开放性高", text)
        self.assertIn("新技术", text)

    def test_quota_distribution_covers_all_types(self):
        """配额：8 类家庭全部覆盖，总数正确。"""
        import random
        from population import _quota_distribution
        counts = _quota_distribution(100, random.Random(1))
        self.assertEqual(sum(counts.values()), 100)
        self.assertEqual(len(counts), 8)   # 8 类全在

    def test_couple_age_association(self):
        """成员关联：夫妻年龄差 ≤5（2508.09964 关联思想）。"""
        import random
        from population import _build_template
        h = _build_template("young_couple", random.Random(7))
        ages = sorted(m["age"] for m in h["members"])
        self.assertLessEqual(ages[1] - ages[0], 5)

    def test_multigenerational_age_order(self):
        """多代同堂：三代年龄有序（祖父母夫妻差≤5，代际差≥18）。"""
        import random
        from population import _build_template
        h = _build_template("multigenerational", random.Random(3))
        ages = sorted(m["age"] for m in h["members"])
        # ages = [孩子, 父母, 祖父母(小), 祖父母(大)]
        self.assertLessEqual(ages[3] - ages[2], 5)    # 祖父母是夫妻，年龄差小
        self.assertGreaterEqual(ages[2] - ages[1], 20)  # 祖父母-父母 ≥20
        self.assertGreaterEqual(ages[1] - ages[0], 18)  # 父母-孩子 ≥18

    def test_big_five_field_in_household(self):
        """v2 字段：big_five / behavior_text / news_sensitivity 存在。"""
        import random
        from population import _build_template
        h = _build_template("single_living", random.Random(5))
        pers = h["members"][0]["personality"]
        self.assertIn("big_five", pers)
        self.assertEqual(len(pers["big_five"]), 5)
        self.assertIn("behavior_text", pers)
        self.assertIn("news_sensitivity", pers)

    def test_dedupe_names(self):
        """家庭内成员姓名唯一（agent 身份键要求）。"""
        import random
        from population import _build_template, _dedupe_names
        h = _build_template("multigenerational", random.Random(3))
        _dedupe_names(h)
        names = [m["name"] for m in h["members"]]
        self.assertEqual(len(names), len(set(names)))


class TestPopulation(unittest.TestCase):
    """人口构建器 + 聚合（计划4）。"""

    def test_builder_deterministic(self):
        """同种子两次生成完全一致（论文可复现要求）。"""
        import random
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        h1 = _build_template("young_couple", rng1)
        h2 = _build_template("young_couple", rng2)
        self.assertEqual(json.dumps(h1, ensure_ascii=False), json.dumps(h2, ensure_ascii=False))

    def test_builder_heterogeneous(self):
        """不同种子/类型生成不同家庭（异质性）。"""
        import random
        a = _build_template("young_couple", random.Random(1))
        b = _build_template("family_with_kids", random.Random(2))
        self.assertNotEqual(a["type"], b["type"])
        self.assertEqual(len(b["members"]), 3)   # 有孩家庭 3 人

    def test_aggregation_math(self):
        """聚合：总曲线 = 逐户曲线之和，统计量正确。"""
        house_results = []
        for i, watts in enumerate([(100.0, 500.0), (150.0, 700.0)]):
            loads = [watts[0]] * 1440
            loads[1200] = watts[1]   # 20:00 各自峰值

            day_result = {
                "energy_calculator": FakeEnergyCalculator(loads),
                "energy_summary": {"total_energy_kwh": watts[1] * 0.06},
            }
            house_results.append((f"house_{i}", day_result))

        pop = aggregate_population(house_results)

        self.assertEqual(pop["households"], 2)
        self.assertAlmostEqual(pop["load_profile_watts"][0], 250.0)        # 100+150
        self.assertAlmostEqual(pop["load_profile_watts"][1200], 1200.0)    # 500+700
        self.assertEqual(pop["peak_time"], "20:00")
        self.assertAlmostEqual(pop["mean_household_kwh"], (500.0 * 0.06 + 700.0 * 0.06) / 2, places=4)
        self.assertGreater(pop["std_household_kwh"], 0)   # 异质性存在


class TestMemory(unittest.TestCase):
    """跨天记忆：摘要生成与 prompt 注入。"""

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
        loads[1200] += 2000.0   # 20:00 高峰 2050W

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
        self.assertEqual(alice["wake_time"], "07:30")    # 第一个非睡觉活动
        self.assertEqual(alice["sleep_time"], "23:59")   # 最后一个睡觉段结束
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
        """模板在 memory_context 为空时也能正常渲染。"""
        from engine.prompt import Prompt
        rendered = Prompt().load("simulate_step1_macro_plan",
            member_name="Alice", member_age=28, member_occupation="软件工程师",
            member_personality="细心", date="2026年4月21日", day_type="工作日",
            time_context="日期：2026年4月21日（工作日）",
            home_structure="{}", members_info="[]", memory_context="")
        self.assertNotIn("memory_context", rendered)   # 占位符被替换，无残留


# ---------- 测试用固定家庭：1 台冰箱（常开）+ 1 台电视（按需）----------

def build_test_home():
    home = Home("测试之家")

    kitchen = Room("厨房")
    kitchen.add_appliance_by_name("冰箱")   # always_on，默认日耗 1.2 kWh
    home.add_room(kitchen)

    living = Room("客厅")
    living.add_appliance_by_name("电视")    # on_demand，150W
    home.add_room(living)

    alice = Member("Alice", 28, "软件工程师", "细心", {"wake_time": "07:00"})
    alice.add_personal_appliance_by_name("手机")  # charging，20W
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
        # "not-a-range" 被修复逻辑拆成 not/range → 都解析失败回退 0:00 → 跨天规则变全天 (0,1440)
        self.assertEqual(utils.parse_time_range("not-a-range"), (0, 1440))

    def test_parse_time_range_multi_dash_repair(self):
        # "18:00-19:00-20:00" 这种 LLM 常见错误：取第一个和最后一个
        self.assertEqual(utils.parse_time_range("18:00-19:00-20:00"), (1080, 1200))


class TestTimeline(unittest.TestCase):
    def test_load_and_sort(self):
        tl = Timeline("Alice")
        tl.load_from_activities([
            {"time": "19:00-22:00", "location": "客厅", "activity": "看电视"},
            {"time": "08:00-09:00", "location": "厨房", "activity": "吃早餐"},
        ])
        self.assertEqual(len(tl.slots), 2)
        self.assertEqual(tl.slots[0].activity, "吃早餐")   # 已按开始时间排序
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
        """计划1核心：冰箱基载 1.2 kWh 必须计入日总用电。"""
        # 只给 Alice 一条合法决策：看电视 1 小时（150W → 0.15 kWh）
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

        # 冰箱 1.2 + 电视 0.15
        self.assertAlmostEqual(calc.baseline_kwh, 1.2, places=4)
        self.assertAlmostEqual(calc.decision_kwh, 0.15, places=4)
        self.assertAlmostEqual(calc.baseline_kwh + calc.decision_kwh, 1.35, places=4)

        # 家庭分钟负荷：1440 点；基载 50W 持续；20:00 区间多 150W
        profile = calc.household_load_watts
        self.assertEqual(len(profile), 1440)
        self.assertAlmostEqual(profile[0], 50.0, places=2)         # 0:00 只有冰箱
        self.assertAlmostEqual(profile[1200], 200.0, places=2)     # 20:00 = 50 + 150
        self.assertEqual(calc.validation_warnings, [])             # 无警告

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
        """非法 unique_id / action 必须进 warnings，绝不静默。"""
        self._write_decision({
            "member": "Alice",
            "appliance_decisions": [
                {
                    "time": "20:00-21:00",
                    "location": "客厅",
                    "activity": "看电视",
                    "operations": [
                        {"unique_id": "客厅_电视", "action": "use"},
                        {"unique_id": "不存在的电器", "action": "use"},          # 未知电器
                        {"unique_id": "客厅_电视", "action": "launch_nuclear"},   # 非法操作
                    ]
                }
            ]
        })

        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()

        self.assertEqual(len(calc.validation_warnings), 2)
        # 合法操作仍被计入
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
        self.assertAlmostEqual(profile["peak_watts"], 50.0, places=4)  # 只有基载时峰值 50W

    def test_daily_cap_truncates_ev_overcharge(self):
        """计划7：电动汽车 12 小时充电被截断到 4 小时上限，并记警告。"""
        # 给 Alice 加一台电动汽车（charging 类），配置 7000W
        self.home.get_room("厨房").appliances  # noop 确保 room 存在
        garage = Room("车库")
        garage.add_appliance_by_name("电动汽车")
        self.home.add_room(garage)

        self._write_decision({
            "member": "Alice",
            "appliance_decisions": [
                {
                    "time": "20:00-08:00",   # 12 小时连续充电
                    "location": "车库",
                    "activity": "充电",
                    "operations": [{"unique_id": "车库_电动汽车", "action": "charge_home"}],
                }
            ]
        })

        calc = EnergyCalculator(self.home, self.tmpdir)
        calc.calculate_all_energy()

        ev = calc.appliance_usage["车库_电动汽车"]
        # 7000W × 4 小时 = 28 kWh（截断到上限 240 分钟）
        self.assertAlmostEqual(ev["total_energy_kwh"], 28.0, places=4)
        self.assertEqual(ev["usage_segments"][0]["duration_minutes"], 240)
        self.assertTrue(ev["usage_segments"][0]["capped"])
        self.assertTrue(any("超限截断" in w for w in calc.validation_warnings))


class TestSubAgent(unittest.TestCase):
    def test_parallel_call_empty(self):
        self.assertEqual(SubAgent.parallel_call([]), [])

    def test_retry_config_limits(self):
        """用户 2026-08 指令：并发不设上限（观测保留，无硬性限制常量）。"""
        import config as cfg
        self.assertGreaterEqual(cfg.MAX_RETRIES, 1)   # 重试仍启用
        self.assertFalse(hasattr(cfg, "MAX_WORKERS"))  # 并发上限已移除

    def test_concurrency_stats_reset(self):
        """并发统计可查询，且峰值初始为 0。"""
        SubAgent.reset_tokens()
        current, peak = SubAgent.get_concurrency_stats()
        self.assertEqual(peak, 0)   # 本轮未调用 API 前峰值应为 0


class TestReport(unittest.TestCase):
    """论文报告：价格弹性计算（make_report）。"""

    def test_price_elasticity_typical(self):
        # 峰段用电 -9.2%，电价 +57.1% → 弹性 ≈ -0.161
        self.assertAlmostEqual(price_elasticity(-9.2, 57.1), -0.161, places=3)

    def test_price_elasticity_zero_price_change(self):
        # 电价不变（ΔP% = 0）→ 弹性未定义，返回 None
        self.assertIsNone(price_elasticity(-5.0, 0))

    def test_price_elasticity_positive_demand_growth(self):
        # 需求上升 +10% 而价格不变动区间外的情况：涨价仍增长 → 正弹性
        self.assertEqual(price_elasticity(10.0, 20.0), 0.5)

    def test_tou_elasticity_real_values(self):
        # 论文实测值：56.5 → 51.3 kWh，0.35 → 0.55 澳元/kWh
        elasticity, q_change = tou_elasticity(56.5, 51.3, 0.55, 0.35)
        self.assertAlmostEqual(q_change, -9.2035, places=3)
        self.assertAlmostEqual(elasticity, -0.161, places=3)
        self.assertLess(elasticity, 0)   # 涨价 → 用电下降

    def test_tou_elasticity_zero_baseline(self):
        # 基线峰段电量为 0 → 无法算变化率，返回 (None, None) 而非崩溃
        self.assertEqual(tou_elasticity(0.0, 10.0, 0.55, 0.35), (None, None))

    def test_tou_elasticity_no_response(self):
        # 电价涨但峰段用电不变 → 弹性为 0（完全无响应）
        elasticity, q_change = tou_elasticity(50.0, 50.0, 0.55, 0.35)
        self.assertEqual(q_change, 0.0)
        self.assertEqual(elasticity, 0.0)

    def test_parse_kwh_plain_and_suffixed(self):
        # 矩阵单元格：纯数字与带 '(±x.x%)' 后缀均可解析
        self.assertEqual(parse_kwh("56.5"), 56.5)
        self.assertEqual(parse_kwh("51.3 (-9.1%)"), 51.3)
        self.assertEqual(parse_kwh("+151.3 (+6.9%)"), 151.3)

    def test_parse_kwh_invalid_returns_none(self):
        # 无数字或 None → 返回 None，不抛异常
        self.assertIsNone(parse_kwh("无数据"))
        self.assertIsNone(parse_kwh(None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
