import argparse
from simulation_env import sim_root
import csv
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def flatten(record, prefix=""):
    flat = {}
    for key, value in record.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(flatten(value, name + "."))
        elif isinstance(value, list):
            flat[name] = json.dumps(value, ensure_ascii=False)
        else:
            flat[name] = value
    return flat


def export_json_to_csv(path, out_dir):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = None
    for key in ("per_house", "scenarios", "groups", "seasons", "clusters"):
        if isinstance(data.get(key), list):
            records = data[key]
            break
    if records is None:
        if isinstance(data, dict):
            records = [data]
        else:
            return None
    flat_records = [flatten(r) for r in records]
    keys = []
    seen = set()
    for r in flat_records:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    name = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(out_dir, f"{name}.csv")
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in flat_records:
            writer.writerow(r)
    return out_path


def export_world(world_id):
    analysis_dir = os.path.join(sim_root(world_id), "analysis")
    if not os.path.isdir(analysis_dir):
        raise ValueError(f"No analysis directory: {analysis_dir}")
    out_dir = os.path.join(analysis_dir, "csv")
    os.makedirs(out_dir, exist_ok=True)
    exported = []
    for name in sorted(os.listdir(analysis_dir)):
        if not name.endswith(".json") or name.startswith("csv"):
            continue
        path = os.path.join(analysis_dir, name)
        result = export_json_to_csv(path, out_dir)
        if result:
            exported.append(result)
    if not exported:
        raise ValueError("No JSON reports to export")
    return exported


def main():
    parser = argparse.ArgumentParser(description="Export analysis results to CSV")
    parser.add_argument("world_id")
    args = parser.parse_args()

    exported = export_world(args.world_id)
    print(f"CSV export done ({len(exported)} files)")
    for path in exported:
        print(f"  {path}")
    print(f"  Directory: output/simulation/{args.world_id}/analysis/csv/")


if __name__ == "__main__":
    main()
