








import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check(world_id, date_dir):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(project_root, "outputs", world_id, "3168")
    if not os.path.isdir(base):
        print("世界无输出目录")
        return

    checked = 0
    memory_hits = 0
    for house_id in sorted(os.listdir(base)):
        scenario_dir = os.path.join(base, house_id, "baseline")
        if not os.path.isdir(scenario_dir):
            continue
        day_dir = os.path.join(scenario_dir, date_dir)
        if not os.path.isdir(day_dir):
            continue
        for f in os.listdir(day_dir):
            if f.startswith("01_第一层") and f.endswith(".md"):
                path = os.path.join(day_dir, f)
                with open(path, "r", encoding="utf-8") as fh:
                    text = fh.read()
                checked += 1
                if "昨日记忆" in text:
                    memory_hits += 1
                break

    print(f"[{world_id}] 第 {date_dir} 天：检查 {checked} 个成员第一层日志，"
          f"{memory_hits} 个含昨日记忆章节")
    if checked == 0:
        print("  未找到第一层日志（该日期可能未模拟）")
    return memory_hits == checked and checked > 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="续跑记忆检查")
    parser.add_argument("world_id")
    parser.add_argument("date_dir", help="日期目录（紧凑格式 20260422）")
    args = parser.parse_args()
    ok = check(args.world_id, args.date_dir)
    sys.exit(0 if ok else 1)
