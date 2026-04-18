import json
import os
from datetime import datetime
from .prompt import Prompt
from .subagent import SubAgent

class Executor:
    def __init__(self, home, planner):
        self.home = home
        self.planner = planner
        self.appliance_operations = []
        self.log_dir = planner.log_dir
        self.segment_counter = 0
        self.prompt = Prompt()
    
    def execute_all_segments(self, season="夏天", weather="晴天", temperature=28):
        for member_name, timeline in self.planner.timelines.items():
            member = self._get_member(member_name)
            if not member:
                continue
            
            for slot in timeline.slots:
                segment = {
                    "time": slot._format_time_range(),
                    "location": slot.location,
                    "activity": slot.activity
                }
                self._execute_segment(member, segment, season, weather, temperature)
        
        return self.appliance_operations
    
    def _get_member(self, name):
        for member in self.home.members:
            if member.name == name:
                return member
        return None
    
    def _time_to_slot(self, time_str):
        parts = time_str.split("-")
        if len(parts) != 2:
            return None, None
        
        start_time = parts[0].strip()
        end_time = parts[1].strip()
        
        start_hour, start_min = map(int, start_time.split(":"))
        end_hour, end_min = map(int, end_time.split(":"))
        
        start_slot = start_hour * 6 + start_min // 10
        end_slot = end_hour * 6 + end_min // 10
        
        return start_slot, end_slot
    
    def _execute_segment(self, member, segment, season, weather, temperature):
        time = segment["time"]
        location = segment["location"]
        activity = segment["activity"]
        
        if location == "外出":
            return
        
        room = self.home.get_room(location)
        if not room:
            return
        
        appliances_info = "\n".join([f"- {info}" for info in room.get_appliances_info()])
        
        home_structure = self.home.to_json()
        home_structure_str = json.dumps(home_structure, ensure_ascii=False, indent=2)
        
        current_status = {}
        start_slot, end_slot = self._time_to_slot(time)
        if start_slot is not None:
            for appliance in room.appliances:
                current_status[appliance.name] = "开启" if appliance.status[start_slot] else "关闭"
        
        status_str = "\n".join([f"- {name}: {status}" for name, status in current_status.items()])
        
        prompt = self.prompt.load("appliance_decision",
            home_structure=home_structure_str,
            time=time,
            member_name=member.name,
            member_age=member.age,
            member_occupation=member.occupation,
            location=location,
            activity=activity,
            season=season,
            weather=weather,
            temperature=temperature,
            appliances_info=appliances_info,
            status_str=status_str,
            member_habits=member.habits
        )
        
        result = SubAgent.single_call(prompt, json_mode=True, thinking=False)
        tokens = SubAgent.get_tokens()
        
        self.segment_counter += 1
        safe_time = time.replace(":", "-")
        self._save_log(f"07_第七层_用电决策_{self.segment_counter:03d}_{member.name}_{safe_time}", prompt, result, tokens)
        
        try:
            decision_data = json.loads(result)
            operations = decision_data.get("operations", [])
            
            if start_slot is not None and end_slot is not None:
                for op in operations:
                    appliance_name = op["appliance"]
                    action = op["action"]
                    
                    appliance = self.home.get_appliance(location, appliance_name)
                    if appliance:
                        if action == "开启":
                            for slot in range(start_slot, min(end_slot, 144)):
                                appliance.status[slot] = True
                        elif action == "关闭":
                            for slot in range(start_slot, min(end_slot, 144)):
                                appliance.status[slot] = False
            
            record = {
                "time": time,
                "member": member.name,
                "location": location,
                "activity": activity,
                "operations": operations
            }
            
            self.appliance_operations.append(record)
            
        except Exception as e:
            print(f"解析用电决策失败: {e}")
    
    def _save_log(self, stage_name, prompt, response, tokens=None):
        log_file = os.path.join(self.log_dir, f"{stage_name}.md")
        
        with open(log_file, "w", encoding="utf-8") as f:
            if tokens:
                miss, hit, completion = tokens
                f.write(f"Token使用: prompt_cache_miss={miss}, prompt_cache_hit={hit}, completion={completion}\n\n")
            
            f.write(f"# {stage_name}\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write("## 提示词\n\n")
            f.write("```\n")
            f.write(prompt)
            f.write("\n```\n\n")
            f.write("---\n\n")
            f.write("## LLM返回结果\n\n")
            f.write("```json\n")
            f.write(response)
            f.write("\n```\n")
