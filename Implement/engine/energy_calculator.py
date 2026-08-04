"""能耗计算：把成员的电器使用决策换算成分钟级家庭负荷。

核心改动（计划1）：
1. 常开电器（冰箱等 always_on）的基载耗电自动计入 —— 之前完全丢失，导致日用电偏低
2. 输出家庭级 1440 分钟总负荷曲线 house_load_profile_1440min.json —— 论文 RQ1 的核心产出
3. 非法决策（未知电器/非法操作）记入 validation_warnings，绝不静默
"""

import json
import os

from . import utils

MINUTES_PER_DAY = 1440


class EnergyCalculator:
    def __init__(self, home, log_dir):
        self.home = home
        self.log_dir = log_dir
        self.energy_info_dir = os.path.join(log_dir, "用电信息")
        os.makedirs(self.energy_info_dir, exist_ok=True)

        self.appliance_usage = {}          # 每台电器的使用统计
        self.household_load_watts = [0.0] * MINUTES_PER_DAY   # 家庭每分钟总负荷（瓦）
        self.baseline_kwh = 0.0            # 常开电器基载（千瓦时/天）
        self.decision_kwh = 0.0            # 成员决策耗电（千瓦时/天）
        self.validation_warnings = []      # 决策校验警告

    # ---------- 读取决策 ----------

    def load_all_decisions(self):
        decisions = []
        for filename in os.listdir(self.log_dir):
            if filename.startswith("04_第四层_批量用电决策_") and filename.endswith(".json"):
                filepath = os.path.join(self.log_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    decisions.append(json.load(f))
        return decisions

    # ---------- 主计算 ----------

    def calculate_all_energy(self):
        decisions = self.load_all_decisions()

        # 第一步：处理每个成员的有序决策
        for decision_data in decisions:
            member_name = decision_data.get("member", "未知成员")
            self._process_member_decisions(member_name, decision_data)

        # 第二步：加入常开电器（always_on）基载 —— 计划1修复：之前完全丢失
        self._add_always_on_baseline()

        # 第三步：汇总统计并保存
        self._finalize_statistics()
        self._save_energy_info()

        return self.appliance_usage

    # ---------- 成员决策 ----------

    def _process_member_decisions(self, member_name, decision_data):
        """校验并累加一个成员的全部用电决策。非法操作记入警告，不静默。"""
        cleaned_decisions = utils.validate_appliance_decisions(decision_data, self.home, self.validation_warnings)

        for decision in cleaned_decisions:
            time_range = decision["time"]
            start_minutes = decision["start_minutes"]
            end_minutes = decision["end_minutes"]
            location = decision["location"]

            for operation in decision["operations"]:
                appliance_id = operation["unique_id"]
                action = operation["action"]

                appliance = self.home.get_appliance(appliance_id)
                if not appliance:
                    continue

                if action not in ["use", "charge_home"]:
                    # charge_external（外部充电）不计入家庭用电；use（使用已存电量）不耗家庭电
                    continue

                # 计算这段使用的耗电量（千瓦时）
                energy = appliance.calculate_energy(start_minutes, end_minutes, power_source="home")
                self.decision_kwh += energy

                # 累加进家庭分钟负荷（瓦）
                watts = appliance.power_watts
                for minute in range(start_minutes, end_minutes):
                    actual_minute = minute % MINUTES_PER_DAY
                    self.household_load_watts[actual_minute] += watts

                # 累加进这台电器的使用记录
                usage = self._get_or_create_usage(appliance)
                usage["usage_segments"].append({
                    "time_range": time_range,
                    "start_minutes": start_minutes,
                    "end_minutes": end_minutes,
                    "duration_minutes": end_minutes - start_minutes,
                    "action": action,
                    "location": location,
                    "member": member_name,
                    "energy_kwh": energy
                })
                usage["total_energy_kwh"] += energy
                for minute in range(start_minutes, end_minutes):
                    actual_minute = minute % MINUTES_PER_DAY
                    usage["minute_watts"][actual_minute] += watts

    # ---------- 常开电器基载 ----------

    def _add_always_on_baseline(self):
        """把 always_on 电器（如冰箱）按日耗能平摊进每一分钟，并计入家庭负荷。"""
        baseline_appliances = []

        for appliance in self.home.appliance_registry.values():
            if appliance.appliance_type != "always_on":
                continue

            # 日耗能 → 持续瓦数（1.2 kWh/天 = 50W 持续）
            watts = (appliance.daily_energy_kwh / 24.0) * 1000.0
            kwh_per_day = appliance.daily_energy_kwh

            for minute in range(MINUTES_PER_DAY):
                self.household_load_watts[minute] += watts

            usage = self._get_or_create_usage(appliance)
            usage["total_energy_kwh"] = kwh_per_day
            usage["total_hours"] = 24.0
            usage["total_minutes"] = MINUTES_PER_DAY
            usage["minute_watts"] = [watts] * MINUTES_PER_DAY
            usage["usage_segments"] = [{
                "time_range": "00:00-24:00",
                "start_minutes": 0,
                "end_minutes": MINUTES_PER_DAY,
                "duration_minutes": MINUTES_PER_DAY,
                "action": "always_on",
                "location": appliance.location,
                "member": "（自动基载）",
                "energy_kwh": kwh_per_day
            }]

            self.baseline_kwh += kwh_per_day
            baseline_appliances.append({
                "unique_id": appliance.unique_id,
                "name": appliance.name,
                "kwh_per_day": kwh_per_day,
                "watts": round(watts, 2)
            })

        self.baseline_appliances = baseline_appliances

    # ---------- 统计与保存 ----------

    def _get_or_create_usage(self, appliance):
        if appliance.unique_id not in self.appliance_usage:
            self.appliance_usage[appliance.unique_id] = {
                "name": appliance.name,
                "unique_id": appliance.unique_id,
                "power_watts": appliance.power_watts,
                "type": appliance.appliance_type,
                "minute_watts": [0.0] * MINUTES_PER_DAY,
                "usage_segments": [],
                "total_minutes": 0,
                "total_hours": 0,
                "total_energy_kwh": 0
            }
        return self.appliance_usage[appliance.unique_id]

    def _finalize_statistics(self):
        for usage in self.appliance_usage.values():
            usage["total_minutes"] = sum(1 for w in usage["minute_watts"] if w > 0)
            usage["total_hours"] = round(usage["total_minutes"] / 60.0, 2)

    def _save_energy_info(self):
        # 每台电器的分钟曲线 + 使用段
        for appliance_id, usage_data in self.appliance_usage.items():
            safe_name = usage_data["name"].replace("/", "_").replace("\\", "_")
            filename = f"{appliance_id}_{safe_name}.json"
            filepath = os.path.join(self.energy_info_dir, filename)

            minute_usage = [
                {
                    "minute": idx,
                    "time": f"{idx // 60:02d}:{idx % 60:02d}",
                    "watts": round(watts, 2)
                }
                for idx, watts in enumerate(usage_data["minute_watts"]) if watts > 0
            ]

            output_data = {
                "appliance_info": {
                    "unique_id": usage_data["unique_id"],
                    "name": usage_data["name"],
                    "type": usage_data["type"],
                    "power_watts": usage_data["power_watts"]
                },
                "usage_summary": {
                    "total_minutes": usage_data["total_minutes"],
                    "total_hours": usage_data["total_hours"],
                    "total_energy_kwh": round(usage_data["total_energy_kwh"], 4)
                },
                "usage_segments": usage_data["usage_segments"],
                "minute_by_minute_usage": minute_usage
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

        # 家庭总汇总
        summary_data = {
            "total_appliances": len(self.appliance_usage),
            "total_energy_kwh": round(self.baseline_kwh + self.decision_kwh, 4),
            "baseline_kwh": round(self.baseline_kwh, 4),
            "decision_kwh": round(self.decision_kwh, 4),
            "validation_warnings": self.validation_warnings,
            "appliances": [
                {
                    "unique_id": usage_data["unique_id"],
                    "name": usage_data["name"],
                    "type": usage_data["type"],
                    "total_hours": usage_data["total_hours"],
                    "total_energy_kwh": round(usage_data["total_energy_kwh"], 4)
                }
                for usage_data in self.appliance_usage.values()
            ]
        }
        summary_filepath = os.path.join(self.energy_info_dir, "总用电汇总.json")
        with open(summary_filepath, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        # 家庭级 1440 分钟总负荷曲线（论文 RQ1 核心产出）
        peak_minute = max(range(MINUTES_PER_DAY), key=lambda m: self.household_load_watts[m])
        profile = {
            "unit": "watts",
            "minutes": MINUTES_PER_DAY,
            "baseline_kwh": round(self.baseline_kwh, 4),
            "decision_kwh": round(self.decision_kwh, 4),
            "total_energy_kwh": round(self.baseline_kwh + self.decision_kwh, 4),
            "peak_watts": round(max(self.household_load_watts), 2),
            "peak_minute": peak_minute,
            "peak_time": f"{peak_minute // 60:02d}:{peak_minute % 60:02d}",
            "load_profile_watts": [round(w, 2) for w in self.household_load_watts],
            "hourly_average_watts": [
                round(sum(self.household_load_watts[h * 60:(h + 1) * 60]) / 60.0, 2)
                for h in range(24)
            ]
        }
        profile_filepath = os.path.join(self.energy_info_dir, "house_load_profile_1440min.json")
        with open(profile_filepath, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    def get_summary(self):
        total_energy = self.baseline_kwh + self.decision_kwh
        return {
            "total_appliances": len(self.appliance_usage),
            "total_energy_kwh": round(total_energy, 4),
            "baseline_kwh": round(self.baseline_kwh, 4),
            "decision_kwh": round(self.decision_kwh, 4),
            "appliances": [
                {
                    "unique_id": usage_data["unique_id"],
                    "name": usage_data["name"],
                    "total_hours": usage_data["total_hours"],
                    "total_energy_kwh": round(usage_data["total_energy_kwh"], 4)
                }
                for usage_data in sorted(
                    self.appliance_usage.values(),
                    key=lambda x: x["total_energy_kwh"],
                    reverse=True
                )
            ]
        }
