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


class FakeEnergyCalculator:
    def __init__(self, loads):
        self.household_load_watts = loads


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


class TestSubAgent(unittest.TestCase):
    def test_parallel_call_empty(self):
        self.assertEqual(SubAgent.parallel_call([]), [])

    def test_retry_config_limits(self):
        from engine.subagent import MAX_WORKERS
        self.assertLessEqual(MAX_WORKERS, 10)   # 用户硬性要求：并发 ≤ 10


if __name__ == "__main__":
    unittest.main(verbosity=2)
