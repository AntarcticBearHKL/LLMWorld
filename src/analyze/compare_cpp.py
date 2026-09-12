"""Critical-peak-pricing (CPP) same-era comparison (R161).

Compares paired envs ``<prefix>_b_<i>`` (baseline) vs ``<prefix>_c_<i>`` (``--policy cpp``)
for one world/house/date. Reuses the unified dataset reader so load maths match the rest
of the analysis suite. Reports total, evening-peak (16-21h) and per-appliance energy plus a
paired t-test across the n pairs.

Usage:
    python compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 \
        --prefix cpp --n 9 [--tag cpp]
"""
import argparse
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from dataset import iter_house_days  # noqa: E402

PEAK_MIN = (16 * 60, 21 * 60)  # 16:00-21:00 (project's evening peak)
VALLEY_MIN = ((0, 7 * 60), (22 * 60, 1440))  # 22:00-07:00 (project's valley)


def peak_kwh(profile):
    return sum(profile[PEAK_MIN[0]:PEAK_MIN[1]]) / 60.0 / 1000.0


def valley_kwh(profile):
    return sum(sum(profile[a:b]) for a, b in VALLEY_MIN) / 60.0 / 1000.0


def one_record(world, env, date, house, policy):
    recs = list(iter_house_days(world, env=env, date=date, policy=policy, houses=[house]))
    if not recs:
        raise SystemExit(f"[ERR] no record for env={env} policy={policy} house={house}")
    return recs[0]


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def paired_t(a, b):
    """Paired t on differences a-b; returns (t, n)."""
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    sd = std(d)
    if n < 2 or sd == 0:
        return float("nan"), n
    return mean(d) / (sd / math.sqrt(n)), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", required=True)
    ap.add_argument("--house", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--prefix", default="cpp")
    ap.add_argument("--base-prefix", default=None, help="default: <prefix>_b")
    ap.add_argument("--treat-prefix", default=None, help="default: <prefix>_c")
    ap.add_argument("--n", type=int, default=9)
    ap.add_argument("--tag", default="cpp", help="policy tag used by the treatment envs")
    args = ap.parse_args()

    base_prefix = args.base_prefix or f"{args.prefix}_b"
    treat_prefix = args.treat_prefix or f"{args.prefix}_c"

    rows = []
    for i in range(1, args.n + 1):
        b = one_record(args.world, f"{base_prefix}_{i}", args.date, args.house, "baseline")
        c = one_record(args.world, f"{treat_prefix}_{i}", args.date, args.house, args.tag)
        rows.append((b, c))

    def series(recs, key):
        return [r[key] for r in recs]

    def metric(label, getter):
        b = [getter(r[0]) for r in rows]
        c = [getter(r[1]) for r in rows]
        t, n = paired_t(c, b)
        mb, mc = mean(b), mean(c)
        dpct = (mc - mb) / mb * 100.0 if mb else float("nan")
        print(f"{label:24s} base={mb:8.4f} cpp={mc:8.4f} d={mc-mb:+8.4f} ({dpct:+6.1f}%) t={t:+5.2f} n={n}")

    print(f"=== CPP comparison: {args.world}/{args.house} {args.date} (n={args.n}) ===")
    metric("total_kwh", lambda r: r["total_energy_kwh"])
    metric("peak_16_21_kwh", lambda r: peak_kwh(r["load_profile_watts"]))
    metric("valley_22_7_kwh", lambda r: valley_kwh(r["load_profile_watts"]))
    metric("max_watts", lambda r: max(r["load_profile_watts"]))

    appliances = sorted({a for r in rows for a in r[1]["per_appliance_kwh"]})
    for a in appliances:
        metric(a, lambda r, a=a: r["per_appliance_kwh"].get(a, 0.0))

    print("\nhourly mean kWh (base -> treat):")
    base_h = [0.0] * 24
    treat_h = [0.0] * 24
    for b, c in rows:
        for h in range(24):
            base_h[h] += sum(b["load_profile_watts"][h * 60:(h + 1) * 60]) / 60.0 / 1000.0
            treat_h[h] += sum(c["load_profile_watts"][h * 60:(h + 1) * 60]) / 60.0 / 1000.0
    n = len(rows)
    for h in range(24):
        mb, mt = base_h[h] / n, treat_h[h] / n
        print(f"  {h:02d}:00  {mb:6.3f} -> {mt:6.3f}  ({mt-mb:+6.3f})")

    # paired per-env peak table
    print("\nper-pair peak_16_21_kwh (base -> cpp):")
    for i, (b, c) in enumerate(rows, 1):
        pb, pc = peak_kwh(b["load_profile_watts"]), peak_kwh(c["load_profile_watts"])
        print(f"  pair {i}: {pb:.3f} -> {pc:.3f}  ({pc-pb:+.3f})")


if __name__ == "__main__":
    main()
