import json
import os

from . import utils
from .prompt import Prompt
from .subagent import SubAgent
import config


class Executor:
    def __init__(self, home, planner, policy_context="", news_context=""):
        self.home = home
        self.planner = planner
        self.log_dir = planner.log_dir
        self.prompt = Prompt()
        self.policy_context = policy_context
        self.news_context = news_context
        self.validation_warnings = []

    def execute_all_segments(self, season="Summer", weather="Sunny", temperature=28):
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

            home_structure_with_appliances = self._get_home_structure_with_appliances(member)

            prompt = self.prompt.load("simulate_step4_batch_appliance_decision",
                member_name=member_name,
                member_age=member.age,
                member_occupation=member.occupation,
                member_habits=member.habits,
                member_timeline=json.dumps(member_timeline, ensure_ascii=False, indent=2),
                home_structure_with_appliances=json.dumps(home_structure_with_appliances, ensure_ascii=False, indent=2),
                season=season,
                weather=weather,
                temperature=temperature,
                policy_context=self.policy_context,
                world_news=self.news_context
            )

            prompts.append(prompt)
            members_data.append((member_name, member))

        results = SubAgent.parallel_call(prompts, json_mode=True, thinking=config.THINKING)

        for (member_name, member), prompt, result in zip(members_data, prompts, results):
            tokens = SubAgent.get_tokens()
            log_name = f"04_layer4_batch_appliance_decision_{member_name}"
            result_content = result["content"] if isinstance(result, dict) else result
            reasoning_content = result.get("reasoning_content", "") if isinstance(result, dict) else ""
            utils.save_log(self.log_dir, log_name, prompt, result_content, tokens, reasoning_content)

            try:
                decision_data = utils.parse_json_with_retry(prompt, result_content, json_mode=True, thinking=config.THINKING)
            except Exception as e:
                self.validation_warnings.append(f"[Parse failed] {member_name}'s appliance decision is not valid JSON: {e}")
                print(f"[Error] Failed to parse {member_name}'s appliance decision: {e} (this member's appliance decisions for today are missing)")
                continue


            member_warnings = []
            total_energy = self._calculate_member_energy_consumption(member, decision_data, member_warnings)
            decision_data["total_energy_kwh"] = total_energy
            decision_data["validation_warnings"] = member_warnings
            self.validation_warnings.extend(member_warnings)

            json_filename = f"04_layer4_batch_appliance_decision_{member_name}.json"
            json_filepath = os.path.join(self.log_dir, json_filename)
            with open(json_filepath, "w", encoding="utf-8") as f:
                json.dump(decision_data, f, ensure_ascii=False, indent=2)

            print(f"Generated {member_name}'s appliance decisions, total energy: {total_energy:.3f} kWh"
                  + (f", {len(member_warnings)} validation warnings" if member_warnings else ""))

        return None

    def _calculate_member_energy_consumption(self, member, decision_data, warnings):

        total_energy = 0
        cleaned_decisions = utils.validate_appliance_decisions(decision_data, self.home, warnings)

        for decision in cleaned_decisions:
            start_minutes = decision["start_minutes"]
            end_minutes = decision["end_minutes"]
            location = decision["location"]

            for operation in decision["operations"]:
                appliance_id = operation["unique_id"]
                action = operation["action"]

                appliance = self.home.get_appliance(appliance_id)
                if not appliance:
                    continue

                if action not in ["use", "charge_home"]:
                    continue

                energy = appliance.calculate_energy(start_minutes, end_minutes, power_source="home")
                total_energy += energy

                appliance.log_usage(
                    start_minutes,
                    end_minutes,
                    energy,
                    action=action,
                    power_source="home",
                    location=location
                )

        return total_energy

    def _get_home_structure_with_appliances(self, member):
        structure = {}
        for room_name, room in self.home.rooms.items():
            structure[room_name] = {
                "appliances": [appliance.to_dict() for appliance in room.appliances]
            }

        if member.personal_appliances:
            structure[f"{member.name}'s personal appliances"] = {
                "appliances": [appliance.to_dict() for appliance in member.personal_appliances]
            }

        return structure

    def _get_member(self, name):
        for member in self.home.members:
            if member.name == name:
                return member
        return None
