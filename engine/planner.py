import json
import os
from datetime import datetime
from .prompt import Prompt
from .subagent import SubAgent
from .timeline import Timeline, visualize_timelines

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

class Planner:
    def __init__(self, home, run_id=None, date_str=None):
        self.home = home
        self.timelines = {}
        self.prompt = Prompt()
        
        os.makedirs("logs", exist_ok=True)
        
        if run_id and date_str:
            run_dir = os.path.join("logs", f"{run_id}_logs")
            os.makedirs(run_dir, exist_ok=True)
            self.log_dir = os.path.join(run_dir, date_str)
        else:
            self.log_dir = os.path.join("logs", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def generate_plans(self, time_obj):
        home_structure = self.home.get_home_structure()
        members_info = self.home.get_members_info()
        
        date = time_obj.get_date_string()
        day_type = time_obj.day_type
        time_context = time_obj.get_prompt_string()
        
        prompts = []
        members = []
        
        for member in self.home.members:
            prompt = self.prompt.load("01_macro_plan",
                member_name=member.name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_personality=member.personality,
                date=date,
                day_type=day_type,
                time_context=time_context,
                home_structure=json.dumps(home_structure, ensure_ascii=False, indent=2),
                members_info=json.dumps(members_info, ensure_ascii=False, indent=2)
            )
            prompts.append(prompt)
            members.append(member)
        
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=True)
        
        for member, prompt, result in zip(members, prompts, results):
            tokens = SubAgent.get_tokens()
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            self._save_log(f"01_第一层_宏观计划_{member.name}", prompt, result_content, tokens, reasoning_content)
            
            try:
                plan_data = json.loads(result_content)
                timeline = Timeline(member.name)
                timeline.load_from_activities(plan_data.get("activities", []))
                self.timelines[member.name] = timeline
            except:
                print(f"解析{member.name}的计划失败")
        
        return self.timelines
    
    def coordinate_timelines_progressively(self):
        member_names = list(self.timelines.keys())
        
        if len(member_names) <= 1:
            print("只有一个成员，无需协调")
            return self.timelines
        
        print(f"\n开始渐进式协调，基准成员：{member_names[0]}")
        
        for i in range(1, len(member_names)):
            current_member = member_names[i]
            coordinated_members = member_names[:i]
            
            print(f"\n协调 {current_member} 与 {coordinated_members}")
            
            coordinated_timelines_text = ""
            for name in coordinated_members:
                timeline = self.timelines[name]
                coordinated_timelines_text += f"\n{name}的时间线：\n"
                for slot in timeline.slots:
                    coordinated_timelines_text += f"  {slot._format_time_range()}: {slot.location} - {slot.activity}\n"
            
            current_timeline = self.timelines[current_member]
            current_timeline_text = f"\n{current_member}的原始时间线：\n"
            for slot in current_timeline.slots:
                current_timeline_text += f"  {slot._format_time_range()}: {slot.location} - {slot.activity}\n"
            
            member = self._get_member(current_member)
            
            prompt = self.prompt.load("02_progressive_coordination",
                current_member_name=current_member,
                current_member_age=member.age,
                current_member_occupation=member.occupation,
                current_member_personality=member.personality,
                coordinated_members=", ".join(coordinated_members),
                coordinated_timelines=coordinated_timelines_text,
                current_timeline=current_timeline_text
            )
            
            result = SubAgent.single_call(prompt, json_mode=True, thinking=True)
            tokens = SubAgent.get_tokens()
            
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            self._save_log(f"02_第二层_渐进协调_{i}_{current_member}", prompt, result_content, tokens, reasoning_content)
            
            try:
                coordination_data = json.loads(result_content)
                new_activities = coordination_data.get("coordinated_activities", [])
                
                new_timeline = Timeline(current_member)
                new_timeline.load_from_activities(new_activities)
                self.timelines[current_member] = new_timeline
                
                print(f"已协调 {current_member} 的时间线")
            except Exception as e:
                print(f"解析 {current_member} 的协调结果失败: {e}")
        
        return self.timelines
    
    def visualize_plans(self, stage_name="时间线"):
        timelines_list = list(self.timelines.values())
        output_path = f"{self.log_dir}/{stage_name}_可视化.png"
        visualize_timelines(timelines_list, output_path, f"家庭成员{stage_name}")
    
    def enrich_activities(self, season="夏天", weather="晴天", temperature=28):
        prompts = []
        members = []
        
        for member_name, timeline in self.timelines.items():
            member = self._get_member(member_name)
            if not member:
                continue
            
            member_timeline = timeline.to_dict()["activities"]
            
            other_timelines = {}
            for other_name, other_timeline in self.timelines.items():
                if other_name != member_name:
                    other_timelines[other_name] = other_timeline.to_dict()["activities"]
            
            prompt = self.prompt.load("03_enrich_activities",
                member_name=member_name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_personality=member.personality,
                member_timeline=json.dumps(member_timeline, ensure_ascii=False, indent=2),
                other_members_timelines=json.dumps(other_timelines, ensure_ascii=False, indent=2),
                home_structure=json.dumps(self.home.get_home_structure(), ensure_ascii=False, indent=2),
                season=season,
                weather=weather,
                temperature=temperature
            )
            
            prompts.append(prompt)
            members.append((member_name, timeline))
        
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=True)
        
        for (member_name, timeline), prompt, result in zip(members, prompts, results):
            tokens = SubAgent.get_tokens()
            log_name = f"03_第三层_丰富行为描述_{member_name}"
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            self._save_log(log_name, prompt, result_content, tokens, reasoning_content)
            
            try:
                enriched_data = json.loads(result_content)
                enriched_activities = enriched_data.get("enriched_activities", [])
                
                for i, slot in enumerate(timeline.slots):
                    if i < len(enriched_activities):
                        slot.desc = enriched_activities[i].get("desc", "")
                
                print(f"已丰富 {member_name} 的行为描述")
            except Exception as e:
                print(f"解析 {member_name} 的丰富描述失败: {e}")
        
        return self.timelines
    
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
        
        print(f"日志已保存: {log_file}")
