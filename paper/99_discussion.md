# 99 — Discussion（草稿）

> 状态：草稿，随实验推进更新。仅记录**已产生（含初步）有效果**的内容；过程证据见 `reports/`。

## RQ1 — Heterogeneous population

- Implemented: structured personality (big_five / energy_awareness) derived deterministically;
  room/appliance dedup; 28-type catalog with physical parameters.
- Verified offline (L1) and on a real 2-day run (personality fields present on all members).
- Open: population-scale generation and distributional validation vs real aggregate load.

## RQ2 — Behavioural transmission of external inputs

> **Summary**: **seven** results are statistically significant across three worlds — **heatwave → cooling**
> (baseline AC 0/9 vs 11/12, two-sided p≈0.00003), **lockdown → stay-home** (Out 13/13 → 1/13,
> p≈0.000003, plus a judgeable **+220.7% daytime-load magnitude**, same-era n=9, p≈0.010), **cold-snap → heating**
> (0/10 vs 6/10, two-sided p≈0.011), **air-conditioner peak tax → AC-off/peak-shaving** under
> heatwave (AC-on 15/15→7/15, p≈0.0022; peak −22.5%/−24.6%/−20.6% across three worlds, R118/R120/R122/R125),
> and a **stay-home family** of structural shocks that raise total energy across three worlds —
> **public holiday** (+19%…+65%, p≤0.019, R166–R186), **work-from-home** (+28.7%/+30.6%/+30.6%, p≤0.014,
> R191–R193) and **transport strike** (+22.2%/+29.3%/+33.9%, p≤0.039, R196–R198). Other interventions are
> directional, inconclusive, or null (below).

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
- **Public holiday (cross-world, significant)**: a factual `holiday` event (no stay-home mandate) raised
   **total energy** by +48.3% / +31.9% / +39.8% across three worlds (n=15 each; p=3.5e-4 / 3.8e-7 / 0.0014),
   driven by **stay-home** appliance use (kitchen light +93%/+93%, living-room TV +65%/+109%, induction
   cooker +34%/+36%). Same mechanism as lockdown, milder. The **peak effect is not robust** (three worlds:
   +7.8% n.s. / +24.9% / −15.2% n.s.) and is deliberately **not claimed**.
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
   (Replicated on a second household, R149: cooker −1.64 → oven +1.02 / microwave +0.76, total peak +0.23.)
   **Not universal (R211)**: on world_172148 h001 (all 5 members) the cooker-tax left the cooker
   **byte-identical** (total peak −2.4% n.s.) — the substitution path is event/household-specific.
  **Population-level composition (R151)**: scanning every house, the evening peak is **cooking-dominated
  in most of them** (InductionCooker 27–54% of the window), so those peaks are substitution-bound;
  only AC-dominated houses (e.g. world_143345 house_0003, AC 28%) expose a shaveable peak. This unifies
  the mechanism: *whether a house's peak can be shaved depends on whether its dominant peak device is
  substitutable.* **Cooking resists shaving even with a price signal (R156)**: a 10% *induction-cooker
  peak tax* cut the cooker's own peak load only −9.6% (n.s.) and left the total peak unchanged (−3.9%,
  n.s.; microwave partly substituted) — whereas the non-substitutable AC responds strongly to `ac_tax`.
   So substitutable (cooking) peaks are hard to shave under *both* informational and price framings.
   **Water-heater targeting is also ineffective (R147/R182/R183)**: three tests left the water-heater
   peak unchanged (and, on two worlds, raised the *total* peak, R182/R183) — consistent with the
   requirement that a *device that actually responds* (AC), plus the window, is what shaves.
   **`ac_tax` is conditional on the AC running (R188)**: without a heatwave the AC load is 0 and
   `ac_tax` has no effect (peak −4.1%, n.s.) — event effects are baseline/appliance-state dependent.
- **Future-oriented notices (world-specific, R141/R142/R146)**: on `world_838587` house_0002 a *future*
  TOU-tariff announcement and a community notice **increased** current total energy (+20.8%, p≈0.0001,
  n=15; +11.0%, p≈0.026, n=15) with no peak change, while a neutral custom event did not (+7.9%, n.s.).
  **However the announcement did not replicate on `world_172148` (−1.6%, n.s., R146)** — it is a
  **house/world-specific** effect, not a general mechanism, and is **excluded from headline claims**
  (cross-world replication requirement, R128). **Generic custom events inflate load on that house
  (R157)**: a *generic* evening-peak tax raised the total peak +18.9% (n=9) — the same house-specific
  reactivity — further confirming that `ac_tax`'s peak-shaving requires **device+window joint
  anchoring**, not a generic window signal.
