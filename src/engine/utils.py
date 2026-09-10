import json
import os
import random
from datetime import datetime

from appliances.catalog import ID_TYPE_SYNONYMS, appliance_family




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

    return json.loads(clean_json_text(text), strict=False)


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


def _snake_token(text):

    import re
    text = str(text or "").strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s-]+', '_', text)
    return text.lower()


def _parse_uid_type(unique_id):

    text = str(unique_id or "").strip().lower()
    if not text:
        return None
    tokens = text.split("_")
    candidates = []
    if tokens and tokens[-1]:
        candidates.append(("_".join(tokens[:-1]), tokens[-1]))
    if len(tokens) >= 2:
        candidates.append(("_".join(tokens[:-2]), "_".join(tokens[-2:])))
    for prefix, fragment in candidates:
        if fragment in ID_TYPE_SYNONYMS:
            return ID_TYPE_SYNONYMS[fragment], prefix
    return None


def _appliance_prefix(appliance):

    unique_id = str(getattr(appliance, "unique_id", "") or "")
    name = getattr(appliance, "name", "") or ""
    suffix = "_" + _snake_token(name)
    if name and unique_id.endswith(suffix):
        return unique_id[: -len(suffix)]
    if "_" in unique_id:
        return unique_id.rsplit("_", 1)[0]
    return ""


def repair_appliance_operations(operations, home, member_name=None):

    clean_operations = []
    repairs = []
    unknowns = []
    registry = getattr(home, "appliance_registry", None) or {}

    for operation in operations or []:
        if not isinstance(operation, dict):
            continue
        unique_id = operation.get("unique_id", "")
        action = operation.get("action", "")

        appliance = home.get_appliance(unique_id)
        if appliance is not None:
            if action in appliance.get_available_actions():
                clean_operations.append({"unique_id": unique_id, "action": action})
            else:
                unknowns.append({"unique_id": unique_id, "action": action})
            continue

        replacement = None
        parsed = _parse_uid_type(unique_id)
        if parsed is not None:
            type_token, prefix = parsed
            family = appliance_family(type_token)
            candidates = []
            for candidate in registry.values():
                if _appliance_prefix(candidate) != prefix:
                    continue
                if appliance_family(getattr(candidate, "name", None)) == family:
                    candidates.append(candidate)
            if len(candidates) == 1:
                replacement = candidates[0]

        if replacement is None:
            if parsed is not None:
                prefix = parsed[1]
            elif "_" in str(unique_id):
                prefix = str(unique_id).rsplit("_", 1)[0]
            else:
                prefix = ""
            candidates = [c for c in registry.values() if _appliance_prefix(c) == prefix]
            if len(candidates) == 1:
                replacement = candidates[0]

        if replacement is None:
            unknowns.append({"unique_id": unique_id, "action": action})
            continue

        if action in replacement.get_available_actions():
            repairs.append({"from": unique_id, "to": replacement.unique_id})
            clean_operations.append({"unique_id": replacement.unique_id, "action": action})
        else:
            unknowns.append({"unique_id": unique_id, "action": action})

    return clean_operations, repairs, unknowns


