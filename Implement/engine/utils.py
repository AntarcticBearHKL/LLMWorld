"""公共工具模块：JSON 格式化、日志保存、时间解析、LLM 输出校验。

所有模块统一从这里取工具函数，避免复制粘贴重复代码。
设计原则：每个函数只做一件事，命名即文档（不懂代码的人也能看懂）。
"""

import json
import os
import random
from datetime import datetime


# ---------- 随机种子 ----------

def set_seed(seed):
    """固定随机种子，保证实验可复现（论文要求）。"""
    random.seed(seed)
    try:
        import numpy
        numpy.random.seed(seed)
    except ImportError:
        pass  # numpy 非必需，无则跳过


# ---------- JSON 格式化 ----------

def format_json_compact(obj, indent=2, current_indent=0):
    """把 JSON 格式化得紧凑易读（列表项不留额外缩进），用于写日志。"""
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


# ---------- 日志保存 ----------

def save_log(log_dir, stage_name, prompt, response, tokens=None, reasoning_content=""):
    """把一次 LLM 调用的 提示词/思考过程/返回结果 保存为 .md 日志文件。"""
    log_file = os.path.join(log_dir, f"{stage_name}.md")

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
        except Exception:
            f.write(response)
        f.write("\n```\n")


# ---------- 时间解析 ----------

def parse_time(time_str):
    """把 'HH:MM' 解析为"从零点起的分钟数"。失败时返回 0 并打印警告。"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    except Exception as e:
        print(f"[错误] 解析时间失败: '{time_str}' - {e}")
        print("[回退] 使用默认时间: 00:00")
        return 0


def parse_time_range(time_range):
    """把 'HH:MM-HH:MM' 解析为 (开始分钟, 结束分钟)。
    跨天时自动 +1440（如 22:00-02:00）；格式错误时回退 (0, 10)。"""
    try:
        parts = time_range.split('-')
        if len(parts) != 2:
            print(f"[警告] 时间格式错误: '{time_range}'，尝试修复...")
            if len(parts) > 2:
                start, end = parts[0], parts[-1]
                print(f"[修复] 使用第一个和最后一个时间: {start} - {end}")
            else:
                raise ValueError(f"无法解析时间范围: {time_range}")
        else:
            start, end = parts

        start_min = parse_time(start.strip())
        end_min = parse_time(end.strip())

        if end_min <= start_min:
            end_min += 1440

        return start_min, end_min
    except Exception as e:
        print(f"[错误] 解析时间范围失败: '{time_range}' - {e}")
        print("[回退] 使用默认时间范围: 00:00-00:10")
        return 0, 10


# ---------- LLM 返回解析与校验 ----------

def clean_json_text(text):
    """去掉 LLM 返回中的 ```json 代码块标记，只保留 JSON 本体。"""
    text = text.strip()

    if text.startswith('```'):
        lines = text.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines)

    return text.strip()


def parse_json_response(text):
    """清理 LLM 返回的 ```json 代码块并解析为 Python 对象。解析失败抛异常（不静默）。"""
    return json.loads(clean_json_text(text))


def parse_json_with_retry(prompt, raw_text, json_mode=True, thinking=False):
    """解析 LLM 返回的 JSON；失败时用同一 prompt 重试一次（追加'只输出JSON'指令）。

    这是对 thinking=False 快速模式下偶发畸形 JSON 的保险：最多多花一次调用，
    但避免整层结果丢失。仍失败则抛原始异常（由调用方显式处理）。
    """
    try:
        return parse_json_response(raw_text)
    except Exception:
        from .subagent import SubAgent
        retry_prompt = prompt + (
            "\n\n重要：你上一次的输出不是合法 JSON。"
            "请重新输出，只输出一个合法 JSON 对象，不要任何解释、不要代码块标记。"
        )
        result = SubAgent.single_call(retry_prompt, json_mode=json_mode, thinking=thinking)
        content = result["content"] if isinstance(result, dict) else result
        return parse_json_response(content)


def validate_appliance_decisions(decision_data, home, warnings):
    """校验 LLM 的用电决策：unique_id 必须存在、action 必须合法。

    返回清洗后的决策列表；非法操作不会被静默丢弃，而是记入 warnings。
    """
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
                        f"未知电器 unique_id='{appliance_id}'（成员 {decision_data.get('member','?')}，"
                        f"时段 {time_range}，位置 {location}）→ 已跳过该操作"
                    )
                    continue

                if action not in appliance.get_available_actions():
                    warnings.append(
                        f"非法操作 action='{action}'（电器 {appliance.name}[{appliance_id}]，可用: "
                        f"{appliance.get_available_actions()}）→ 已跳过该操作"
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
            warnings.append(f"决策解析失败: {e} → 该时段已跳过")

    return cleaned_decisions
