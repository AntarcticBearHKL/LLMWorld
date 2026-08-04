import argparse
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
    path = os.path.join(PROJECT_ROOT, "outputs", world_id, "comparison",
                        "policy_matrix.json")
    if not os.path.exists(path):
        raise ValueError("没有 policy_matrix.json（先跑 compare_policies --all）")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for s in data.get("scenarios", []):
        name = s.get("场景", "?")
        rows.append({
            "scenario": name,
            "total_change_pct": _to_float(s.get("总kWh")),
            "peak_hours_change_pct": _to_float(s.get("晚峰16-21点kWh")),
            "peak_load_cut_pct": _to_float(s.get("峰值W")),
            "peak_plateau_cut_pct": _to_float(s.get("峰值平台分钟")),
            "peak_to_mean": _to_float(s.get("峰均比")),
        })
    if not rows:
        raise ValueError("矩阵为空")
    return {"scenarios": rows}


def main():
    parser = argparse.ArgumentParser(description="政策权衡分析（多目标）")
    parser.add_argument("world_id")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    report = build_report(args.world_id)
    report["world_id"] = args.world_id
    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "outputs", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, "policy_tradeoffs.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("政策权衡矩阵（% 为 vs 基线；越负越优）")
    print(f"{'政策':<14}{'总电':<10}{'晚峰':<10}{'峰值':<10}{'平台':<10}{'峰均比':<8}")
    for r in report["scenarios"]:
        fmt = lambda v: f"{v:+.1f}%" if v is not None else "-"
        print(f"{r['scenario']:<14}{fmt(r['total_change_pct']):<10}"
              f"{fmt(r['peak_hours_change_pct']):<10}"
              f"{fmt(r['peak_load_cut_pct']):<10}"
              f"{fmt(r['peak_plateau_cut_pct']):<10}"
              f"{str(r['peak_to_mean']):<8}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
