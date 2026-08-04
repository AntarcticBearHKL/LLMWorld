import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.load_features import (hourly_means, normalize_shape,
                                  kmeans, auto_k)


def scan_household_days(world_id, scenario):
    outputs_root = os.path.join(PROJECT_ROOT, "outputs", world_id)
    if not os.path.isdir(outputs_root):
        return []
    samples = []
    for postcode_dir in sorted(os.listdir(outputs_root)):
        postcode_path = os.path.join(outputs_root, postcode_dir)
        if not os.path.isdir(postcode_path) or postcode_dir == "population":
            continue
        for house_id in sorted(os.listdir(postcode_path)):
            scenario_dir = os.path.join(postcode_path, house_id, scenario)
            if not os.path.isdir(scenario_dir):
                continue
            dates = sorted(d for d in os.listdir(scenario_dir)
                           if os.path.isdir(os.path.join(scenario_dir, d)))
            for date_dir in dates:
                path = os.path.join(scenario_dir, date_dir, "用电信息",
                                    "house_load_profile_1440min.json")
                if not os.path.exists(path):
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                hourly = hourly_means(data.get("load_profile_watts", []))
                samples.append({
                    "house_id": house_id,
                    "date": date_dir,
                    "kwh": data.get("total_energy_kwh", 0.0),
                    "shape": normalize_shape(hourly),
                    "hourly": hourly,
                })
    return samples


def build_report(samples, k):
    if not samples:
        raise ValueError("没有找到任何模拟曲线")
    try:
        chosen_k = k if k else auto_k([s["shape"] for s in samples])
        labels, centers, wcss = kmeans([s["shape"] for s in samples], chosen_k)
    except ValueError:
        chosen_k = 1
        labels = [0] * len(samples)
        centers = [[round(v, 6) for v in samples[0]["shape"]]]
        wcss = 0.0
    for i, sample in enumerate(samples):
        sample["cluster"] = labels[i]

    clusters = []
    for c in range(chosen_k):
        members = [s for s in samples if s["cluster"] == c]
        clusters.append({
            "label": c,
            "samples": len(members),
            "center_shape": [round(v, 6) for v in centers[c]],
            "house_days": [f"{m['house_id']}@{m['date']}" for m in members],
        })

    by_house = {}
    for s in samples:
        by_house.setdefault(s["house_id"], []).append(s)

    per_house = []
    for house_id, days in sorted(by_house.items()):
        days.sort(key=lambda d: d["date"])
        seq = [d["cluster"] for d in days]
        transitions = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
        dominant = max(range(chosen_k), key=lambda c: seq.count(c))
        per_house.append({
            "house_id": house_id,
            "n_days": len(days),
            "transitions": transitions,
            "dominant_cluster": dominant,
            "cluster_sequence": seq,
            "dates": [d["date"] for d in days],
            "mean_kwh": round(sum(d["kwh"] for d in days) / len(days), 4),
        })
    per_house.sort(key=lambda h: (-h["transitions"], h["house_id"]))

    total_transitions = sum(h["transitions"] for h in per_house)
    return {
        "households": len(per_house),
        "samples": len(samples),
        "k": chosen_k,
        "wcss": round(wcss, 4),
        "mean_transitions": round(total_transitions / len(per_house), 4),
        "clusters": clusters,
        "per_house": per_house,
    }


def main():
    parser = argparse.ArgumentParser(description="行为模式迁移分析(household-days 聚类)")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--k", type=int, default=0, help="簇数，缺省肘部法自动选")
    parser.add_argument("--out", default=None, help="输出文件路径，缺省写入 analysis/")
    args = parser.parse_args()

    samples = scan_household_days(args.world_id, args.scenario)
    report = build_report(samples, args.k)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        analysis_dir = os.path.join(PROJECT_ROOT, "outputs", args.world_id,
                                    "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        args.out = os.path.join(analysis_dir, f"patterns_{args.scenario}.json")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"行为模式迁移分析完成（{report['samples']} 个 household-days，"
          f"{report['households']} 户，k={report['k']}）")
    for c in report["clusters"]:
        print(f"  模式{c['label']}: {c['samples']} 样本")
    print(f"  平均迁移次数: {report['mean_transitions']}")
    for h in report["per_house"]:
        seq = "→".join(str(c) for c in h["cluster_sequence"])
        print(f"    {h['house_id']}: 迁移 {h['transitions']} 次, "
              f"主导簇 {h['dominant_cluster']} [{seq}]")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
