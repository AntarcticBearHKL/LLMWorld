# Event — Transport strike (`transport_strike`)

## 1 Research Question
Does a **transport disruption** that keeps commuters at home raise aggregate household electricity use,
like the holiday/lockdown/wfh events? (RQ2.)

## 2 Hypothesis & Expected Effect
A public-transport strike keeps would-be commuters at home during the day → higher daytime appliance use
and **higher total** energy; the same stay-home mechanism as `holiday`, `wfh`, and `lockdown`.

## 3 Experimental Setup
- Worlds `world_838587` h002 and `world_172148` h002; `--member 0`, date 2026-09-11.
- `--event-template "2026-09-11|transport_strike"`; same-era interleaved baseline, **n=15** each arm.
- `python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env ts_t_i --event-template "2026-09-11|transport_strike" --workers 1`.

## 4 Metrics
Total energy (kWh), evening-peak 16–21h energy, valley 22–07h energy, max power (W).

## 5 Results (n=15, paired t, df=14)
| Metric | W1 `838587` h002 | W2 `172148` h002 | W3 `143345` h002 |
|---|---|---|---|
| **Total energy** | **+33.9%** (p=0.028) | **+22.2%** (p=4.2e-4) | **+29.3%** (p=0.039) |
| Peak 16–21 | +5.4% (n.s.) | +17.6% (p=0.041) | +15.8% (n.s.) |
| Valley 22–7 | −10.0% (n.s.) | −30.6% (p=0.076) | −10.7% (n.s.) |

Total energy is **+22% … +34% across all three worlds** (all significant).

## 6 Comparison with Literature
Same **stay-home** mechanism as holiday (R166–R188), wfh (R191–R193) and lockdown (R068/R107, Xia et al.
2026). A transport disruption is a non-mandated, non-calendar shock that reproduces the effect.

## 7 Validity Check
- same-era paired, n=15; **three worlds**; total replicates at +22.2%/+29.3%/+33.9% (all significant).
- **Cross-world replicated (red line 3 satisfied) → promoted to headline.**
- Single member (M1) per household.

## 8 Conclusion
A transport strike significantly **raises total energy** (+22.2% / +29.3% / +33.9% across three worlds) —
the 3rd stay-home headline (after `holiday` and `wfh`), further generalising the "time-at-home → daytime
load" mechanism.
