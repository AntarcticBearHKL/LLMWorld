import argparse
import json
import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_variability import scan_house_daily_profiles
from sklearn.ensemble import RandomForestRegressor


def weekday_of(date_dir):
    if len(date_dir) == 8 and date_dir.isdigit():
        date_str = f"{date_dir[:4]}-{date_dir[4:6]}-{date_dir[6:]}"
    else:
        date_str = date_dir
    return datetime.strptime(date_str, "%Y-%m-%d").weekday()


def build_house_dataset(days, min_days=5):
    if len(days) < min_days:
        return None
    rows = []
    for day in days:
        wd = weekday_of(day["date"])
        for h in range(24):
            rows.append({"hour": h, "weekday": wd, "kwh": day["hourly"][h]})
    split = int(len(days) * 0.8)
    train_days = days[:split]
    test_days = days[split:]
    if not train_days or not test_days:
        return None
    return rows, train_days, test_days


def evaluate_forecast(days, min_days=5):
    dataset = build_house_dataset(days, min_days)
    if dataset is None:
        return None
    rows, train_days, test_days = dataset
    train_rows = []
    for day in train_days:
        wd = weekday_of(day["date"])
        for h in range(24):
            train_rows.append([h, wd, day["hourly"][h]])
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    X_train = [[r[0], r[1]] for r in train_rows]
    y_train = [r[2] for r in train_rows]
    model.fit(X_train, y_train)

    total_mae = 0.0
    total_mape = 0.0
    n = 0
    naive_total_mae = 0.0
    naive_total_mape = 0.0
    for day in test_days:
        wd = weekday_of(day["date"])
        actual = day["hourly"]
        pred = model.predict([[h, wd] for h in range(24)])
        for h in range(24):
            total_mae += abs(pred[h] - actual[h])
            total_mape += abs(pred[h] - actual[h]) / actual[h] if actual[h] else 0
            n += 1
    for i in range(1, len(days)):
        actual = days[i]["hourly"]
        prev = days[i - 1]["hourly"]
        for h in range(24):
            naive_total_mae += abs(prev[h] - actual[h])
            naive_total_mape += abs(prev[h] - actual[h]) / actual[h] if actual[h] else 0
            n += 1
    if n == 0:
        return None
    naive_mae = naive_total_mae / n
    result = {
        "train_days": len(train_days),
        "test_days": len(test_days),
        "mae_kw": round(total_mae / n, 4),
        "mape": round(total_mape / n, 4),
        "naive_mae_kw": round(naive_mae, 4),
        "naive_mape": round(naive_total_mape / n, 4),
        "improvement_pct": round((1 - (total_mae / n) / naive_mae) * 100, 2)
        if naive_mae else None,
    }
    return result


def build_report(per_house):
    rows = []
    for house in per_house:
        days = sorted(house["days"], key=lambda d: d["date"])
        result = evaluate_forecast(days)
        if result is None:
            continue
        result["house_id"] = house["house_id"]
        rows.append(result)
    if not rows:
        raise ValueError("没有足够多日数据（每户至少 5 日）")
    return {"households": len(rows), "per_house": rows}


def main():
    parser = argparse.ArgumentParser(description="负荷预测与可预测性分析")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    per_house = scan_house_daily_profiles(args.world_id, args.scenario)
    report = build_report(per_house)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "outputs", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, f"forecast_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"负荷预测分析完成（{report['households']} 户）")
    for r in report["per_house"]:
        print(f"  {r['house_id']}: MAE {r['mae_kw']}kW "
              f"(naive {r['naive_mae_kw']}, 提升 {r['improvement_pct']}%) "
              f"MAPE {r['mape']}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
