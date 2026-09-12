# Event — Work-from-home day (`wfh`)

## 1 Research Question
Does a **structural stay-home** social event — a work-from-home day — raise aggregate household
electricity use, like the holiday and lockdown events? (RQ2.)

## 2 Hypothesis & Expected Effect
Working from home instead of commuting keeps residents home during the day → higher daytime appliance
use (lighting, cooking, computers) and **higher total** energy; the same mechanism as the `holiday` and
`lockdown` events.

## 3 Experimental Setup
- Worlds `world_838587` h002 (1-person) and `world_172148` h002 (2-person); `--member 0`, date 2026-09-11.
- `--event-template "2026-09-11|wfh"`; same-era interleaved baseline, **n=15** each arm.
- `python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env wfh_t_i --event-template "2026-09-11|wfh" --workers 1`.

## 4 Metrics
Total energy (kWh), evening-peak 16–21h energy, valley 22–07h energy, max power (W).

## 5 Results (n=15, paired t, df=14)
| Metric | W1 `838587` h002 | W2 `172148` h002 |
|---|---|---|
| **Total energy** | **+30.6%** (t=3.25, p=0.006) | **+28.7%** (t=5.62, p=6.3e-5) |
| Peak 16–21 | +17.5% (p=0.044) | +27.4% (p=0.007) |
| Valley 22–7 | −9.0% (n.s.) | −15.8% (n.s.) |
| Max power | −8.9% (n.s.) | +21.0% (p=0.039) |

## 6 Comparison with Literature
Same **stay-home** mechanism as the holiday (R166–R188) and lockdown (R068/R107, Xia et al. 2026) events:
a structural change in time-at-home raises daytime demand. The `wfh` signal generalises the mechanism to
a non-mandated, non-calendar work arrangement.

## 7 Validity Check
- same-era paired, n=15; **two worlds**; effect replicates (total +28.7%/+30.6%, both significant).
- **Cross-world** replication pending on the 3rd world (red line 3); not yet promoted to headline.
- Single member (M1) per household; peak direction is more consistent than for `holiday`.

## 8 Conclusion
A work-from-home event significantly **raises total energy** (+28.7% / +30.6% across two worlds) — the
second stay-home event (after `holiday`), generalising the "time-at-home → daytime load" mechanism.
Pending a 3rd world for full cross-world headline status.
