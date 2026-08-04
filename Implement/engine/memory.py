"""家庭记忆：跨天行为连续性（论文 Park et al. 记忆-反思-规划循环的最简实现）。

机制：
- 每天模拟结束后，从"当天时间线 + 用电信息"生成本地结构化摘要（0 额外 LLM 调用）
- 第二天的第一层（宏观计划）prompt 注入"昨日记忆"，让计划受昨天行为影响
- 摘要包含：成员昨日活动概要、作息（起床/入睡）、家庭用电要点

这样 LLM 无需任何额外调用就能形成"习惯连续性"，为后续升级为
LLM 反思摘要/语义检索留出接口。
"""


class HouseholdMemory:
    def __init__(self):
        self.days = []   # 每天一份结构化摘要
        self.last = None # 最近一天的摘要（注入明天的 prompt）

    # ---------- 每天结束后调用 ----------

    def update_from_day(self, day_result):
        """从一天的结果生成摘要并存档。day_result 来自 World.simulate_day。"""
        summary = self._build_summary(day_result)
        self.days.append(summary)
        self.last = summary
        return summary

    # ---------- 摘要生成（纯本地逻辑）----------

    def _build_summary(self, day_result):
        planner = day_result["planner"]

        # 每个成员：活动概要 + 作息
        member_summaries = {}
        for name, timeline in planner.timelines.items():
            member_summaries[name] = self._summarize_member(timeline)

        # 家庭用电要点
        energy = day_result.get("energy_summary", {})
        electricity = self._summarize_electricity(day_result, energy)

        return {
            "date": day_result.get("date", ""),
            "members": member_summaries,
            "electricity": electricity,
        }

    def _summarize_member(self, timeline):
        slots = timeline.slots

        wake_time = None   # 起床：第一个非睡觉活动段的开始
        sleep_time = None  # 入睡：最后一个含"睡觉"活动段的结束
        activities = []    # 主要活动概要（最多 8 段）

        for slot in slots:
            activity = slot.activity or ""
            is_sleep = ("睡觉" in activity or "睡眠" in activity or "入睡" in activity)

            if not is_sleep and wake_time is None:
                wake_time = self._fmt(slot.start)
            if is_sleep:
                sleep_time = self._fmt(slot.end)

            if not is_sleep and len(activities) < 8:
                activities.append(f"{self._fmt(slot.start)}-{self._fmt(slot.end)} {slot.location} {activity}")

        if not activities and slots:
            # 整天只有睡觉等极端情况：取首段兜底
            s = slots[0]
            activities.append(f"{self._fmt(s.start)}-{self._fmt(s.end)} {s.location} {s.activity}")

        return {
            "activities": activities,
            "wake_time": wake_time,
            "sleep_time": sleep_time,
        }

    def _summarize_electricity(self, day_result, energy_summary):
        total = energy_summary.get("total_energy_kwh", 0)
        baseline = energy_summary.get("baseline_kwh", 0)
        decision = energy_summary.get("decision_kwh", 0)

        # 高峰时段：从 1440 分钟负荷曲线找峰值
        peak_time = None
        peak_watts = None
        calculator = day_result.get("energy_calculator")
        if calculator is not None and hasattr(calculator, "household_load_watts"):
            loads = calculator.household_load_watts
            if loads:
                peak_minute = max(range(len(loads)), key=lambda m: loads[m])
                peak_watts = round(loads[peak_minute])
                peak_time = f"{peak_minute // 60:02d}:{peak_minute % 60:02d}"

        # 主要耗电电器（前 3）
        top_appliances = []
        for app in energy_summary.get("appliances", [])[:3]:
            top_appliances.append(f"{app['name']} {app['total_energy_kwh']:.1f} kWh")

        return {
            "total_kwh": round(total, 2),
            "baseline_kwh": round(baseline, 2),
            "decision_kwh": round(decision, 2),
            "peak_time": peak_time,
            "peak_watts": peak_watts,
            "top_appliances": top_appliances,
        }

    # ---------- 注入 prompt ----------

    def get_prompt_context(self):
        """返回"昨日记忆"章节文本（无记忆时返回空串，调用方需容忍空）。"""
        if not self.last:
            return ""

        lines = []
        for name, m in self.last["members"].items():
            lines.append(f"{name}昨天的活动：")
            for act in m["activities"]:
                lines.append(f"  - {act}")
            rhythm = []
            if m["wake_time"]:
                rhythm.append(f"起床 {m['wake_time']}")
            if m["sleep_time"]:
                rhythm.append(f"入睡 {m['sleep_time']}")
            if rhythm:
                lines.append(f"  作息：{'，'.join(rhythm)}")
            lines.append("")

        elec = self.last["electricity"]
        elec_line = f"昨天（{self.last['date']}）家庭用电：总 {elec['total_kwh']} kWh"
        if elec["peak_time"]:
            elec_line += f"，高峰 {elec['peak_time']}（{elec['peak_watts']} W）"
        lines.append(elec_line)
        if elec["top_appliances"]:
            lines.append(f"主要耗电：{'、'.join(elec['top_appliances'])}")

        header = "## 昨日记忆（帮助你保持习惯连续性，昨天发生的事会影响今天的安排）"
        return header + "\n" + "\n".join(lines)

    # ---------- 工具 ----------

    @staticmethod
    def _fmt(minutes):
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
