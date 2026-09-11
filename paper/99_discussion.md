# 99 — Discussion（草稿）

> 状态：草稿，随实验推进更新。仅记录**已产生（含初步）有效果**的内容；过程证据见 `reports/`。

## RQ1 — Heterogeneous population

- Implemented: structured personality (big_five / energy_awareness) derived deterministically;
  room/appliance dedup; 28-type catalog with physical parameters.
- Verified offline (L1) and on a real 2-day run (personality fields present on all members).
- Open: population-scale generation and distributional validation vs real aggregate load.

## RQ2 — Behavioural transmission of external inputs

> **Summary**: **four** results are statistically significant across three worlds — **heatwave → cooling**
> (baseline AC 0/9 vs 11/12, two-sided p≈0.00003), **lockdown → stay-home** (Out 13/13 → 1/13,
> p≈0.000003, plus a judgeable **+220.7% daytime-load magnitude**, same-era n=9, p≈0.010), **cold-snap → heating**
> (0/10 vs 6/10, two-sided p≈0.011), and **air-conditioner peak tax → AC-off/peak-shaving** under
> heatwave (AC-on 15/15→7/15, p≈0.0022; peak −22.5%/−24.6%/−20.6% across three worlds, R118/R120/R122/R125).
> Other interventions are directional, inconclusive, or null (below).

- **Heatwave (binary signal, statistically significant)**: a natural-language heatwave event causes
  agents to switch the air-conditioner on. Aggregating all post-fix runs **across three independent
  worlds**, the AC was active in **0/9** baseline vs **11/12** heatwave member-days (Fisher two-sided
  **p ≈ 0.00003**, p<0.0001); direction
  consistent with Xia et al. (2026). Individual heterogeneity is visible (one heatwave member did not
  use it). **Key validity condition**: the news text must agree with the environment weather,
  otherwise agents ignore it (observed failure → fixed by event↔weather linkage). Note that the
  single-sample *total-energy* increases (+17%~+64%) are noise-dominated (cf. noise floor, R057) and
  are not claimed.
- **Cold-snap (binary signal, significant)**: a `cold_snap` event switched heating devices from off to
  on — baseline **0/10** vs **6/10** (Fisher two-sided **p ≈ 0.011**, across three worlds, R093).
  Activation probability (60%) is lower than the heatwave's (~92%) — response robustness differs by event.
- **Economic / warning events — WITHDRAWN (baseline-drift artifact)**: apparent peak-window cuts
  (`blackout_risk` −31.7%, `price_hike` −17.9%) were an artifact of comparing against **older baseline
  runs**: fresh identical baselines (mean 3.441 kWh) overlap the event runs (2.9–3.8), and even a
  **neutral** event cut "peak-window" by −32.9% (R104). **Continuous metrics drift systematically
  across session time**; only **binary/structural** signals (device on/off, home/out) are drift-immune.
  This is a core methodological finding.
  **Same-era re-verification (R106)**: the three binary event results — heatwave → AC, cold-snap →
  heating, lockdown → out-of-home=0 — all reproduce against fresh same-era baselines, confirming
  **binary/structural signals are drift-immune** while continuous ones are not.
  **Small-sample hazard (R112/R114)**: continuous-effect magnitudes are unreliable at n=3 or n=9 —
  TOU gave −17.5% (n=3) → +13.1% (n=9) → −3.2% (n=15, n.s.). Continuous magnitudes require **n≥15**.
- **Lockdown (binary signal, strongest)**: a `lockdown` event removed almost all out-of-home time —
  baseline **13/13** member-days had out-of-home activity vs **1/13** under lockdown (Fisher two-sided
  **p ≈ 0.000003**), across three worlds; daytime (9–17) load rose (+294% in the single-instance case,
  R068/R069/R086). The clearest causal chain in this work.
