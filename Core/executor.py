import json
import os
from datetime import datetime
from Engine import Agent

class Executor:
    def __init__(self, llm_provider, home, planner):
        self.llm = llm_provider
        self.home = home
        self.planner = planner
        self.appliance_operations = []
        self.log_dir = planner.log_dir
        self.segment_counter = 0
    
    def execute_all_segments(self, season="夏天", weather="晴天", temperature=28):
        for member_name, segments in self.planner.time_segments.items():
            member = self._get_member(member_name)
            if not member:
                continue
            
            for segment in segments:
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
        
        prompt = f"""你是一个家庭用电行为专家。请根据以下信息，决定该时间段需要操作哪些家电。

家庭结构：
{home_structure_str}

时间段信息：
- 时间：{time}
- 人物：{member.name}（{member.age}岁，{member.occupation}）
- 地点：{location}
- 活动：{activity}

环境信息：
- 季节：{season}
- 天气：{weather}
- 气温：{temperature}度

{location}的家电：
{appliances_info}

当前电器状态：
{status_str}

人物用电习惯：
- {member.habits}

请决策：
1. 需要开启哪些家电（如果已经开启则不需要重复开启）
2. 需要关闭哪些家电
3. 每个操作的原因

要求：
- 只操作家中的电器，不涉及家外的设备
- 符合活动需求
- 符合人物习惯
- 合理真实
- 检查电器当前状态，避免重复操作

输出JSON格式：
{{
  "operations": [
    {{"appliance": "家电名称", "action": "开启/关闭", "reason": "原因"}}
  ]
}}"""
        
        agent = Agent("用电决策", self.llm)
        agent.add_input(prompt)
        result = agent.think()
        
        self.segment_counter += 1
        safe_time = time.replace(":", "-")
        self._save_log(f"第四层_用电决策_{self.segment_counter:03d}_{member.name}_{safe_time}", prompt, result.raw)
        
        try:
            decision_data = json.loads(result.raw)
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
    
    def _save_log(self, stage_name, prompt, response):
        log_file = os.path.join(self.log_dir, f"{stage_name}.md")
        
        with open(log_file, "w", encoding="utf-8") as f:
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