- **Critical-peak pricing (`cpp`) — peak null, world-specific saving (R161/R163)**: a 17:00–20:00
  high-price event **did not shave the peak** on either of two worlds (W1 −2.7%, W2 +13.0%, both n.s.,
  n=15) — misaligning with Faruqui & Sergici (2010)'s 13–20% CPP benchmark. Its **total-energy** drop was
  **world-specific** (−14.4%, p=0.007 on world_838587; −4.3% n.s. on world_172148) and left the valley
  unfilled → load **conserved, not shifted** (R162). A facts-only control (`cpp_soft`) gave the same
  qualitative result (−10.9% total, peak n.s.), so the effect is driven by the high-price fact.
- **Uniform electricity tax (`tax_uniform`, Gunkel et al. 2023) — null (R164)**: total +5.6%, peak +10.7%
  (both n.s., n=15) → a generic tax framing does not change behaviour (consistent with `price_hike`
  withdrawal and the generic-tax rebound, R157).
- **Injection-path confound ruled out (R165)**: preset vs custom injection with **byte-identical** content
  differed on **no** metric (n=15) → the path is not a confound; earlier preset/custom divergence reflects
  **content + small samples** (R159/R165).
- **Valley-filling direction, underpowered (R185)**: a "free electricity 12:00–14:00" event raised midday
  load +90% nominally (0.20→0.39 kWh) but **n.s.** (p=0.31, n=15) — direction consistent with price
  response, but the absolute effect is below the noise floor (R057/R058).
- **Cost context makes TOU shifting detectable (R200/R201)**: injecting a concrete per-appliance
  peak/off-peak **cost table** *plus explicit authorization to reschedule flexible loads off-peak*
  turns the otherwise-null TOU into a significant **shift**. Versus a *no-policy* baseline (shared
  s4-only timeline, n=15) the effect is **peak −13.2%** (p=0.0018) and **valley +25.6%** (p=2.3e-5),
  total unchanged; versus TOU-text-only the table alone adds peak −7.2% / valley +16.6%. Without the
  authorization clause the same table had **no** effect (peak −0.1%). This is the platform's **first
  detectable price response** — the lever is concrete, actionable information, not the price text.
- **Price-elasticity dose–response (R205)**: with the cost context on both arms, a larger peak/valley gap
  (0.5→1.2 AUD, 2.4×) significantly increases shifting — peak **−7.3%** (p=0.0095), valley **+14.8%**
  (p=0.014). Without the cost context the same gap change had **no** effect (R180). The platform therefore
  exhibits a measurable **price elasticity** once the trade-off is made concrete.
- **Price-sensitivity heterogeneity (R207)**: holding the tariff + cost context fixed, a high
  cost-consciousness persona shifts significantly more than a low one (peak **−7.0%**, valley
  **+14.6%**, p=0.014) — the platform reproduces **heterogeneous price response** (Costa & Kahn 2010;
  Wang et al. 2021). The level is now **derived from persona traits** (`energy_awareness` /
  `conscientiousness`) and auto-injected (R213).
- **Multi-day bill feedback (R208/R210)**: injecting yesterday's bill / peak cost (`--bill-feedback`)
  does **not** change day-2 behaviour. With a **shared day-2 timeline** (R210) the effect is a clean
  **null** (peak −0.7%, n.s.); the earlier "increase" (R208) was plan-level variance. The single-day cost
  context works but does **not accumulate** — the **habit/learning channel is not supported** (consistent
  with the R140 timeline null).
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
- **Household scale economies (R150)**: per-capita daily energy falls with household size (1→9.74,
  2→~7.1, 4→4.96, 5→3.12, 6→5.33 kWh), qualitatively aligning with Schröder et al. (2013).
- **Cross-day variability (R152)**: households differ widely in regularity (variability index
  0.26–0.44; peak-hour shift 0.5–11 h) — supporting heterogeneous behaviour.
- **Weekday/weekend (R176/R195)**: 5 households × 7 days give weekend-vs-weekday changes of **+3.1% … +44.9%**,
  and the weekend effect **correlates with the household's holiday effect (r=0.82, n=5)** — both share the
  same **stay-home dose** (time normally away on weekdays). Weekend = a periodic holiday.
- **Household load-shape archetypes (N9, R178)**: six baseline households split into **evening-peak (18h,
  eve 45%) / morning-peak (7h, 37–41%) / late-night (21h)** types — real inter-household heterogeneity
  (RQ3); still descriptive (6 households, single member each).
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
