import json
import os
from datetime import datetime
from .prompt import Prompt
from .subagent import SubAgent
from .timeline import Timeline, visualize_timelines

class Planner:
    def __init__(self, home, run_id=None, date_str=None):
        self.home = home
        self.macro_plans = {}
        self.coordinations = []
        self.timelines = {}
        self.logs = []
        self.prompt = Prompt()
        self.adjustment_iteration = 0
        self.verification_iteration = 0
        
        os.makedirs("output", exist_ok=True)
        
        if run_id and date_str:
            run_dir = os.path.join("output", f"{run_id}_logs")
            os.makedirs(run_dir, exist_ok=True)
            self.log_dir = os.path.join(run_dir, date_str)
        else:
            self.log_dir = os.path.join("output", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
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
            prompt = self.prompt.load("macro_plan",
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
        
        from .subagent import SubAgent
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=False)
        
        for idx, (member, prompt, result) in enumerate(zip(members, prompts, results)):
            tokens = SubAgent.get_tokens()
            self._save_log(f"01_第一层_宏观计划_{member.name}", prompt, result, tokens)
            
            try:
                plan_data = json.loads(result)
                self.macro_plans[member.name] = plan_data
                
                timeline = Timeline(member.name)
                timeline.load_from_activities(plan_data.get("activities", []))
                self.timelines[member.name] = timeline
                
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
        
        if not self.coordinations:
            print("没有需要协调的场景，跳过调整")
            return self.timelines
        
        for member_name, timeline in self.timelines.items():
            member_coordinations = []
            for coord in self.coordinations:
                participants = coord.get("participants", {})
                if member_name in participants:
                    unified_time = coord.get("unified_time", "")
                    unified_location = coord.get("unified_location", "")
                    activity = participants.get(member_name, "")
                    
                    try:
                        timeline.update_slot(unified_time, unified_location, activity)
                        
                        member_coordinations.append({
                            "coordination_id": coord.get("coordination_id", ""),
                            "type": coord.get("type", ""),
                            "unified_time": unified_time,
                            "unified_location": unified_location,
                            "activity": activity
                        })
                    except Exception as e:
                        print(f"[错误] {member_name} 插入协调事件失败: {e}")
                        print(f"[跳过] 协调事件: {unified_time} - {activity}")
                        continue
            
            if member_coordinations:
                log_name = f"03_第三层_代码强制插入_第{self.adjustment_iteration}次_{member_name}"
                self._save_log(log_name, 
                    f"协调要求:\n{json.dumps(member_coordinations, ensure_ascii=False, indent=2)}", 
                    timeline.to_json(), 
                    None)
                print(f"已强制插入 {member_name} 的协调时间段（第{self.adjustment_iteration}次）")
        
        return self.timelines
    
    def fill_empty_slots(self):
        prompts = []
        members_data = []
        
        for member_name, timeline in self.timelines.items():
            empty_slots = timeline.get_empty_slots_formatted()
            
            if not empty_slots:
                print(f"{member_name} 没有空余时间段")
                continue
            
            member = self._get_member(member_name)
            if not member:
                continue
            
            current_activities = timeline.to_dict()["activities"]
            
            prompt = self.prompt.load("fill_empty_slots",
                member_name=member_name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_personality=member.personality,
                current_activities=json.dumps(current_activities, ensure_ascii=False, indent=2),
                empty_slots=json.dumps(empty_slots, ensure_ascii=False, indent=2)
            )
            
            prompts.append(prompt)
            members_data.append((member_name, timeline))
        
        if not prompts:
            return self.timelines
        
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=False)
        
        for (member_name, timeline), prompt, result in zip(members_data, prompts, results):
            tokens = SubAgent.get_tokens()
            log_name = f"04_第四层_填充空余时间_{member_name}"
            self._save_log(log_name, prompt, result, tokens)
            
            try:
                fill_data = json.loads(result)
                fill_activities = fill_data.get("fill_activities", [])
                
                for activity in fill_activities:
                    time_range = activity["time"]
                    location = activity.get("location", "")
                    activity_desc = activity["activity"]
                    timeline.insert_slot(time_range, location, activity_desc, force=False)
                
                print(f"已填充 {member_name} 的空余时间段")
            except:
                print(f"解析 {member_name} 的填充活动失败")
        
        return self.timelines
    
    def verify_coordinations(self):
        self.verification_iteration += 1
        
        plans_text = ""
        for name, timeline in self.timelines.items():
            plans_text += f"\n{name}的计划：\n"
            for slot in timeline.slots:
                plans_text += f"  {slot._format_time_range()}: {slot.location} - {slot.activity}\n"
        
        prompt = self.prompt.load("coordination_verification", plans_text=plans_text)
        
        result = SubAgent.single_call(prompt, json_mode=True, thinking=False)
        tokens = SubAgent.get_tokens()
        
        log_name = f"05_第五层_协调验证_第{self.verification_iteration}次"
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
        for member_name, timeline in self.timelines.items():
            self._save_log(f"06_第六层_最终计划_{member_name}", "经过所有协调后的最终计划", timeline.to_json(), None)
        
        return self.timelines
    
    def visualize_plans(self, stage_name="最终计划"):
        timelines_list = list(self.timelines.values())
        output_path = f"{self.log_dir}/{stage_name}_可视化.png"
        visualize_timelines(timelines_list, output_path, f"家庭成员{stage_name}")
    
    def decompose_to_segments(self):
        time_segments = {}
        for name, timeline in self.timelines.items():
            segments = []
            for slot in timeline.slots:
                segment = {
                    "time": slot._format_time_range(),
                    "location": slot.location,
                    "activity": slot.activity
                }
                if slot.desc:
                    segment["desc"] = slot.desc
                segments.append(segment)
            time_segments[name] = segments
        
        segments_summary = json.dumps(time_segments, ensure_ascii=False, indent=2)
        self._save_log("07_第七层_时间段分解", "基于最终计划生成时间段", segments_summary, None)
        
        return time_segments
    
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
            
            prompt = self.prompt.load("enrich_activities",
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
        
        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=False)
        
        for (member_name, timeline), prompt, result in zip(members, prompts, results):
            tokens = SubAgent.get_tokens()
            log_name = f"08_第八层_丰富行为描述_{member_name}"
            self._save_log(log_name, prompt, result, tokens)
            
            try:
                enriched_data = json.loads(result)
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
