# -*- coding: utf-8 -*-


import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check(world_id, date_iso):
    from simulation_env import latest_env, SIMULATION_DIR
    env_id = latest_env(world_id)
    if not env_id:
        print("世界无模拟环境（simulation/<world>_*）")
        return False

    day_root = os.path.join(SIMULATION_DIR, env_id, date_iso)  # 如 2026-04-22
    if not os.path.isdir(day_root):
        print(f"[{world_id}] 环境 {env_id} 无 {date_iso} 日期目录（该日期可能未模拟）")
        return False

    checked = 0
    memory_hits = 0
    for postcode in sorted(os.listdir(day_root)):
        pc_dir = os.path.join(day_root, postcode)
        if not os.path.isdir(pc_dir):
            continue
        for house_id in sorted(os.listdir(pc_dir)):
            house_dir = os.path.join(pc_dir, house_id)
            if not os.path.isdir(house_dir):
                continue
            for f in sorted(os.listdir(house_dir)):
                if f.startswith("01_第一层") and f.endswith(".md"):
                    with open(os.path.join(house_dir, f), "r", encoding="utf-8") as fh:
                        text = fh.read()
                    checked += 1
                    if "昨日记忆" in text:
                        memory_hits += 1
                    break

    print(f"[{world_id}] 环境 {env_id} 第 {date_iso} 天：检查 {checked} 个成员第一层日志，"
          f"{memory_hits} 个含昨日记忆章节")
    if checked == 0:
        print("  未找到第一层日志")
    return memory_hits == checked and checked > 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="续跑记忆检查（模拟环境新结构）")
    parser.add_argument("world_id")
    parser.add_argument("date_iso", help="日期目录（格式 YYYY-MM-DD，如 2026-04-22）")
    args = parser.parse_args()
    ok = check(args.world_id, args.date_iso)
    sys.exit(0 if ok else 1)
