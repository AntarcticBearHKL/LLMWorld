import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root


def load_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def build_report(world_id, scenario):
    analysis_dir = os.path.join(sim_root(world_id), "analysis")

    cluster = load_json(os.path.join(analysis_dir, f"clusters_{scenario}_latest.json"))
    if not cluster:
        cluster = None
        if os.path.isdir(analysis_dir):
            for name in sorted(os.listdir(analysis_dir)):
                if name.startswith(f"clusters_{scenario}_"):
                    cluster = load_json(os.path.join(analysis_dir, name))
                    break
    variability = load_json(os.path.join(analysis_dir,
                                         f"variability_{scenario}.json"))
    anomalies = load_json(os.path.join(analysis_dir, f"anomalies_{scenario}.json"))
    behavior = None
    if os.path.isdir(analysis_dir):
        for name in sorted(os.listdir(analysis_dir)):
            if name.startswith(f"behavior_load_{scenario}_"):
                behavior = load_json(os.path.join(analysis_dir, name))
                break

    cluster_map = {}
    if cluster and "per_house" in cluster:
        for item in cluster["per_house"]:
            cluster_map[item["house_id"]] = item["cluster"]

    house_ids = set()
    for source in (cluster, variability, anomalies, behavior):
        if source and "per_house" in source:
            for item in source["per_house"]:
                house_ids.add(item["house_id"])

    variability_group = {}
    if variability:
        for hid in variability.get("regular_half", []):
            variability_group[hid] = "Regular"
        for hid in variability.get("variable_half", []):
            variability_group[hid] = "Variable"

    anomaly_map = {}
    if anomalies and "per_house" in anomalies:
        for item in anomalies["per_house"]:
            anomaly_map[item["house_id"]] = item.get("anomaly_flags", [])

    consistency_map = {}
    if behavior and "per_house" in behavior:
        for item in behavior["per_house"]:
            consistency_map[item["house_id"]] = item.get("load_consistent")

    kwh_map = {}
    if anomalies and "per_house" in anomalies:
        for item in anomalies["per_house"]:
            kwh_map[item["house_id"]] = item.get("total_kwh")

    rows = []
    for hid in sorted(house_ids):
        rows.append({
            "house_id": hid,
            "cluster": cluster_map.get(hid),
            "variability_group": variability_group.get(hid),
            "anomaly_flags": anomaly_map.get(hid, []),
            "load_consistent": consistency_map.get(hid),
            "total_kwh": kwh_map.get(hid),
        })
    return {"households": len(rows), "per_house": rows}


def main():
    parser = argparse.ArgumentParser(description="World summary (aggregates all analyses)")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    report = build_report(args.world_id, args.scenario)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    if not report["per_house"]:
        raise ValueError("No analysis data found")

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, f"world_summary_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"World summary done ({report['households']} households)")
    for r in report["per_house"]:
        flags = "；".join(r["anomaly_flags"]) or "OK"
        print(f"  {r['house_id']}: cluster {r['cluster']} {r['variability_group']} "
              f"consistent={r['load_consistent']} kWh={r['total_kwh']} [{flags}]")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
