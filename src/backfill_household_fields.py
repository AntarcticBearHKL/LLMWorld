"""旧世界字段补丁：为修复前生成的 household.json 补充分析工具所需字段。

用法:
  python src/backfill_household_fields.py pop03

为每位成员 personality 补：energy_awareness / news_sensitivity / big_five（已有则不覆盖）。
新世界（generate_world.py 新模板）已由 LLM 生成这些字段，无需运行。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def backfill(world_id):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(project_root, "worlds", world_id, "3168")
    if not os.path.isdir(base):
        print(f"[错误] 未找到世界 {world_id} 的目录：{base}")
        sys.exit(1)

    patched = 0
    for house_id in sorted(os.listdir(base)):
        p = os.path.join(base, house_id, "household.json")
        if not os.path.isfile(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            household = json.load(f)
        changed = False
        for m in household.get("members", []):
            pers = m.setdefault("personality", {})
            if not isinstance(pers, dict):
                continue
            if "energy_awareness" not in pers:
                pers["energy_awareness"] = "低"   # 兜底；重新生成可获得 LLM 推断值
                changed = True
            if "news_sensitivity" not in pers:
                pers["news_sensitivity"] = "中"
                changed = True
            if "big_five" not in pers:
                pers["big_five"] = {}
                changed = True
        if changed:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(household, f, ensure_ascii=False, indent=2)
            patched += 1
            print(f"  [补丁] {house_id} 已补字段")
    print(f"完成：{patched} 户已补充（worlds/{world_id}/）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="旧世界 household.json 字段补丁")
    parser.add_argument("world_id", help="世界ID，如 pop03")
    args = parser.parse_args()
    backfill(args.world_id)
