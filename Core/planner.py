import json
import os
from datetime import datetime
from .prompt import Prompt
from .subagent import SubAgent

class Planner:
    def __init__(self, home):
        self.home = home
        self.macro_plans = {}
        self.coordinations = []
        self.decomposed_plans = {}
        self.time_segments = {}
        self.logs = []
        self.prompt = Prompt()
        self.adjustment_iteration = 0
        self.verification_iteration = 0
        
        os.makedirs("output", exist_ok=True)
        self.log_dir = os.path.join("output", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def generate_plans(self, date, day_type="工作日"):
        home_structure = self.home.get_home_structure()
        members_info = self.home.get_members_info()
        
        prompts = []
        members = []
        
        for member in self.home.members:
            prompt = self.prompt.load("macro_plan",
                member_name=member.name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_personality=member.personality,
                date=date,
                day_type=day_type,
                home_structure=json.dumps(home_structure, ensure_ascii=False, indent=2),
                members_info=json.dumps(members_info, ensure_ascii=False, indent=2)
            )
            prompts.append(prompt)
            members.append(member)
        
        from .subagent import SubAgent
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=False)
        
        for idx, (member, prompt, result) in enumerate(zip(members, prompts, results)):
            tokens = SubAgent.get_tokens()
            self._save_log(f"01_第一层_宏观计划_{member.name}", prompt, result, tokens)
            
            try:
                plan_data = json.loads(result)
                self.macro_plans[member.name] = plan_data
            except:
                print(f"解析{member.name}的计划失败")
        
        return self.macro_plans
    
    def analyze_interactions(self):
        plans_text = ""
        for name, plan in self.macro_plans.items():
            plans_text += f"\n{name}的计划：\n"
            for activity in plan.get("activities", []):
                time_str = activity['time']
                location = activity.get('location', '')
                activity_desc = activity['activity']
                plans_text += f"  {time_str}: {location} - {activity_desc}\n"
        
        prompt = self.prompt.load("interaction_analysis", plans_text=plans_text)
        
        result = SubAgent.single_call(prompt, json_mode=True, thinking=False)
        tokens = SubAgent.get_tokens()
        
        self._save_log("02_第二层_协调识别", prompt, result, tokens)
        
        try:
            coordination_data = json.loads(result)
            self.coordinations = coordination_data.get("coordinations", [])
            return self.coordinations
        except:
            print("解析协调场景失败")
            return []
    
    def adjust_timelines(self):
        self.adjustment_iteration += 1
        
        for member_name in self.macro_plans.keys():
            self.decomposed_plans[member_name] = {
                "member": member_name,
                "activities": self.macro_plans[member_name].get("activities", [])
            }
        
        if not self.coordinations:
            print("没有需要协调的场景，跳过调整")
            return self.decomposed_plans
        
        coordinations_str = json.dumps(self.coordinations, ensure_ascii=False, indent=2)
        
        for member_name in self.decomposed_plans.keys():
            current_timeline = self.decomposed_plans[member_name].get("activities", [])
            current_timeline_str = json.dumps(current_timeline, ensure_ascii=False, indent=2)
            
            member_coordinations = []
            for coord in self.coordinations:
                participants = coord.get("participants", {})
                if member_name in participants:
                    member_coord = {
                        "coordination_id": coord.get("coordination_id", ""),
                        "type": coord.get("type", ""),
                        "unified_time": coord.get("unified_time", ""),
                        "unified_location": coord.get("unified_location", ""),
                        "your_activity": participants.get(member_name, ""),
                        "other_participants": [p for p in participants.keys() if p != member_name],
                        "reason": coord.get("reason", "")
                    }
                    member_coordinations.append(member_coord)
            
            if not member_coordinations:
                print(f"{member_name} 没有参与任何协调，保持原计划")
                continue
            
            coordinations_for_member = json.dumps(member_coordinations, ensure_ascii=False, indent=2)
            
            prompt = self.prompt.load("timeline_adjustment",
                member_name=member_name,
                current_timeline=current_timeline_str,
                coordinations=coordinations_for_member
            )
            
            result = SubAgent.single_call(prompt, json_mode=True, thinking=False)
            tokens = SubAgent.get_tokens()
            
            log_name = f"03_第三层_批量调整_第{self.adjustment_iteration}次_{member_name}"
            self._save_log(log_name, prompt, result, tokens)
            
            try:
                adjusted_timeline = json.loads(result)
                self.decomposed_plans[member_name] = adjusted_timeline
                print(f"已调整 {member_name} 的时间线（第{self.adjustment_iteration}次）")
            except:
                print(f"解析 {member_name} 的调整失败（第{self.adjustment_iteration}次）")
        
        return self.decomposed_plans
    
    def verify_coordinations(self):
        self.verification_iteration += 1
        
        plans_text = ""
        for name, plan in self.decomposed_plans.items():
            plans_text += f"\n{name}的计划：\n"
            for activity in plan.get("activities", []):
                time_str = activity['time']
                location = activity.get('location', '')
                activity_desc = activity['activity']
                plans_text += f"  {time_str}: {location} - {activity_desc}\n"
        
        prompt = self.prompt.load("coordination_verification", plans_text=plans_text)
        
        result = SubAgent.single_call(prompt, json_mode=True, thinking=False)
        tokens = SubAgent.get_tokens()
        
        log_name = f"04_第四层_协调验证_第{self.verification_iteration}次"
        self._save_log(log_name, prompt, result, tokens)
        
        try:
            verification_data = json.loads(result)
            new_coordinations = verification_data.get("coordinations", [])
            
            if not new_coordinations:
                print(f"验证通过（第{self.verification_iteration}次），没有发现新的协调问题")
                return False
            else:
                print(f"发现 {len(new_coordinations)} 个新的协调问题（第{self.verification_iteration}次），需要重新调整")
                self.coordinations = new_coordinations
                return True
        except:
            print(f"解析验证结果失败（第{self.verification_iteration}次）")
            return False
    
    def save_final_plans(self):
        for member_name, plan in self.decomposed_plans.items():
            member_summary = json.dumps(plan, ensure_ascii=False, indent=2)
            self._save_log(f"05_第五层_最终计划_{member_name}", "经过所有协调后的最终计划", member_summary, None)
        
        return self.decomposed_plans
    
    def decompose_to_segments(self):
        for name, plan in self.decomposed_plans.items():
            segments = []
            for activity in plan.get("activities", []):
                time_range = activity["time"]
                location = activity.get("location", "")
                activity_desc = activity["activity"]
                
                segment = {
                    "time": time_range,
                    "location": location,
                    "activity": activity_desc
                }
                
                segments.append(segment)
            
            self.time_segments[name] = segments
        
        segments_summary = json.dumps(self.time_segments, ensure_ascii=False, indent=2)
        self._save_log("06_第六层_时间段分解", "基于最终计划生成时间段", segments_summary, None)
        
        return self.time_segments
    
    def _get_member(self, name):
        for member in self.home.members:
            if member.name == name:
                return member
        return None
    
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
        
        print(f"日志已保存: {log_file}")
