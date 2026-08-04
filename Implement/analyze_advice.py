import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_anomalies import build_report as build_anomaly_report
from load_profile_cluster import scan_house_profiles
from engine.load_features import hourly_means, peak_hour, peak_to_mean


def advice_for(metrics):
    advice = []
    if metrics.get("total_kwh_z") is not None and metrics["total_kwh_z"] > 2:
        advice.append("用电显著高于社区平均：空调设定 26°C 以上、"
                      "随手关灯、换用 LED、缩短大功率电器使用时长")
    if metrics.get("overlap_count", 0) > 0:
        advice.append("存在大功率叠加：将洗衣机/吸尘器与空调、"
                      "电磁炉错开使用，避免同小时叠加")
    if metrics.get("peak_hour") is not None and 17 <= metrics["peak_hour"] <= 21:
        advice.append("晚峰集中：将洗衣机/吸尘器/电动汽车充电移至"
                      "22 点后（谷段电价更低）")
    if metrics.get("peak_to_mean") is not None and metrics["peak_to_mean"] > 5:
        advice.append("峰谷差大：分散用电时段，避免瞬时高功率")
    return advice


def build_report(profiles):
    anomaly = build_anomaly_report(profiles)
    rows = []
    for r in anomaly["per_house"]:
        hourly = hourly_means(
            next(p["load_profile_watts"] for p in profiles
                 if p["house_id"] == r["house_id"]))
        metrics = {
            "total_kwh_z": r.get("z_total_kwh"),
            "overlap_count": r.get("overlap_count", 0),
            "peak_hour": peak_hour(hourly),
            "peak_to_mean": peak_to_mean(hourly),
        }
        advice = advice_for(metrics)
        if not advice:
            advice = ["用电规律健康，保持当前习惯"]
        rows.append({"house_id": r["house_id"], "advice": advice})
    return {"households": len(rows), "per_house": rows}


def main():
    parser = argparse.ArgumentParser(description="个性化节能建议（advisor）")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD，缺省取每户最后一天")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    profiles = scan_house_profiles(args.world_id, args.scenario, args.date)
    report = build_report(profiles)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "outputs", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"advice_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"个性化建议生成完成（{report['households']} 户）")
    for r in report["per_house"]:
        print(f"  {r['house_id']}:")
        for a in r["advice"]:
            print(f"    - {a}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
