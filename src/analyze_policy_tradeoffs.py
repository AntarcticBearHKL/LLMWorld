import argparse
from simulation_env import sim_root
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _to_float(text):
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    text = str(text).replace("%", "").strip()
    if "(" in text:
        text = text.split("(")[-1].rstrip(")").strip()
    try:
        return float(text)
    except ValueError:
        return None


def build_report(world_id):
    path = os.path.join(sim_root(world_id), "comparison",
                        "policy_matrix.json")
    if not os.path.exists(path):
        raise ValueError("No policy_matrix.json (run compare_policies --all first)")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for s in data.get("scenarios", []):
        name = s.get("scenario", "?")
        rows.append({
            "scenario": name,
            "total_change_pct": _to_float(s.get("total_kwh")),
            "peak_hours_change_pct": _to_float(s.get("peak_hours_kwh")),
            "peak_load_cut_pct": _to_float(s.get("peak_watts")),
            "peak_plateau_cut_pct": _to_float(s.get("peak_plateau_minutes")),
            "peak_to_mean": _to_float(s.get("peak_to_mean")),
        })
    if not rows:
        raise ValueError("Matrix is empty")
    return {"scenarios": rows}


def main():
    parser = argparse.ArgumentParser(description="Policy tradeoff analysis (multi-objective)")
    parser.add_argument("world_id")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    report = build_report(args.world_id)
    report["world_id"] = args.world_id
    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, "policy_tradeoffs.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Policy tradeoff matrix (% is vs baseline; more negative is better)")
    print(f"{'Policy':<14}{'Total':<10}{'Peak hrs':<10}{'Peak':<10}{'Plateau':<10}{'P/M':<8}")
    for r in report["scenarios"]:
        fmt = lambda v: f"{v:+.1f}%" if v is not None else "-"
        print(f"{r['scenario']:<14}{fmt(r['total_change_pct']):<10}"
              f"{fmt(r['peak_hours_change_pct']):<10}"
              f"{fmt(r['peak_load_cut_pct']):<10}"
              f"{fmt(r['peak_plateau_cut_pct']):<10}"
              f"{str(r['peak_to_mean']):<8}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