def validate_and_clean_decisions(decision_data, home, member_name=None, rooms=None):

    room_names = set(rooms) if rooms is not None else set(getattr(home, "rooms", {}) or {})
    raw_decisions = decision_data.get("appliance_decisions", []) if isinstance(decision_data, dict) else []

    cleaned_decisions = []
    repaired_all = []
    dropped_all = []
    operations_in = 0
    operations_kept = 0

    for decision in raw_decisions:
        if not isinstance(decision, dict):
            continue
        time_range = decision.get("time", "")
        location = decision.get("location", "")
        start_min, end_min = parse_time_range(time_range)

        operations = decision.get("operations", []) or []
        operations_in += len(operations)

        clean_operations, repairs, unknowns = repair_appliance_operations(
            operations, home, member_name=member_name)
        repaired_all.extend(repairs)

        final_operations = []
        outside_home = location not in room_names
        for operation in clean_operations:
            if outside_home:
                appliance = home.get_appliance(operation["unique_id"])
                owner = getattr(appliance, "owner", None) if appliance is not None else None
                if owner != member_name:
                    dropped_all.append({"unique_id": operation["unique_id"], "action": operation["action"],
                                        "reason": "out of home: room appliance not allowed"})
                    continue
                if operation["action"] == "charge_home":
                    dropped_all.append({"unique_id": operation["unique_id"], "action": operation["action"],
                                        "reason": "out of home: charge_home not allowed"})
                    continue
                if operation["action"] not in ("use", "charge_external", "idle"):
                    dropped_all.append({"unique_id": operation["unique_id"], "action": operation["action"],
                                        "reason": "out of home: action not allowed"})
                    continue
            final_operations.append(operation)

        for unknown in unknowns:
            dropped_all.append({"unique_id": unknown.get("unique_id"), "action": unknown.get("action"),
                                "reason": "unknown appliance id or invalid action"})

        operations_kept += len(final_operations)
        cleaned_decisions.append({
            "time": time_range,
            "start_minutes": start_min,
            "end_minutes": end_min,
            "location": location,
            "activity": decision.get("activity", ""),
            "operations": final_operations,
        })

    report = {
        "segments": len(cleaned_decisions),
        "operations_in": operations_in,
        "operations_kept": operations_kept,
        "repaired": repaired_all,
        "dropped": dropped_all,
        "valid": not repaired_all and not dropped_all,
    }
    return cleaned_decisions, report


def _normalize_hhmm(value):

    text = str(value).strip().replace("：", ":")
    if ":" not in text:
        return None
    hour_text, minute_text = text.split(":", 1)
    if not hour_text.isdigit() or not minute_text.isdigit():
        return None
    hour = int(hour_text)
    minute = int(minute_text)
    if hour > 24 or minute > 59:
        return None
    if hour == 24 and minute != 0:
        return None
    return f"{hour:02d}:{minute:02d}"


def _hhmm_to_minutes(hhmm):

    hour, minute = hhmm.split(":")
    return int(hour) * 60 + int(minute)


def _minutes_to_hhmm(minutes):

    if minutes >= 1440:
        return "24:00"
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


_DASH_VARIANTS = ("–", "—", "−", "－")


def normalize_time_range(time_str, next_start=None, prev_end=None):

    if time_str is None:
        return time_str
    text = str(time_str).strip()
    for dash in _DASH_VARIANTS:
        text = text.replace(dash, "-")
    text = text.replace("：", ":")
    text = "".join(text.split())
    if not text:
        return time_str

    parts = text.split("-")
    if len(parts) == 2:
        start = _normalize_hhmm(parts[0])
        end = _normalize_hhmm(parts[1])
        if start is not None and end is not None:
            return f"{start}-{end}"
        return time_str
    if len(parts) > 2:
        return time_str

    start = _normalize_hhmm(text)
    if start is None:
        return time_str

    start_minutes = _hhmm_to_minutes(start)
    end_minutes = None
    if next_start is not None:
        next_text = str(next_start).strip()
        for dash in _DASH_VARIANTS:
            next_text = next_text.replace(dash, "-")
        next_text = next_text.replace("：", ":").split("-")[0].strip()
        next_value = _normalize_hhmm(next_text)
        if next_value is not None:
            end_minutes = _hhmm_to_minutes(next_value)
    if end_minutes is None or end_minutes <= start_minutes:
        end_minutes = start_minutes + 60
    if end_minutes > 1440:
        end_minutes = 1440
    return f"{start}-{_minutes_to_hhmm(end_minutes)}"


def normalize_activity_times(items, key="time", repair_log=None):

    result = []
    if not items:
        return result
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            result.append(item)
            continue
        original = item.get(key)
        next_start = None
        if index + 1 < len(items):
            next_item = items[index + 1]
            if isinstance(next_item, dict):
                next_start = next_item.get(key)
        normalized = normalize_time_range(original, next_start=next_start)
        new_item = dict(item)
        new_item[key] = normalized
        if normalized != original and repair_log is not None:
            repair_log.append(f"segment {index + 1}: '{original}' -> '{normalized}'")
        result.append(new_item)
    return result
