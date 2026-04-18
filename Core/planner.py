import json
import os
from datetime import datetime
from Engine import Agent

class Planner:
    def __init__(self, llm_provider, home):
        self.llm = llm_provider
        self.home = home
        self.macro_plans = {}
        self.interactions = []
        self.time_segments = {}
        self.logs = []
        
        os.makedirs("output", exist_ok=True)
        self.log_dir = os.path.join("output", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def generate_macro_plan(self, member, date, day_type="工作日"):
        prompt = f"""你是一个家庭生活规划专家。请为以下家庭成员生成一天的宏观活动计划。

家庭成员信息：
- 姓名：{member.name}
- 年龄：{member.age}岁
- 职业：{member.occupation}
- 性格：{member.personality}

日期：{date}（{day_type}）

请生成该成员从00:00到23:59一整天的活动安排，要求：
- 只描述做什么活动，不涉及具体地点和家电
- 时间段颗粒度最低为10分钟，但是可以是以10分钟为单位的时间段
- 符合角色特征和日常规律
- 必须从00:00开始，覆盖完整的24小时
- 包含这个角色所有可能的日常活动
- 本项目只统计在家中的活动，因此如果当前时间段角色不在家中，那么应该写外出

输出JSON格式：
{{
  "member": "{member.name}",
  "activities": [
    {{"time": "...", "activity": "..."}},
    {{"time": "...", "activity": "..."}},
    ...
  ]
}}"""
        
        agent = Agent(f"{member.name}计划生成", self.llm)
        agent.add_input(prompt)
        result = agent.think()
        
        self._save_log(f"第一层_宏观计划_{member.name}", prompt, result.raw)
        
        try:
            plan_data = json.loads(result.raw)
            self.macro_plans[member.name] = plan_data
            return plan_data
        except:
            print(f"解析{member.name}的计划失败")
            return None
    
    def generate_all_plans(self, date, day_type="工作日"):
        for member in self.home.members:
            self.generate_macro_plan(member, date, day_type)
        
        home_structure = self.home.to_json()
        self._save_log("家庭结构", "家庭房间和电器配置", json.dumps(home_structure, ensure_ascii=False, indent=2))
        
        return self.macro_plans
    
    def analyze_interactions(self):
        plans_text = ""
        for name, plan in self.macro_plans.items():
            plans_text += f"\n{name}的计划：\n"
            for activity in plan.get("activities", []):
                plans_text += f"  {activity['time']}: {activity['activity']}\n"
        
        prompt = f"""你是一个家庭互动场景编剧。以下是一个家庭成员的宏观计划，请分析他们的互动。

{plans_text}

请找出所有时间段的交集，对每个交集生成互动场景，包括：
1. 参与者
2. 活动内容
3. 互动过程
4. 最终结果（谁在哪里做什么，持续多久）

要求：
- 互动要自然合理
- 考虑家庭关系和角色
- 如有冲突，给出协商过程和结果

输出JSON格式：
{{
  "interactions": [
    {{
      "time": "时间段",
      "participants": ["参与者1", "参与者2"],
      "type": "互动类型",
      "content": "互动内容描述",
      "result": {{
        "location": "地点",
        "details": "详细描述"
      }}
    }}
  ]
}}"""
        
        agent = Agent("互动分析", self.llm)
        agent.add_input(prompt)
        result = agent.think()
        
        self._save_log("第二层_互动分析", prompt, result.raw)
        
        try:
            interaction_data = json.loads(result.raw)
            self.interactions = interaction_data.get("interactions", [])
            return self.interactions
        except:
            print("解析互动失败")
            return []
    
    def decompose_to_segments(self):
        for name, plan in self.macro_plans.items():
            segments = []
            for activity in plan.get("activities", []):
                time_range = activity["time"]
                activity_desc = activity["activity"]
                
                location = self._infer_location(activity_desc)
                
                segments.append({
                    "time": time_range,
                    "location": location,
                    "activity": activity_desc
                })
            
            self.time_segments[name] = segments
        
        self._apply_interactions()
        
        segments_summary = json.dumps(self.time_segments, ensure_ascii=False, indent=2)
        self._save_log("第三层_时间段分解", "基于宏观计划和互动结果分解时间段", segments_summary)
        
        return self.time_segments
    
    def _infer_location(self, activity):
        if any(word in activity for word in ["出门", "上班", "上学", "外出", "公司", "学校", "商场", "超市"]):
            return "外出"
        elif any(word in activity for word in ["做饭", "准备餐", "厨房"]):
            return "厨房"
        elif any(word in activity for word in ["看电视", "吃饭", "客厅"]):
            return "客厅"
        elif any(word in activity for word in ["睡觉", "午休", "卧室"]):
            return "卧室"
        elif any(word in activity for word in ["洗漱", "洗澡", "卫生间"]):
            return "卫生间"
        else:
            return "客厅"
    
    def _apply_interactions(self):
        for interaction in self.interactions:
            time = interaction["time"]
            location = interaction["result"]["location"]
            
            for participant in interaction["participants"]:
                if participant in self.time_segments:
                    for segment in self.time_segments[participant]:
                        if segment["time"] == time:
                            segment["location"] = location
                            segment["interaction"] = interaction["content"]
    
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
        
        print(f"日志已保存: {log_file}")
