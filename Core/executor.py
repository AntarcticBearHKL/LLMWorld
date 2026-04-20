import json
import os
from datetime import datetime
from .prompt import Prompt
from .subagent import SubAgent

def format_json_compact(obj, indent=2, current_indent=0):
    if isinstance(obj, dict):
        if all(not isinstance(v, (dict, list)) for v in obj.values()):
            return json.dumps(obj, ensure_ascii=False)
        
        items = []
        for key, value in obj.items():
            formatted_value = format_json_compact(value, indent, current_indent + indent)
            items.append(f'{" " * (current_indent + indent)}"{key}": {formatted_value}')
        
        return "{\n" + ",\n".join(items) + "\n" + " " * current_indent + "}"
    
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        
        if all(isinstance(item, dict) and all(not isinstance(v, (dict, list)) for v in item.values()) for item in obj):
            items = [format_json_compact(item, indent, current_indent + indent) for item in obj]
            return "[\n" + " " * (current_indent + indent) + (",\n" + " " * (current_indent + indent)).join(items) + "\n" + " " * current_indent + "]"
        
        items = [format_json_compact(item, indent, current_indent + indent) for item in obj]
        return "[\n" + ",\n".join(items) + "\n" + " " * current_indent + "]"
    
    else:
        return json.dumps(obj, ensure_ascii=False)

class Executor:
    def __init__(self, home, planner):
        self.home = home
        self.planner = planner
        self.log_dir = planner.log_dir
        self.prompt = Prompt()
    
    def execute_all_segments(self, season="夏天", weather="晴天", temperature=28):
        prompts = []
        members_data = []
        
        for member_name, timeline in self.planner.timelines.items():
            member = self._get_member(member_name)
            if not member:
                continue
            
            member_timeline = []
            for slot in timeline.slots:
                segment = {
                    "time": slot._format_time_range(),
                    "location": slot.location,
                    "activity": slot.activity
                }
                if slot.desc:
                    segment["desc"] = slot.desc
                member_timeline.append(segment)
            
            home_structure_with_appliances = self._get_home_structure_with_appliances()
            
            prompt = self.prompt.load("09_batch_appliance_decision",
                member_name=member_name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_habits=member.habits,
                member_timeline=json.dumps(member_timeline, ensure_ascii=False, indent=2),
                home_structure_with_appliances=json.dumps(home_structure_with_appliances, ensure_ascii=False, indent=2),
                season=season,
                weather=weather,
                temperature=temperature
            )
            
            prompts.append(prompt)
            members_data.append((member_name, member))
        
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=True)
        
        for (member_name, member), prompt, result in zip(members_data, prompts, results):
            tokens = SubAgent.get_tokens()
            log_name = f"09_第九层_批量用电决策_{member_name}"
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            self._save_log(log_name, prompt, result_content, tokens, reasoning_content)
            
            try:
                decision_data = json.loads(result_content)
                
                json_filename = f"09_第九层_批量用电决策_{member_name}.json"
                json_filepath = os.path.join(self.log_dir, json_filename)
                with open(json_filepath, "w", encoding="utf-8") as f:
                    json.dump(decision_data, f, ensure_ascii=False, indent=2)
                
                print(f"已生成 {member_name} 的用电决策")
            except Exception as e:
                print(f"解析 {member_name} 的用电决策失败: {e}")
        
        return None
    
    def _get_home_structure_with_appliances(self):
        structure = {}
        for room_name, room in self.home.rooms.items():
            structure[room_name] = {
                "appliances": [appliance.to_dict() for appliance in room.appliances]
            }
        return structure
    
    def _get_member(self, name):
        for member in self.home.members:
            if member.name == name:
                return member
        return None
    
    def _save_log(self, stage_name, prompt, response, tokens=None, reasoning_content=""):
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
            
            if reasoning_content:
                f.write("## 思考过程\n\n")
                f.write("```\n")
                f.write(reasoning_content)
                f.write("\n```\n\n")
                f.write("---\n\n")
            
            f.write("## LLM返回结果\n\n")
            f.write("```json\n")
            try:
                response_obj = json.loads(response)
                formatted_response = format_json_compact(response_obj)
                f.write(formatted_response)
            except:
                f.write(response)
            f.write("\n```\n")

