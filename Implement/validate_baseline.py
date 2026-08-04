"""基线对比：人口模拟负荷 vs 维州真实负荷（RQ3 第一组证据）。

对比对象：
- 模拟：population_runner 聚合输出（1440 分钟曲线，或各户曲线）
- 真实：vic_electricity_data.csv（VIC1 区域小时需求 MW，OpenElectricity）

方法：都转成"归一化小时曲线"（每小时均值/全天均值），比较形状而非量纲。

用法：
    python Implement/validate_baseline.py --world pop01 [--real vic_electricity_data.csv]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import pandas as pd


# ---------- 指标计算（纯函数，便于测试）----------

def hourly_normalized(load_watts_or_mw, hours=24):
    """1440 分钟(或 N 小时)数据 → 归一化小时曲线（每小时均值/全天均值）。"""
    n = len(load_watts_or_mw)
    if n == hours * 60:
        hourly = [sum(load_watts_or_mw[h * 60:(h + 1) * 60]) / 60.0 for h in range(hours)]
    else:
        hourly = list(load_watts_or_mw)  # 已是小时数据
    mean = sum(hourly) / len(hourly)
    if mean == 0:
        return [0.0] * len(hourly)
    return [v / mean for v in hourly]


def find_peak_hour(curve):
    """返回 (峰值小时, 峰值归一化值)。"""
    peak = max(range(len(curve)), key=lambda h: curve[h])
    return peak, curve[peak]


def find_valley_hour(curve):
    valley = min(range(len(curve)), key=lambda h: curve[h])
    return valley, curve[valley]


def peak_to_mean(curve):
    return max(curve)


def bimodality(curve, morning=(6, 10), evening=(16, 21)):
    """双峰强度：晚峰均值与晨峰均值的比值 + 谷底深度。"""
    m_peak = max(curve[morning[0]:morning[1] + 1])
    e_peak = max(curve[evening[0]:evening[1] + 1])
    valley = min(curve)
    return {
        "morning_peak": round(m_peak, 3),
        "evening_peak": round(e_peak, 3),
        "evening_over_morning": round(e_peak / m_peak, 3) if m_peak else None,
        "valley": round(valley, 3),
    }


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    if va == 0 or vb == 0:
        return 0.0
    return cov / (va * vb)


def compare_curves(sim_curve, real_curve):
    """两条归一化小时曲线 → 对比报告。"""
    sim_h, sim_v = find_peak_hour(sim_curve)
    real_h, real_v = find_peak_hour(real_curve)
    sim_valley, _ = find_valley_hour(sim_curve)
    real_valley, _ = find_valley_hour(real_curve)

    return {
        "sim_peak_hour": sim_h,
        "real_peak_hour": real_h,
        "peak_hour_offset": real_h - sim_h,
        "sim_peak_to_mean": round(peak_to_mean(sim_curve), 3),
        "real_peak_to_mean": round(peak_to_mean(real_curve), 3),
        "sim_bimodality": bimodality(sim_curve),
        "real_bimodality": bimodality(real_curve),
        "sim_valley_hour": sim_valley,
        "real_valley_hour": real_valley,
        "correlation": round(pearson(sim_curve, real_curve), 4),
        "sim_hourly": [round(v, 3) for v in sim_curve],
        "real_hourly": [round(v, 3) for v in real_curve],
    }


# ---------- 数据加载 ----------

def load_real_data(path):
    """加载 VIC1 小时需求 CSV → (hourly_mw 列表, 日期列表)。"""
    df = pd.read_csv(path)
    df = df[df["region_id"] == "VIC1"]
    df["interval"] = pd.to_datetime(df["interval"])
    df = df.sort_values("interval")

    # 取一个完整的自然日（0 点开始、24 个整点），保证与模拟的小时轴一致
    df["date"] = df["interval"].dt.date
    full_day = None
    for d, g in df.groupby("date"):
        if len(g) == 24 and g["interval"].min().hour == 0:
            full_day = g
            break
    if full_day is None:
        raise ValueError("真实数据中没有完整的自然日（0 点起 24 小时）")
    df = full_day

    hourly = df["demand"].tolist()
    dates = df["interval"].dt.strftime("%Y-%m-%d %H:%M").tolist()
    return hourly, dates, df


def load_sim_profile(world_id):
    """读取 population 聚合曲线（aggregate_only.json 或按日期目录取最新）。"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_dir = os.path.join(project_root, "outputs", world_id, "population")

    candidates = []
    if os.path.isdir(pop_dir):
        for name in os.listdir(pop_dir):
            p = os.path.join(pop_dir, name)
            if os.path.isfile(p) and name.endswith(".json"):
                candidates.append(p)
        date_dirs = [os.path.join(pop_dir, d) for d in os.listdir(pop_dir)
                     if os.path.isdir(os.path.join(pop_dir, d))]
        for d in date_dirs:
            for f in os.listdir(d):
                if f.endswith(".json"):
                    candidates.append(os.path.join(d, f))

    if not candidates:
        raise FileNotFoundError(f"没有找到 {world_id} 的人口聚合曲线，请先跑 population_runner")

    path = sorted(candidates)[-1]   # 取最新
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data, path


