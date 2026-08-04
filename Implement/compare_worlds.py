import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_world_policies(world_id):
    path = os.path.join(PROJECT_ROOT, "outputs", world_id, "comparison",
                        "policy_matrix.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = {}
    for scenario in data.get("scenarios", []):
        name = scenario.get("场景", "?")
        rows[name] = {
            "total_change_pct": _to_float(scenario.get("总kWh")),
            "peak_hours_change_pct": _to_float(scenario.get("晚峰16-21点kWh")),
            "peak_load_cut_pct": _to_float(scenario.get("峰值W")),
            "peak_plateau_cut_pct": _to_float(scenario.get("峰值平台分钟")),
        }
    return rows


def _to_float(text):
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    text = str(text)
    if "(" in text:
        text = text.split("(")[-1].split("%")[0]
    try:
        return float(text)
    except ValueError:
        return None


def build_matrix(world_ids):
    worlds = {}
    for world_id in world_ids:
        rows = load_world_policies(world_id)
        if rows:
            worlds[world_id] = rows
    if not worlds:
        raise ValueError("没有任何世界的 policy_matrix.json（先跑 compare_policies --all）")
    scenarios = set()
    for rows in worlds.values():
        scenarios.update(rows.keys())
    scenarios = sorted(s for s in scenarios if s != "baseline")
    matrix = {"worlds": list(worlds.keys()), "scenarios": scenarios, "cells": {}}
    for world_id, rows in worlds.items():
        matrix["cells"][world_id] = {s: rows.get(s, {}) for s in scenarios}
    return matrix


def main():
    parser = argparse.ArgumentParser(description="多世界政策效果横向对比")
    parser.add_argument("--worlds", nargs="+", required=True,
                        help="世界 ID 列表，如 pop06 pop07")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    matrix = build_matrix(args.worlds)
    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "outputs", "comparison")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, "worlds_matrix.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)

    print("=== 多世界政策效果横向对比（总用电变化%）===")
    header = f"{'场景':<14}" + "".join(f"{w:<16}" for w in matrix["worlds"])
    print(header)
    for s in matrix["scenarios"]:
        cells = []
        for w in matrix["worlds"]:
            pct = matrix["cells"][w].get(s, {}).get("total_change_pct")
            cells.append(f"{pct:+.1f}%".ljust(16) if pct is not None else "  -  ".ljust(16))
        print(f"{s:<14}" + "".join(cells))
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
