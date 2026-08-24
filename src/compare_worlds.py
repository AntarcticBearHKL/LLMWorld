import argparse
from simulation_env import sim_root
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_world_policies(world_id):
    path = os.path.join(sim_root(world_id), "comparison",
                        "policy_matrix.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = {}
    for scenario in data.get("scenarios", []):
        name = scenario.get("scenario", "?")
        rows[name] = {
            "total_change_pct": _to_float(scenario.get("total_kwh")),
            "peak_hours_change_pct": _to_float(scenario.get("peak_hours_kwh")),
            "peak_load_cut_pct": _to_float(scenario.get("peak_watts")),
            "peak_plateau_cut_pct": _to_float(scenario.get("peak_plateau_minutes")),
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
        raise ValueError("No policy_matrix.json for any world (run compare_policies --all first)")
    scenarios = set()
    for rows in worlds.values():
        scenarios.update(rows.keys())
    scenarios = sorted(s for s in scenarios if s != "baseline")
    matrix = {"worlds": list(worlds.keys()), "scenarios": scenarios, "cells": {}}
    for world_id, rows in worlds.items():
        matrix["cells"][world_id] = {s: rows.get(s, {}) for s in scenarios}
    return matrix


def main():
    parser = argparse.ArgumentParser(description="Cross-world policy effect comparison")
    parser.add_argument("--worlds", nargs="+", required=True,
                        help="World ID list, e.g. pop06 pop07")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    matrix = build_matrix(args.worlds)
    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "simulation", "comparison")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, "worlds_matrix.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)

    print("=== Cross-world policy effect comparison (total energy change %) ===")
    header = f"{'scenario':<14}" + "".join(f"{w:<16}" for w in matrix["worlds"])
    print(header)
    for s in matrix["scenarios"]:
        cells = []
        for w in matrix["worlds"]:
            pct = matrix["cells"][w].get(s, {}).get("total_change_pct")
            cells.append(f"{pct:+.1f}%".ljust(16) if pct is not None else "  -  ".ljust(16))
        print(f"{s:<14}" + "".join(cells))
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