# ---------- 主流程 ----------

def main():
    parser = argparse.ArgumentParser(description="人口模拟 vs 维州真实负荷基线对比")
    parser.add_argument("--world", required=True, help="世界ID（取人口聚合曲线）")
    parser.add_argument("--real", default=None, help="真实数据 CSV（默认项目根目录 vic_electricity_data.csv）")
    parser.add_argument("--out", default=None, help="输出目录（默认 outputs/<world>/baseline/）")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    real_path = args.real or os.path.join(project_root, "vic_electricity_data.csv")

    # 加载数据
    sim_data, sim_path = load_sim_profile(args.world)
    real_hourly, real_dates, _ = load_real_data(real_path)
    print(f"模拟数据: {sim_path}")
    print(f"  总用电 {sim_data.get('total_energy_kwh')} kWh, {sim_data.get('households')} 户")
    print(f"真实数据: {real_path}")
    print(f"  小时需求 {len(real_hourly)} 点, 首 {real_dates[0]} → 末 {real_dates[-1]}")

    # 归一化小时曲线
    sim_curve = hourly_normalized(sim_data["load_profile_watts"])
    real_curve = hourly_normalized(real_hourly)

    report = compare_curves(sim_curve, real_curve)
    report["sim_source"] = sim_path
    report["real_source"] = real_path
    report["sim_total_kwh"] = sim_data.get("total_energy_kwh")
    report["real_mean_mw"] = round(sum(real_hourly) / len(real_hourly), 2)

    # 输出
    out_dir = args.out or os.path.join(project_root, "outputs", args.world, "baseline")
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "baseline_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 打印解读
    print("\n=== 形状对比报告 ===")
    print(f"晚峰时刻: 模拟 {report['sim_peak_hour']}:00 vs 真实 {report['real_peak_hour']}:00"
          f"（偏移 {report['peak_hour_offset']} 小时）")
    print(f"峰均比: 模拟 {report['sim_peak_to_mean']} vs 真实 {report['real_peak_to_mean']}")
    print(f"双峰强度(晨/晚): 模拟 {report['sim_bimodality']['morning_peak']}/{report['sim_bimodality']['evening_peak']}"
          f" vs 真实 {report['real_bimodality']['morning_peak']}/{report['real_bimodality']['evening_peak']}")
    print(f"谷值时刻: 模拟 {report['sim_valley_hour']}:00 vs 真实 {report['real_valley_hour']}:00")
    print(f"逐小时相关性: {report['correlation']}")
    print(f"报告已保存: {report_path}")

    # 出图
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False

        hours = list(range(24))
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        ax.plot(hours, report["sim_hourly"], "o-", label=f"模拟人口 (world {args.world})")
        ax.plot(hours, report["real_hourly"], "s--", label="真实 VIC1 需求 (2026-06-23 周二)")
        ax.axvline(report["sim_peak_hour"], color="C0", alpha=0.3, linestyle=":")
        ax.axvline(report["real_peak_hour"], color="C1", alpha=0.3, linestyle=":")
        ax.set_xlabel("小时")
        ax.set_ylabel("归一化负荷（全天均值 = 1）")
        ax.set_title(f"人口模拟 vs 维州真实负荷形状对比（相关性 {report['correlation']}）")
        ax.legend()
        ax.grid(alpha=0.3)
        png_path = os.path.join(out_dir, "baseline_shape.png")
        fig.savefig(png_path, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"对比图已保存: {png_path}")
    except ImportError:
        print("（matplotlib 未安装，跳过出图）")


if __name__ == "__main__":
    main()
