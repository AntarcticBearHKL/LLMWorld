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
| Metric | W1 `838587` h002 | W2 `172148` h002 | W3 `143345` h002 |
|---|---|---|---|
| **Total energy** | **+30.6%** (p=0.006) | **+28.7%** (p=6.3e-5) | **+30.6%** (p=0.014) |
| Peak 16–21 | +17.5% (p=0.044) | +27.4% (p=0.007) | +8.1% (n.s.) |
| Valley 22–7 | −9.0% (n.s.) | −15.8% (n.s.) | +0.2% (n.s.) |
| Max power | −8.9% (n.s.) | +21.0% (p=0.039) | +6.2% (n.s.) |

Total energy is **+28.7% … +30.6% across all three worlds** — the most consistent event effect in the study.

## 6 Comparison with Literature
Same **stay-home** mechanism as the holiday (R166–R188) and lockdown (R068/R107, Xia et al. 2026) events:
a structural change in time-at-home raises daytime demand. The `wfh` signal generalises the mechanism to
a non-mandated, non-calendar work arrangement.

## 7 Validity Check
- same-era paired, n=15; **three worlds**; total effect replicates at +28.7%/+30.6%/+30.6% (all significant).
- **Cross-world replicated (red line 3 satisfied) → promoted to headline.**
- Single member (M1) per household; peak direction is world-dependent (assert total only).

## 8 Conclusion
A work-from-home event significantly **raises total energy** (+28.7% / +30.6% / +30.6% across three
worlds) — the second stay-home event (after `holiday`), generalising the "time-at-home → daytime load"
mechanism. This is the most **consistent** event effect in the study (three worlds within 2 pp).