- **Peak-shaving is conditional on the house's appliance-time structure**: reducing the *peak*
  requires the intervention to actually lower **peak-window** load, and whether it does is
  house-specific. On `world_838587` (bedroom AC, used mostly overnight) a targeted non-price request
  (avoid the AC 5–8pm, R126) cut AC/total (−58.3%/−28.4%) but left the peak unmoved (+12.2%, n.s.),
  whereas the targeted *tax* (`ac_tax`) shaved it (−22.5%); on `world_172148` (living-room AC, an
  evening load) the **same** non-price request cut the peak (−25.5%, t=−4.81, 9/9) (R128). So the
  earlier "price × targeting" 2×2 (R126) does **not** generalize — the operative condition is whether
  the intervention lowers peak-window load, which depends on where/when the targeted appliance runs.
  `energy_crisis`/`storm` (pure information) changed nothing in either world. This is consistent with
  the baseline-specificity of event effects (R082/R083) and reinforces the **cross-world-replication
  requirement** (alongside R104 drift and R114 small-sample). Note also **energy-saving ≠ peak-shaving**:
  a request can slash total AC use while leaving the peak (dominated by non-AC loads) unmoved.
  **Quantified (R130/R131)**: peak-decomposition (total peak minus non-AC peak) reveals **two shaving
  paths**. (A) *Device-targeted* signals (e.g. avoid the AC 5–8pm) can only remove the device's own
  peak-window load, so their ceiling is the **device's peak share** — 5% on world_838587 (nocturnal
  bedroom AC) → no peak effect, vs 30% on world_172148 (evening living-room AC) → peak −25.5%.
  (B) *Window+price* signals (`ac_tax`) additionally move **non-AC** evening load (non-AC peak
  −0.30 kWh), so they shave the peak even when the device share is modest (−22.5% on world_838587).
  Caveat: the device's peak share is itself **batch-stochastic** (world_838587 baseline AC-peak share
  was 5% in one batch, 15% in another) — another instance of the drift red line. The earlier
  "price × targeting" 2×2 is thus a special case, not the mechanism.
  **3-world dose–response (R135)**: the *total*-peak effect of a device-targeted request tracks the
  device's **absolute peak-window load × achieved behaviour-change rate** — world_838587 (AC-peak
  0.16 kWh) → no effect (+12.2%), world_143345 (AC-peak 1.27 kWh, AC-peak −44.7%) → −10.0% (n.s. at
  n=9), world_172148 (AC-peak 1.62 kWh, AC-peak −63%) → −25.5% (significant). Monotone across worlds,
  supporting the mechanism; the worlds differ in AC location (bedroom/living-room) and hence in the
  AC's peak-window dose.
  **Substitution constraint (R144)**: targeting a device shaves the *total* peak only if that device is
  **not substitutable**. Requesting avoidance of the induction cooker (49.8% of the peak) cut its own
  peak-window load by **−99.7%** but the agent switched to the **oven (+0.93 kWh) and microwave
  (+0.70 kWh)**, leaving the total peak unchanged (−0.2%). Non-substitutable cooling (AC) does shave the
  peak; substitutable cooking does not. The dose law is therefore bounded by appliance substitutability.
- **Future-oriented notices raise current consumption (R141/R142)**: a *future* TOU-tariff announcement
  and a community outage notice both **increased** current total energy (+20.8%, p≈0.0001, n=15;
  +11.0%, p≈0.026, n=15) with no peak change, whereas a neutral custom event did not (+7.9%, n.s.).
  "Plan-ahead" notices thus perturb behaviour toward *more* current use — the opposite of conservation,
  and distinct from the null grid-information events (`energy_crisis`/`storm`).
- Pricing interventions: **TOU is null at adequate power.** With a drift-free same-era interleaved
  design, the peak-shaving claim collapses as n grows: n=3 gave −17.5%, n=9 gave +13.1% (total), and
  **n=15 gave peak −3.2% / total +5.4% (both n.s.)** (R111/R112/R114). The earlier apparent
  direction-reversal under different sampling (R026) was confounded by cross-time drift. Net: no TOU
  effect is resolvable at this noise floor.
- Social norms: **nudge not robust** — an initial small sample looked consistent (5/5 member-days
  negative, −5.8%~−23.3%), but a larger sample on a fresh world (7 members) had **3 members increase**
  and within-group spread (±25~45pp) far exceeding any group difference (R054). The de-instructionalized
  `nudge_soft` ablation (R040) still indicates the response hinges on normative wording.

## RQ3 — Emergent patterns & empirical alignment

- Group-response analyzer ready (`analyze_groups.py`); awareness labels fixed to avoid single-group
  degeneracy, and a fresh world with non-degenerate labels was generated (R052).
