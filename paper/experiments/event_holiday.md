# Event — Public holiday (`holiday`)

## 1 Research Question
Can a **social/structural** natural-language event — a public holiday — change aggregate
household electricity behaviour, and by how much? (RQ2: behavioural transmission.)

## 2 Hypothesis & Expected Effect
A public holiday keeps residents at home (no work/school), raising **daytime** occupancy → higher
daytime appliance use (lighting, TV, cooking) and higher **total** energy, with the **evening peak**
roughly unchanged. Directionally the same mechanism as `lockdown` (Xia et al. 2026), but milder
(no stay-at-home mandate).

## 3 Experimental Setup
- World `world_838587` house_0002 (1 member, cooking-dominated evening peak).
- `--event-template "2026-09-11|holiday"`; same-era interleaved baseline, **n=15** each arm.
- `python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env hol_h_i --event-template "2026-09-11|holiday" --workers 1`.

## 4 Metrics
Total energy (kWh), evening-peak 16–21h energy, valley 22–07h energy, max power (W), per-appliance kWh.

## 5 Results (n=15, paired t, df=14)
| Metric | baseline | holiday | Δ | t | p |
|---|---|---|---|---|---|
| **Total energy** | 8.239 | 12.220 | **+48.3%** | **+4.68** | **0.0004** |
| Peak 16–21 | 3.395 | 3.661 | +7.8% | +0.74 | 0.47 (n.s.) |
| Valley 22–7 | 1.963 | 1.458 | −25.7% | −1.27 | 0.23 (n.s.) |
| Max power | 3667 | 4066 | +10.9% | +1.01 | 0.33 (n.s.) |
| kitchen_light | 0.069 | 0.133 | +92.9% | +5.90 | <0.001 |
| living_room_light | 0.088 | 0.197 | +125.4% | +5.01 | <0.001 |
| living_room_tv | 0.347 | 0.572 | +64.7% | +3.53 | 0.003 |
| InductionCooker | 2.567 | 3.478 | +35.5% | +4.04 | 0.001 |

## 6 Comparison with Literature
Xia et al. (2026): empirically grounded LLM agents reproduce human behaviour shifts during
disruptions (stay-home → daytime demand up). The holiday result (+48.3% total, lighting/TV/cooking
up) is the same mechanism as `lockdown` (daytime **+220.7%**, R107) but milder. Plan §4.3 Phase Three
names public holidays as a target event — this fills that gap.

## 7 Validity Check
- same-era paired, n=15; **single household × single world × single day** → **cross-world replication
  pending** (project red line 3). Not yet promoted to headline.
- No prompt directive beyond the factual holiday statement (natural-language injection only).

## 8 Conclusion
Public holiday = a significant **stay-home** effect: **+48.3% total energy (p≈0.0004)**, driven by
lighting/TV/cooking; evening peak not significantly changed. Replicates the `lockdown` mechanism at
milder intensity. Cross-world replication required before headline status.
