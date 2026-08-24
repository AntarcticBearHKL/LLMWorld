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
                 memory_context="", policy_name="baseline", news_context="", env_id=None):
        self.home = home
        self.timelines = {}
        self.prompt = Prompt()
        self.memory_context = memory_context
        self.policy_name = policy_name
        self.news_context = news_context

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        simulation_dir = os.path.join(project_root, "simulation")
        os.makedirs(simulation_dir, exist_ok=True)

        if env_id and world_id and postcode and house_id and date_str:
            # New structure: simulation/<env>/<date>/<postcode>/<house_id>/
            self.log_dir = os.path.join(simulation_dir, env_id, date_str, postcode, house_id)
        elif world_id and postcode and house_id and date_str:
            self.log_dir = os.path.join(simulation_dir, world_id, postcode, house_id,
                                        self.policy_name, date_str)
        else:
            self.log_dir = os.path.join(simulation_dir, f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.log_dir, exist_ok=True)



    def generate_plans(self, time_obj, community_notice=""):
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
                memory_context=self.memory_context,
                world_news=self.news_context,
                community_notice=community_notice
            )
            prompts.append(prompt)
            members.append(member)

        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=config.THINKING)

        for member, prompt, result in zip(members, prompts, results):
            tokens = SubAgent.get_tokens()
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, f"01_layer1_macro_plan_{member.name}", prompt, result_content, tokens, reasoning_content)

            try:
                plan_data = utils.parse_json_with_retry(prompt, result_content, json_mode=True, thinking=config.THINKING)
                timeline = Timeline(member.name)
                timeline.load_from_activities(plan_data.get("activities", []))
                self.timelines[member.name] = timeline
            except Exception as e:
                print(f"[Error] Failed to parse {member.name}'s plan: {e}")

        return self.timelines



    def coordinate_timelines_progressively(self):
        member_names = list(self.timelines.keys())

        if len(member_names) <= 1:
            print("Only one member, no coordination needed")
            return self.timelines

        print(f"\nStarting progressive coordination, baseline member: {member_names[0]}")

        exclusive_resources = self.home.get_exclusive_resources()
        exclusive_info = ""
        if exclusive_resources:
            exclusive_info = "\n\n## Household Exclusive Resources\n\n"
            for resource in exclusive_resources:
                exclusive_info += f"### {resource['name']}\n"
                exclusive_info += f"- Location: {resource.get('location', 'home')}\n"
                if resource.get('owner'):
                    exclusive_info += f"- Owner: {resource['owner']}\n"
                exclusive_info += "- Usage rules:\n"
                for rule in resource['rules']:
                    exclusive_info += f"  - {rule}\n"
                exclusive_info += "\n"

        for i in range(1, len(member_names)):
            current_member = member_names[i]
            coordinated_members = member_names[:i]

            print(f"\nCoordinating {current_member} with {coordinated_members}")

            coordinated_timelines_text = ""
            for name in coordinated_members:
                timeline = self.timelines[name]
                coordinated_timelines_text += f"\n{name}'s timeline:\n"
                for slot in timeline.slots:
                    coordinated_timelines_text += f"  {slot._format_time_range()}: {slot.location} - {slot.activity}\n"

            current_timeline = self.timelines[current_member]
            current_timeline_text = f"\n{current_member}'s original timeline:\n"
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
                    "## Exclusive resource constraints",
                    exclusive_info + "\n## Coordination requirements"
                )

            result = SubAgent.single_call(prompt_content, json_mode=True, thinking=config.THINKING)
            tokens = SubAgent.get_tokens()

            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, f"02_layer2_progressive_coordination_{i}_{current_member}", prompt_content, result_content, tokens, reasoning_content)

            try:
                coordination_data = utils.parse_json_with_retry(prompt_content, result_content, json_mode=True, thinking=config.THINKING)
                new_activities = coordination_data.get("coordinated_activities", [])

                new_timeline = Timeline(current_member)
                new_timeline.load_from_activities(new_activities)
                self.timelines[current_member] = new_timeline

                print(f"Coordinated {current_member}'s timeline")
            except Exception as e:
                print(f"Failed to parse coordination result for {current_member}: {e}")

        return self.timelines



    def enrich_activities(self, season="Summer", weather="Sunny", temperature=28):
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
            log_name = f"03_layer3_enrich_behavior_{member_name}"
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, log_name, prompt, result_content, tokens, reasoning_content)

            try:
                enriched_data = utils.parse_json_with_retry(prompt, result_content, json_mode=True, thinking=config.THINKING)
                enriched_activities = enriched_data.get("enriched_activities", [])

                for i, slot in enumerate(timeline.slots):
                    if i < len(enriched_activities):
                        slot.desc = enriched_activities[i].get("desc", "")

                print(f"Enriched {member_name}'s behavior description")
            except Exception as e:
                print(f"Failed to parse enrichment for {member_name}: {e}")

        return self.timelines



    def _get_member(self, name):
        for member in self.home.members:
            if member.name == name:
                return member
        return None
