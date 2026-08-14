import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from load_profile_cluster import scan_house_profiles


def ev_curve(power_watts=7000, hours=3, start_hour=22):
    curve = [0.0] * 1440
    for m in range(start_hour * 60, min((start_hour + hours) * 60, 1440)):
        curve[m] = power_watts
    if start_hour + hours > 24:
        for m in range(0, (start_hour + hours - 24) * 60):
            curve[m] = power_watts
    return curve


def heat_pump_curve(power_watts=3000, morning=(6, 9), evening=(17, 22)):
    curve = [0.0] * 1440
    for start, end in (morning, evening):
        for m in range(start * 60, end * 60):
            curve[m] = power_watts
    return curve


def scenario_profiles(load, ev, hp, with_ev, with_hp):
    if with_ev:
        load = [load[m] + ev[m] for m in range(1440)]
    if with_hp:
        load = [load[m] + hp[m] for m in range(1440)]
    return load


def peak_hours_kwh(watts, hours=(16, 21)):
    total_wh = 0.0
    for h in range(24):
        if hours[0] <= h < hours[1]:
            total_wh += sum(watts[h * 60:(h + 1) * 60]) / 60.0
    return total_wh / 1000.0


def build_report(profiles, ev_kw=7.0, hp_kw=3.0):
    if not profiles:
        raise ValueError("没有找到任何模拟曲线")
    ev = ev_curve(int(ev_kw * 1000))
    hp = heat_pump_curve(int(hp_kw * 1000))
    scenarios = ["baseline", "ev", "hp", "ev_hp"]
    agg = {s: {"loads": []} for s in scenarios}
    for p in profiles:
        load = p["load_profile_watts"]
        for s in scenarios:
            with_ev = "ev" in s
            with_hp = "hp" in s
            agg[s]["loads"].append(scenario_profiles(load, ev, hp,
                                                     with_ev, with_hp))

    rows = []
    base_total = None
    base_peak = None
    base_evening = None
    for s in scenarios:
        total_kwh = sum(sum(l) for l in agg[s]["loads"]) / 60000
        peak_watts = max(max(l) for l in agg[s]["loads"])
        evening_kwh = sum(peak_hours_kwh(l) for l in agg[s]["loads"])
        mean = sum(sum(l) for l in agg[s]["loads"]) / (1440 * len(agg[s]["loads"]))
        peak_to_mean = round(peak_watts / mean, 2) if mean else None
        row = {
            "scenario": s,
            "total_kwh": round(total_kwh, 4),
            "peak_watts": round(peak_watts, 2),
            "evening_kwh": round(evening_kwh, 4),
            "peak_to_mean": peak_to_mean,
        }
        if s == "baseline":
            base_total, base_peak, base_evening = total_kwh, peak_watts, evening_kwh
        else:
            row["total_change_pct"] = round((total_kwh / base_total - 1) * 100, 2)
            row["peak_change_pct"] = round((peak_watts / base_peak - 1) * 100, 2)
            row["evening_change_pct"] = round((evening_kwh / base_evening - 1) * 100, 2)
        rows.append(row)
    return {"households": len(profiles), "scenarios": rows}


def main():
    parser = argparse.ArgumentParser(description="电气化情景分析（EV/热泵）")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD，缺省取每户最后一天")
    parser.add_argument("--ev-kw", type=float, default=7.0)
    parser.add_argument("--hp-kw", type=float, default=3.0)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    profiles = scan_house_profiles(args.world_id, args.scenario, args.date)
    report = build_report(profiles, args.ev_kw, args.hp_kw)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "simulation", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"electrification_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"电气化情景分析完成（{report['households']} 户）")
    for r in report["scenarios"]:
        extra = ""
        if r["scenario"] != "baseline":
            extra = (f" 总电{ r['total_change_pct']:+.1f}% "
                     f"峰值{r['peak_change_pct']:+.1f}% "
                     f"晚峰{r['evening_change_pct']:+.1f}%")
        print(f"  {r['scenario']:<9} 总电 {r['total_kwh']}kWh "
              f"峰值 {r['peak_watts']}W 晚峰 {r['evening_kwh']}kWh"
              f" 峰均比 {r['peak_to_mean']}{extra}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
