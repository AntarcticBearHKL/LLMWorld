







import json
import os

import config
from . import utils

MINUTES_PER_DAY = 1440


class EnergyCalculator:
    def __init__(self, home, log_dir):
        self.home = home
        self.log_dir = log_dir
        self.energy_info_dir = os.path.join(log_dir, "用电信息")
        os.makedirs(self.energy_info_dir, exist_ok=True)

        self.appliance_usage = {}
        self.household_load_watts = [0.0] * MINUTES_PER_DAY
        self.baseline_kwh = 0.0
        self.decision_kwh = 0.0
        self.validation_warnings = []
        self._daily_minutes = {}



    def load_all_decisions(self):
        decisions = []
        for filename in os.listdir(self.log_dir):
            if filename.startswith("04_第四层_批量用电决策_") and filename.endswith(".json"):
                filepath = os.path.join(self.log_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    decisions.append(json.load(f))
        return decisions



    def calculate_all_energy(self):
        decisions = self.load_all_decisions()


        for decision_data in decisions:
            member_name = decision_data.get("member", "未知成员")
            self._process_member_decisions(member_name, decision_data)


        self._add_always_on_baseline()


        self._finalize_statistics()
        self._save_energy_info()

        return self.appliance_usage



    def _process_member_decisions(self, member_name, decision_data):

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

                    continue


                clipped_end = self._apply_daily_cap(appliance, start_minutes, end_minutes,
                                                    time_range, member_name)

                if clipped_end <= start_minutes:
                    continue


                energy = appliance.calculate_energy(start_minutes, clipped_end, power_source="home")
                self.decision_kwh += energy


                watts = appliance.power_watts
                for minute in range(start_minutes, clipped_end):
                    actual_minute = minute % MINUTES_PER_DAY
                    self.household_load_watts[actual_minute] += watts


                usage = self._get_or_create_usage(appliance)
                usage["usage_segments"].append({
                    "time_range": time_range,
                    "start_minutes": start_minutes,
                    "end_minutes": clipped_end,
                    "duration_minutes": clipped_end - start_minutes,
                    "action": action,
                    "location": location,
                    "member": member_name,
                    "energy_kwh": energy,
                    "capped": clipped_end != end_minutes,
                })
                usage["total_energy_kwh"] += energy
                for minute in range(start_minutes, clipped_end):
                    actual_minute = minute % MINUTES_PER_DAY
                    usage["minute_watts"][actual_minute] += watts



    def _apply_daily_cap(self, appliance, start_minutes, end_minutes, time_range, member_name):




        cap = config.APPLIANCE_DAILY_CAP_MINUTES.get(appliance.name)
        if not cap:
            return end_minutes

        used = self._daily_minutes.get(appliance.unique_id, 0)
        duration = end_minutes - start_minutes
        remaining = cap - used

        if duration <= remaining:
            self._daily_minutes[appliance.unique_id] = used + duration
            return end_minutes

        if remaining <= 0:
            self.validation_warnings.append(
                f"[超限截断] {appliance.name}[{appliance.unique_id}] 当日已用 {used} 分钟"
                f"（上限 {cap}），{member_name} 在 {time_range} 的使用被完全丢弃"
            )
            return start_minutes

        self._daily_minutes[appliance.unique_id] = used + remaining
        self.validation_warnings.append(
            f"[超限截断] {appliance.name}[{appliance.unique_id}] 当日已用 {used} 分钟"
            f"（上限 {cap}），{member_name} 在 {time_range} 的使用从 {duration} 分钟截断为 {remaining} 分钟"
        )
        return start_minutes + remaining



    def _add_always_on_baseline(self):

        baseline_appliances = []

        for appliance in self.home.appliance_registry.values():
            if appliance.appliance_type != "always_on":
                continue


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