- Group heterogeneity: a preliminary direction (Medium awareness reduces more than Low under nudge)
  was **not statistically meaningful** — within-group variance dominated the between-group difference
  (R053/R054). Group experiments require large samples.
- Multi-world comparison tool restored (`compare_worlds.py`).
- Pending: systematic alignment tables vs the benchmarks in `FIT5216/研究计划.md` §2.7.

## RQ4 — Scalability

- Parallel scheduling (`ThreadPoolExecutor`), `--s4-only` reuse, `--member/--house/--days` scoping,
  and prompt caching are in place; distillation not yet implemented.

## Threats to validity — prompt over-compliance

Across interventions the simulated **magnitude tends to exceed the empirical benchmark even when the
direction is right**: TOU peak −18%~−26% vs the −3~6% plain-TOU range (R23/R24/R26), and fixed-nudge
total −6%~−10% vs −1~3% (R37). Two observations:

1. **Fragility**: for TOU the direction *reverses* under a low-variance / no-thinking setting (R26),
   and a within-arm "rebound" after policy removal was **overturned by a parallel no-policy control**
   (R45 → R46), so single-member / single-run magnitudes are not trustworthy. In general, differences
   between two independently sampled runs are comparable to, or larger than, the treatment effect.
2. **Over-compliance**: this pattern is consistent with LLM agents over-complying with explicit
   natural-language directives, rather than the smaller, habit-bound responses of real households
   (cf. Wang et al. 2021, who find habits dominate price effects). **Direct evidence**: removing the
   normative phrasing from `nudge` (`nudge_soft`, R040) collapsed the total-energy effect from
   −6%~−10% to ≈0, so the response is driven by the directive, not the information.

**Quantified noise floor**: three *identical* baseline runs (same world/house/member/date; no policy/event)
gave total energy 7.37 / 8.19 / 9.80 kWh — mean 8.45, std 1.01 (CV ≈12%), max **+33%** above min (R057).
Any single-run treatment difference below this scale is uninterpretable, which is why single-sample
"effects" (nudge 5/5, TOU reversals, the R045 rebound) did not survive replication.

**World/date-specific baselines**: control values are not universal — e.g., a heating baseline that was
0 in two worlds was already non-zero (3.0 / 1.5 kWh) in a third (R082). Event effects (heatwave
0/7→9/10, lockdown 7/7→0/7) are therefore *conditional on the baseline device/appliance state*;
experiments should use paired (within-subject) designs or verify the baseline per case.

**Mitigation**: provide de-instructionalized variants (`tou_soft`, `nudge_soft`) and compare; and, for
any magnitude claim, average across multiple households/members at a fixed weekday. Accordingly, this
work treats the platform as suited to **direction** and **heterogeneity** claims, with absolute
magnitude calibration left as future work.

Relatedly, **framing effects are unstable**: the loss-framed `nudge_loss` did not beat the plain
`nudge`; it *raised* total energy (+6% vs nudge's −6%~−10%, R041), contradicting Ghesla et al. (2019).
Both the over-compliance and the framing results point to **wording-driven** rather than
information/psychology-driven behaviour in the current agents.

## Limitations

- Event results are **binary / large-effect** (device on/off; out-of-home yes/no) and hold across three
  worlds, but **continuous magnitudes cannot be resolved** at the observed noise floor (CV≈12%,
  R057/R058) — only large effects (≳10–20%) are detectable, so literature-scale (~3%) magnitudes are
  not claimed. Continuous claims additionally require **n≥15** (R112/R114).
- Weather is currently a stub; event effects use a fixed temperature offset.
- Refactor-era drift is resolved: `engine/news.py`, `compare_worlds.py`, all documented policies
  (`tou`/`tou_soft`/`nudge`/`nudge_soft`/`nudge_loss`/`subsidy`/`peak_demand`/`ev_delay`/
  `night_setback`/`in_home_display`), `--community-notice`, `--policy-schedule`, and `--peer-nudge`
  are restored (the guide's `population_runner.py` role is now covered by `run.py`).

## Next steps

1. Extend the significant event set (e.g. storm) and add `analyze_event_response.py` transition metrics.
2. Large-N (multi-seed) averaging for any *magnitude* claim — per the power analysis (R058) this is
   high-budget; magnitude alignment remains future work.
3. Generate an EV-containing world to run `subsidy` / `ev_delay`.
