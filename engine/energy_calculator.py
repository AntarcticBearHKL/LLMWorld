import json
import os
from datetime import datetime

class EnergyCalculator:
    def __init__(self, home, log_dir):
        self.home = home
        self.log_dir = log_dir
        self.energy_info_dir = os.path.join(log_dir, "用电信息")
        os.makedirs(self.energy_info_dir, exist_ok=True)
        self.appliance_usage = {}
    
    def load_all_decisions(self):
        decisions = []
        for filename in os.listdir(self.log_dir):
            if filename.startswith("04_第四层_批量用电决策_") and filename.endswith(".json"):
                filepath = os.path.join(self.log_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    decision_data = json.load(f)
                    decisions.append(decision_data)
        return decisions
    
    def calculate_all_energy(self):
        decisions = self.load_all_decisions()
        
        for decision_data in decisions:
            member_name = decision_data.get("member", "未知成员")
            
            for decision in decision_data.get("appliance_decisions", []):
                time_range = decision["time"]
                location = decision.get("location", "")
                start_str, end_str = time_range.split("-")
                
                start_hour, start_min = map(int, start_str.split(":"))
                end_hour, end_min = map(int, end_str.split(":"))
                
                start_minutes = start_hour * 60 + start_min
                end_minutes = end_hour * 60 + end_min
                
                if end_minutes <= start_minutes:
                    end_minutes += 1440
                
                for operation in decision.get("operations", []):
                    appliance_id = operation["unique_id"]
                    action = operation["action"]
                    
                    appliance = self.home.get_appliance(appliance_id)
                    if not appliance:
                        continue
                    
                    if appliance_id not in self.appliance_usage:
                        self.appliance_usage[appliance_id] = {
                            "name": appliance.name,
                            "unique_id": appliance_id,
                            "power_watts": appliance.power_watts,
                            "type": appliance.appliance_type,
                            "minute_status": [False] * 1440,
                            "usage_segments": [],
                            "total_minutes": 0,
                            "total_hours": 0,
                            "total_energy_kwh": 0
                        }
                    
                    if action in ["use", "charge_home"]:
                        power_source = "home" if action != "charge_external" else "external"
                        
                        energy = appliance.calculate_energy(
                            start_minutes,
                            end_minutes,
                            power_source=power_source
                        )
                        
                        for minute in range(start_minutes, end_minutes):
                            actual_minute = minute % 1440
                            self.appliance_usage[appliance_id]["minute_status"][actual_minute] = True
                        
                        self.appliance_usage[appliance_id]["usage_segments"].append({
                            "time_range": time_range,
                            "start_minutes": start_minutes,
                            "end_minutes": end_minutes,
                            "duration_minutes": end_minutes - start_minutes,
                            "action": action,
                            "location": location,
                            "member": member_name,
                            "energy_kwh": energy
                        })
                        
                        self.appliance_usage[appliance_id]["total_energy_kwh"] += energy
        
        for appliance_id, usage_data in self.appliance_usage.items():
            total_minutes = sum(usage_data["minute_status"])
            usage_data["total_minutes"] = total_minutes
            usage_data["total_hours"] = round(total_minutes / 60.0, 2)
        
        self._save_energy_info()
        
        return self.appliance_usage
    
    def _save_energy_info(self):
        for appliance_id, usage_data in self.appliance_usage.items():
            appliance_name = usage_data["name"]
            safe_name = appliance_name.replace("/", "_").replace("\\", "_")
            
            filename = f"{appliance_id}_{safe_name}.json"
            filepath = os.path.join(self.energy_info_dir, filename)
            
            minute_usage = []
            for minute_idx, is_used in enumerate(usage_data["minute_status"]):
                if is_used:
                    hour = minute_idx // 60
                    minute = minute_idx % 60
                    minute_usage.append(f"{hour:02d}:{minute:02d}")
            
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
            "total_energy_kwh": round(sum(u["total_energy_kwh"] for u in self.appliance_usage.values()), 4),
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
    
    def get_summary(self):
        total_energy = sum(u["total_energy_kwh"] for u in self.appliance_usage.values())
        
        return {
            "total_appliances": len(self.appliance_usage),
            "total_energy_kwh": round(total_energy, 4),
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
