"""计划器：前三层 —— 宏观计划、渐进式协调、丰富行为描述。

职责：
1. 第一层：每个成员生成全天宏观活动计划（并行 LLM 调用）
2. 第二层：逐个成员协调时间线，解决家庭独占资源冲突
3. 第三层：结合季节/天气/温度丰富行为描述
"""

import json
import os
from datetime import datetime

from . import utils
from .prompt import Prompt
from .subagent import SubAgent
import config
from .timeline import Timeline


class Planner:
    def __init__(self, home, world_id=None, postcode=None, house_id=None, date_str=None,
                 memory_context=""):
        self.home = home
        self.timelines = {}
        self.prompt = Prompt()
        self.memory_context = memory_context   # 跨天记忆文本（可为空）

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        if world_id and postcode and house_id and date_str:
            self.log_dir = os.path.join(outputs_dir, world_id, postcode, house_id, date_str)
        else:
            self.log_dir = os.path.join(outputs_dir, f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.log_dir, exist_ok=True)

    # ---------- 第一层：宏观计划 ----------

    def generate_plans(self, time_obj):
        home_structure = self.home.get_home_structure()
        members_info = self.home.get_members_info()

        date = time_obj.get_date_string()
        day_type = time_obj.day_type
        time_context = time_obj.get_prompt_string()

        prompts = []
        members = []

        for member in self.home.members:
            prompt = self.prompt.load("simulate_step1_macro_plan",
                member_name=member.name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_personality=member.personality,
                date=date,
                day_type=day_type,
                time_context=time_context,
                home_structure=json.dumps(home_structure, ensure_ascii=False, indent=2),
                members_info=json.dumps(members_info, ensure_ascii=False, indent=2),
                memory_context=self.memory_context
            )
            prompts.append(prompt)
            members.append(member)

        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=config.THINKING)

        for member, prompt, result in zip(members, prompts, results):
            tokens = SubAgent.get_tokens()
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, f"01_第一层_宏观计划_{member.name}", prompt, result_content, tokens, reasoning_content)

            try:
                plan_data = utils.parse_json_with_retry(prompt, result_content, json_mode=True, thinking=config.THINKING)
                timeline = Timeline(member.name)
                timeline.load_from_activities(plan_data.get("activities", []))
                self.timelines[member.name] = timeline
            except Exception as e:
                print(f"[错误] 解析{member.name}的计划失败: {e}")

        return self.timelines

    # ---------- 第二层：渐进式协调 ----------

    def coordinate_timelines_progressively(self):
        member_names = list(self.timelines.keys())

        if len(member_names) <= 1:
            print("只有一个成员，无需协调")
            return self.timelines

        print(f"\n开始渐进式协调，基准成员：{member_names[0]}")

        exclusive_resources = self.home.get_exclusive_resources()
        exclusive_info = ""
        if exclusive_resources:
            exclusive_info = "\n\n## 家庭独占资源\n\n"
            for resource in exclusive_resources:
                exclusive_info += f"### {resource['name']}\n"
                exclusive_info += f"- 位置：{resource.get('location', '家中')}\n"
                if resource.get('owner'):
                    exclusive_info += f"- 所有者：{resource['owner']}\n"
                exclusive_info += "- 使用规则：\n"
                for rule in resource['rules']:
                    exclusive_info += f"  - {rule}\n"
                exclusive_info += "\n"

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

            prompt_content = self.prompt.load("simulate_step2_progressive_coordination",
                current_member_name=current_member,
                current_member_age=member.age,
                current_member_occupation=member.occupation,
                current_member_personality=member.personality,
                coordinated_members=", ".join(coordinated_members),
                coordinated_timelines=coordinated_timelines_text,
                current_timeline=current_timeline_text
            )

            if exclusive_resources:
                prompt_content = prompt_content.replace(
                    "## 独占资源约束",
                    exclusive_info + "\n## 协调要求"
                )

            result = SubAgent.single_call(prompt_content, json_mode=True, thinking=config.THINKING)
            tokens = SubAgent.get_tokens()

            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, f"02_第二层_渐进协调_{i}_{current_member}", prompt_content, result_content, tokens, reasoning_content)

            try:
                coordination_data = utils.parse_json_with_retry(prompt_content, result_content, json_mode=True, thinking=config.THINKING)
                new_activities = coordination_data.get("coordinated_activities", [])

                new_timeline = Timeline(current_member)
                new_timeline.load_from_activities(new_activities)
                self.timelines[current_member] = new_timeline

                print(f"已协调 {current_member} 的时间线")
            except Exception as e:
                print(f"解析 {current_member} 的协调结果失败: {e}")

        return self.timelines

    # ---------- 第三层：丰富行为描述 ----------

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

            prompt = self.prompt.load("simulate_step3_enrich_activities",
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

        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=config.THINKING)

        for (member_name, timeline), prompt, result in zip(members, prompts, results):
            tokens = SubAgent.get_tokens()
            log_name = f"03_第三层_丰富行为描述_{member_name}"
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, log_name, prompt, result_content, tokens, reasoning_content)

            try:
                enriched_data = utils.parse_json_with_retry(prompt, result_content, json_mode=True, thinking=config.THINKING)
                enriched_activities = enriched_data.get("enriched_activities", [])

                for i, slot in enumerate(timeline.slots):
                    if i < len(enriched_activities):
                        slot.desc = enriched_activities[i].get("desc", "")

                print(f"已丰富 {member_name} 的行为描述")
            except Exception as e:
                print(f"解析 {member_name} 的丰富描述失败: {e}")

        return self.timelines

    # ---------- 辅助 ----------

    def _get_member(self, name):
        for member in self.home.members:
            if member.name == name:
                return member
        return None



