import json
import os
import random
from datetime import datetime




def season_for_date(date_str):
    month = int(date_str.split("-")[1]) if "-" in date_str else int(date_str[4:6])
    if month in (12, 1, 2):
        return "Summer"
    if month in (3, 4, 5):
        return "Autumn"
    if month in (6, 7, 8):
        return "Winter"
    return "Spring"


def set_seed(seed):

    random.seed(seed)
    try:
        import numpy
        numpy.random.seed(seed)
    except ImportError:
        pass




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

        items = [format_json_compact(item, indent, current_indent + indent) for item in obj]
        return "[\n" + ",\n".join(items) + "\n" + " " * current_indent + "]"

    else:
        return json.dumps(obj, ensure_ascii=False)




def save_log(log_dir, stage_name, prompt, response, tokens=None, reasoning_content=""):

    log_file = os.path.join(log_dir, f"{stage_name}.md")

    with open(log_file, "w", encoding="utf-8") as f:
        if tokens:
            miss, hit, completion = tokens
            f.write(f"Token usage: prompt_cache_miss={miss}, prompt_cache_hit={hit}, completion={completion}\n\n")

        f.write(f"# {stage_name}\n\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("## Prompt\n\n")
        f.write("```\n")
        f.write(prompt)
        f.write("\n```\n\n")
        f.write("---\n\n")

        if reasoning_content:
            f.write("## Reasoning\n\n")
            f.write("```\n")
            f.write(reasoning_content)
            f.write("\n```\n\n")
            f.write("---\n\n")

        f.write("## LLM Response\n\n")
        f.write("```json\n")
        try:
            response_obj = json.loads(response)
            formatted_response = format_json_compact(response_obj)
            f.write(formatted_response)
        except Exception:
            f.write(response)
        f.write("\n```\n")




def parse_time(time_str):

    try:
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    except Exception as e:
        print(f"[Error] Failed to parse time: '{time_str}' - {e}")
        print("[Fallback] Using default time: 00:00")
        return 0


def parse_time_range(time_range):


    try:
        parts = time_range.split('-')
        if len(parts) != 2:
            print(f"[Warning] Time format error: '{time_range}', attempting to fix...")
            if len(parts) > 2:
                start, end = parts[0], parts[-1]
                print(f"[Fixed] Using the first and last times: {start} - {end}")
            else:
                raise ValueError(f"Cannot parse time range: {time_range}")
        else:
            start, end = parts

        start_min = parse_time(start.strip())
        end_min = parse_time(end.strip())

        if end_min <= start_min:
            end_min += 1440

        return start_min, end_min
    except Exception as e:
        print(f"[Error] Failed to parse time range: '{time_range}' - {e}")
        print("[Fallback] Using default time range: 00:00-00:10")
        return 0, 10




def clean_json_text(text):

    text = text.strip()

    if text.startswith('```'):
        lines = text.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines)

    start = None
    for i, ch in enumerate(text):
        if ch in "[{":
            start = i
            break

    return text[start:].strip() if start is not None else text.strip()


def parse_json_response(text):

    return json.loads(clean_json_text(text))


def parse_json_with_retry(prompt, raw_text, json_mode=True, thinking=False):




    try:
        return parse_json_response(raw_text)
    except Exception:
        from .subagent import SubAgent
        retry_prompt = prompt + (
            "\n\nImportant: your previous output was not valid JSON. "
            "Please output again, providing only a single valid JSON object, with no explanation and no code fence markers."
        )
        result = SubAgent.single_call(retry_prompt, json_mode=json_mode, thinking=thinking)
        content = result["content"] if isinstance(result, dict) else result
        return parse_json_response(content)


def validate_appliance_decisions(decision_data, home, warnings):




    cleaned_decisions = []
    raw_decisions = decision_data.get("appliance_decisions", [])

    for decision in raw_decisions:
        try:
            time_range = decision["time"]
            location = decision.get("location", "")
            start_min, end_min = parse_time_range(time_range)

            operations = []
            for operation in decision.get("operations", []):
                appliance_id = operation.get("unique_id", "")
                action = operation.get("action", "")

                appliance = home.get_appliance(appliance_id)
                if not appliance:
                    warnings.append(
                        f"Unknown appliance unique_id='{appliance_id}' (member {decision_data.get('member','?')}, "
                        f"time {time_range}, location {location}) -> operation skipped"
                    )
                    continue

                if action not in appliance.get_available_actions():
                    warnings.append(
                        f"Invalid action='{action}' (appliance {appliance.name}[{appliance_id}], available: "
                        f"{appliance.get_available_actions()}) -> operation skipped"
                    )
                    continue

                operations.append({"unique_id": appliance_id, "action": action})

            cleaned_decisions.append({
                "time": time_range,
                "start_minutes": start_min,
                "end_minutes": end_min,
                "location": location,
                "activity": decision.get("activity", ""),
                "operations": operations,
            })
        except Exception as e:
            warnings.append(f"Decision parse failed: {e} -> this time segment was skipped")

    return cleaned_decisions
