# LLM Society: A Multi-Agent Generative Framework for Population-Level Residential Behaviour Simulation and Natural-Language Policy Intervention

**Hongkun Lyu** (Student ID 35933771) — Supervisor: Hao Wang
*FIT5216 — consolidated paper draft, 2026-09-12*

---

## Abstract

We present **LLMWorld**, a population-level multi-agent framework in which each household is an
autonomous LLM-driven agent whose day is planned from a structured profile and then translated into a
minute-resolution, appliance-level electricity load. Every external input — prices, taxes, rebates,
social norms and news events — is injected **only as natural language**; aggregate behaviour is
emergent. We run a large battery of controlled experiments on three heterogeneous synthetic worlds
following four validity rules (same-era baselines, n≥15, cross-world replication, content-contrast),
and obtain **seven statistically significant, cross-world event results**: heatwave→cooling
(0/9→11/12, p≈3e-5), lockdown→stay-home (13/13→1/13, p≈3e-6), cold-snap→heating (0/10→6/10,
p≈0.011), air-conditioner peak tax→AC-off (15/15→7/15, p≈0.0022), and a **stay-home family** —
holiday, work-from-home and transport-strike — that each raise total energy by ~20–65% (p≤0.039).
We further show that **concrete, per-appliance peak/off-peak cost figures** turn otherwise-null time-of-use
and critical-peak prices into significant peak-shifting (peak −3.5…−13.2%, valley +8.2…+27.9% across
three worlds), and we *decompose* this effect: the cost information alone already produces a significant
valley shift (+11.6%), while an explicit authorization to reschedule strengthens peak shaving (−8.1%).
We characterize **when peak shaving works** — a dose law bounded by appliance substitutability, requiring
a *device × window* anchoring — and provide an adversarial **validity audit**: we withdraw a previously
reported peak-shaving result that does not survive a shared-timeline replication, and label every
conclusion as robust / prompt-sensitive / withdrawn. The work contributes an end-to-end
behaviour→appliance→load pipeline, a natural-language intervention surface with emergent effects, and a
mechanistic account of peak shaving together with its capability boundary.

**Keywords**: LLM agents; residential load; demand response; natural-language intervention; emergent
behaviour; validity.

---

## 1 Introduction

Residential electricity demand is increasingly shaped by distributed resources (rooftop PV, batteries,
electric vehicles, heat pumps) and by heterogeneous household behaviour. Classical top-down forecasting
treats households as an undifferentiated mass, while classical bottom-up models (ARGOS, Markov-chain
activity models) encode behaviour as fixed states and transition probabilities, making them ill-suited to
capture contextual decisions or responses to textual/complex signals (Capasso 1994; Widén & Wäckelgård
2010; Richardson 2010). LLM-based generative agents (Park et al. 2023) offer a far more expressive
behavioural engine, but existing LLM energy-simulation work is largely single-household or small-scale
(Chetty et al. 2025; Almashor et al. 2024) and has not been systematically validated against empirical
demand-response benchmarks at population level.

This paper asks:

- **RQ1 — Large-scale heterogeneous population simulation.** Can LLM agents generate realistic,
  diverse minute-resolution household load profiles? *(Population-scale generation and distributional
  validation are out of scope here; the population machinery exists but is exercised at ≤5 households,
  and RQ4/RQ1-at-scale are future work.)*
- **RQ2 — Behavioural transmission of external inputs.** When tariffs, taxes, subsidies, norms or news
  events are injected as natural language, how do agents respond at the appliance-decision level?
- **RQ3 — Emergent patterns & empirical alignment.** Do aggregate responses match the empirical
  literature, and do phenomena beyond individual behaviour emerge?
- **RQ4 — Scalability & practicality.** *(Explicitly out of scope: distillation and hundreds-of-agents
  scaling are not pursued.)*

**Contributions.**
1. An end-to-end pipeline **behaviour → appliance decision → minute-resolution load** driven by LLM agents.
2. A **natural-language intervention surface** (pricing / norms / events / cost-context) whose effects
   are emergent (no hard-coded behaviour).
3. **Seven cross-world significant event results** plus a validated **price-response capability**,
   benchmarked against the empirical literature.
4. A **mechanistic account of peak shaving** — dose × substitutability × device/window anchoring — and the
   observation that **energy-saving ≠ peak-shaving ≠ load-shifting**.
5. An honest **capability boundary**: where the platform is reliable, where it is prompt-sensitive, and
   what it cannot do — including a withdrawn result.

---

## 2 Related work

### 2.1 From top-down to bottom-up behavioural load modelling
Bottom-up models reconstruct load from household composition, appliance ownership and activity patterns,
but reduce behaviour to finite states / Markov chains (Capasso 1994; Widén & Wäckelgård 2010; Richardson
2010). Agent-based hybrids (Xu et al. 2026) add signal–demand feedback but keep rule-based agents. Their
limitation is precisely the rigidity of behavioural representation — the gap this work attacks.

### 2.2 LLM-based generative agents
Park et al. (2023) established the memory–reflection–planning template; AgentSociety (Piao et al. 2025)
scaled LLM agents to >10,000 urban residents; SALM (Koley 2025) reduced token cost with hierarchical
prompts; Chetty et al. (2025) inferred single-household energy with <10% MAPE; Almashor et al. (2024)
synthesized private-LLM household data; Michelon et al. (2025) parsed natural-language HEMS commands.
Reasoning techniques — CoT (Wei et al. 2022), ReAct (Yao et al. 2023a), ToT (Yao et al. 2023b),
Self-Consistency (Wang et al. 2023) — underpin coherent agent decisions. None of this work provides a
population-level, empirically-aligned *policy-intervention* testbed — our positioning.

### 2.3 Empirical benchmarks (alignment targets)
- **Pricing / demand response**: plain TOU cuts peak 3–6% (Faruqui & Sergici 2010); CPP 13–20%;
  demand charge 10–20% (Escarrega et al. 2025); price effects are often dominated by habit (Wang et al. 2021).
- **Non-price behavioural**: social-norm savings ~1–3%, strongest for high users (Allcott 2011;
  Ayres et al. 2013); loss framing ~5% stronger (Ghesla et al. 2019); monetary incentives crowd out
  social norms (Pellerano et al. 2017); heterogeneous nudge/rebate effects (Murakami et al. 2022);
  ideology-modulated nudges (Costa & Kahn 2010).
- **Information**: real-time feedback triples price elasticity (Jessoe & Rapson 2012); personalized
  feedback (Monacchi et al. 2015).
- **Structural**: household-size economies (Schröder et al. 2013); peer effects on solar adoption
  (Barnes et al. 2022); heating sobriety (Cabezas-Rivière et al. 2025).
- **Disruptions**: empirically-grounding LLM agents improves realism under disruptions (Xia et al. 2026);
  counterfactual simulation (Fidone et al. 2025).
- **Method / economics**: CoRenew (Zhang et al. 2026; LLM-agent policy platform), Eco3S (Wei et al. 2026;
  cross-world ABM), Gunkel et al. (2023; uniform electricity taxation), Zhou et al. (2016;
  ML-based DR targeting — variability predicts DR response).

---

## 3 System

### 3.1 Architecture and entry point
A single entry point `run.py` has two modes:
- `--mode world`: synthesize households — **s1** household types → **s2** persona alignment →
  **s3** household build → **s4** world assembly.
- `--mode simulate`: generate behaviour — **s1** macro plan → **s2** coordination → **s3** contextual
  enrichment → **s4** appliance decisions.

All artefacts are structured JSON under `output/`, so every experiment is reproducible from stored data.

### 3.2 Domain model
A household = **members + rooms + appliances**. Appliances fall into four classes: **on-demand**
(`use`/`idle`), **charging** (`charge_home`/`charge_external`/`use`/`idle`), **cycle** (`run`/`idle`;
fixed energy per run), and **always-on** (auto). A shared catalog (`appliances/catalog.py`) provides
rated power, bounds, always-on daily energy, per-type experiment metadata (flexible/duty/season) and
battery capacity/SoC. Charging appliances are bounded by a battery deficit per day.

### 3.3 Behaviour → load pipeline
1. **Macro plan (s1)** — each member's 00:00–24:00 activity segments, constrained to real rooms, full-day
   coverage, exact adjacency; **cross-day carry-over** prevents teleporting home at midnight.
2. **Coordination (s2)** — reconcile shared activities/resources among members.
3. **Enrichment (s3)** — add detail to each activity.
4. **Appliance decision (s4)** — map activities to appliance operations; validated/repaired against the
   registry (unknown ids repaired by family; out-of-home room operations dropped).
5. **Energy calculation** (`load_model.py`) — minute-resolution load and per-appliance kWh.

### 3.4 Intervention surface (all natural-language)
- **Policies** (`--policy`): TOU / TOU-soft, critical-peak pricing (`cpp`/`cpp_soft`), critical-peak
  rebate (`cpr`/`cpr_soft`), uniform electricity tax (`tax_uniform`), subsidy, demand charge
  (`peak_demand`), EV-delay (`ev_delay`), social norm (`nudge`/`nudge_soft`), loss framing
  (`nudge_loss`), night setback, in-home display; **combinations** (`--policy "tou,nudge"`); **timeline**
  (`--policy-schedule`).
- **News / events** (`--event`, `--event-template`): **13 preset templates** — heatwave, cold_snap,
  storm, price_hike, energy_crisis, ac_tax, rebate, blackout_risk, solar_incentive, lockdown, holiday,
  wfh, transport_strike — plus arbitrary custom events and community notices.
- **Social signals**: `--peer-nudge`, `--community-notice`.

Environment-type presets (heatwave / cold_snap) also adjust the weather context so the text and the
structured weather agree — noted as a caveat in the audit (§7).

### 3.5 Cost-context (new)
Because agents otherwise lack any economic model, we add an optional **cost-context**: given a tariff and
the household's flexible appliances, the s4 prompt receives a concrete money table
(`engine/tariff.py`; `--cost-context`, `--cost-context-mode {strong,soft}`):

```
Flexible-appliance costs under today's tariff (peak 16:00-21:00 @0.90; off-peak 22:00-07:00 @0.18):
- bedroom_1_airconditioner: 1.80 AUD now (peak) vs 0.36 AUD off-peak — save 1.44 per hour
- kitchen_dishwasher:       0.99 AUD now (peak) vs 0.20 AUD off-peak — save 0.79 per cycle
- bathroom_waterheater:     2.70 AUD now (peak) vs 0.54 AUD off-peak — save 2.16 per hour
```

`strong` mode appends an explicit "you MAY move it off-peak" authorization; `soft` mode gives the same
numbers with a neutral instruction (prompt-bias control). A **demand-charge** variant shows each
appliance's kW × rate contribution; a multi-day **bill-feedback** injects yesterday's peak-window cost.

---

## 4 Experimental design and validity controls

**Worlds.** Three synthetic communities are used: `world_838587` (2 households), `world_172148`
(3 households) and `world_143345` (3 households, with EV). Household sizes range 1–6.

**Design.** Each comparison is a paired, interleaved **same-era** baseline-vs-treatment design; most
experiments are run on the s4 stage only (`--s4-only`) against a **shared s1–s3 timeline** where the
intervention acts at the appliance-decision stage, and with **full runs** where the intervention acts at
planning (structural events). Sample sizes are **n=15** per arm unless noted.

**Four validity rules (induced from failure).**
1. **Drift.** LLM-agent continuous behaviour drifts across session time; always compare against a
   *same-era* baseline or rely on *binary/structural* signals (drift-immune).
2. **Power.** Continuous magnitudes are unreliable below **n≈15** (TOU: −17.5%→+13.1%→−3.2% as
   n=3→9→15). The noise floor is std≈1.0 kWh (**CV≈12%**); literature-scale effects (3–6%) are below it.
3. **Cross-world.** Mechanistic claims require replication across worlds.
4. **Content, not channel.** Preset vs custom injection with *identical content* differ on no metric —
   the operative variable is the content, not the injection path.

---

## 5 Results

### 5.1 Disruption / environment events (cross-world, significant)
| Event | Evidence | Significance |
|---|---|---|
| **Heatwave → cooling** | baseline AC 0/9 vs heatwave 11/12 | Fisher two-sided p≈3e-5 |
| **Lockdown → stay-home** | out-of-home 13/13 → 1/13; daytime +220.7% (same-era n=9) | p≈3e-6; magnitude p≈0.010 |
| **Cold-snap → heating** | 0/10 vs 6/10 | p≈0.011 |

These reproduce the disruption-robustness argument of Xia et al. (2026). The lockdown daytime magnitude
is large; we assert only the *direction* (see audit §7).

### 5.2 The stay-home family (cross-world, significant)
Three structural "stay at home" shocks each significantly raise **total energy**, across three worlds:

| Event | Total-energy change (W1 / W2 / W3) | Significance |
|---|---|---|
| **Holiday** | +19% … +65% (7 households) | p≤0.019 (7/7 households) |
| **Work-from-home** | +30.6% / +28.7% / +30.6% | p≤0.014 (remarkably consistent) |
| **Transport strike** | +33.9% / +22.2% / +29.3% | p≤0.039 |

The mechanism is **time-at-home**: the effect scales with how much the household is normally *away*
during the day (holiday effect vs baseline daytime share r=−0.47; weekend-vs-weekday effect vs holiday
effect r=0.82). Weekends reproduce the same effect periodically. The evening-peak direction is
household-dependent and is **not** asserted.

### 5.3 Price response — and what makes it work
Pure text pricing is **null** (e.g., TOU peak −3.2%, n=15, n.s.). Adding the **cost-context** turns it on:

| Comparison | Peak 16–21 h | Valley 22–7 h |
|---|---|---|
| TOU + cost vs baseline (3 worlds) | **−13.2% / −5.0% / −3.5%** | **+25.6% / +8.2% / +8.8%** (p≤0.035) |
| CPP + cost vs baseline | **−12.2%** (p=0.004) | **+23.2%** |
| CPR (rebate) + cost vs baseline | **−13.7%** | **+27.9%** |
| **facts-only** cost vs baseline | −5.5% (n.s.) | **+11.6% (p=0.019)** |
| strong (authorized) vs facts-only | **−8.1% (p=0.031)** | **+12.5% (p=0.028)** |

**Decomposition.** The concrete money figures *alone* already produce a significant **valley shift**;
an explicit rescheduling authorization adds a further significant **peak reduction**. Hence the platform
"understands prices" insofar as the trade-off is made **concrete**, and the effect is **not** pure
instruction-following — but it is not a clean economic elasticity either (see audit §7).

**Dose-response and heterogeneity.** A larger price gap produces more shifting (peak −7.3% / valley
+14.8%, p≤0.014); higher *price-sensitivity* personas shift more (peak −7.0% / valley +14.6%, p=0.014,
derived deterministically from `energy_awareness`/`conscientiousness`). Reward and penalty framing are
**equivalent** (CPR ≈ CPP).

**Nulls on the price side.** Demand charge stays null even with concrete figures (it requires a *global*
"lower today's maximum" action the agents do not perform); a "free electricity" window is nominal but
n.s.; multi-day bill feedback is a clean null (no cross-day memory).

### 5.4 The peak-shaving mechanism
Targeting a device shaves the **total** peak only if the device is **not substitutable**:
- targeting the **air-conditioner** (non-substitutable) reduces AC by **−58%** (device-level, robust);
  the *total-peak* claim (−22.5%) is **withdrawn** (§7);
- targeting the **induction cooker** (substitutable) cuts its own load by −99.7% but the agent switches
  to oven/microwave, leaving the total peak unchanged (−0.2%); the cooker peak tax is null;
- targeting the **water heater** is ineffective (three tests).
The evening peak is **cooking-dominated** in most households (induction cooker 27–54% of the window),
which is why cook-dominated peaks resist shaving. Two further facts: **energy-saving ≠ peak-shaving**
(a request can cut AC use while leaving the peak unmoved), and shaving requires a **device × window**
joint anchor (generic window signals do not shave; `ac_tax` does). The device-targeted dose law
(shaving ∝ device peak-window load × behaviour-change rate) holds as a trend across worlds.

### 5.5 Null / retired results
TOU (text), peak_demand, uniform tax (Gunkel 2023 alignment attempt), social norms (unstable),
loss framing (counterexample), in-home display, night setback, storm, energy-crisis, solar-incentive,
rebate (partial), and free window are **null**; `blackout_risk` / `price_hike` are **withdrawn** as
baseline-drift artifacts; future-price / community notices are **world-specific**; EV subsidy / delay are
**blocked** by the overnight valley ceiling; the substitution effect did **not** replicate on a
full 5-member household.

---

## 6 Discussion

**Two classes of behaviour.** The platform is a **context/instruction responder**, not an economic
optimizer. Structural shocks that change the *context* (weather, at-home status) produce strong, robust,
cross-world effects through ordinary commonsense reasoning. Generic prices require an economic trade-off
the agents do not possess; they respond only when the trade-off is made **concrete** (per-appliance
money) and, for peak shaving, **actionable** (device × window).

**Capability boundary (what the platform can and cannot claim).**
- Can: **direction** of structural events; **peak-shifting / valley-filling** under concrete pricing;
  **device-level** response of non-substitutable appliances.
- Cannot: literature-scale (3–6%) price elasticity from text; global (demand-charge) shaving;
  cross-day learning / habit; PV-adoption or EV-valley phenomena.

**Alignment with the literature.** Directions align with Faruqui & Sergici (2010) (peak-shifting, CPP/CPR),
Xia et al. (2026) (disruption realism), Allcott/Ayres and Costa & Kahn (heterogeneity), Pellerano (2017)
(non-additivity / crowding), and Zhou et al. (2016) (variability→response, directionally). Magnitudes
**exceed** empirical values — consistent with LLM **over-compliance** — so absolute magnitudes are not
claimed; alignment is qualitative.

**Prompt-sensitivity is a first-class finding.** The single most important methodological result is that
"the platform can analyse prices" must be stated as "**concrete cost information is effective, and an
explicit rescheduling authorization strengthens peak shaving**" — because a merely abstract price is null,
and raw framing (reward/penalty, gain/loss, social norm) is **flattened** once the window and amount are
concrete.

---

## 7 Validity audit (adversarial self-review)

We re-examined every conclusion and classify it as **robust / prompt-sensitive / withdrawn**.

**Robust (direction).** The seven event results and the null set; all eight primary p-values survive
Benjamini–Hochberg correction across the eight tests (max adjusted p=0.039).

**Prompt-sensitive (preliminary).**
- **Price shaving**: partly instruction-driven (facts-only gives valley +11.6%; authorization adds
  peak −8.1%). Do **not** claim pure elasticity.
- **Heatwave**: preset events set a **structured weather field**, so the effect is not purely
  language-only.
- **Season**: with the date→season mapping, winter-heating / summer-cooling largely follows the prompt's
  season rule.

**Withdrawn / demoted.**
- **ac_tax peak −22.5% is withdrawn**: on a shared timeline the heatwave→+ac_tax comparison gives
  +6.1% (n.s.); only the **device-level AC reduction (−58%)** is robust.
- ac_tax × rebate (n=9) is **weak** evidence; the substitution mechanism did **not** replicate (R211);
  Zhou-variability is directional only (n=5).

**Cross-cutting risks (documented, partially mitigated).** Over-compliance inflating magnitudes;
interventions that touch structured fields (weather/season) rather than language alone; a house-specific
"generic-event reactivity" that inflates load on one household; post-hoc prompt tuning; multiple
comparisons (mitigated by BH-FDR); most experiments simulate a single member; platform-version drift
during the session (weather / tariff / policies added).

---

## 8 Limitations

- Weather beyond the date-derived season and event overrides is a stub; season temperatures are nominal.
- Public benchmarks for occupant-driven stochastic load were not used; alignment is qualitative.
- Population scale is ≤5 households/world; RQ1-at-scale and RQ4 (distillation/cost) are out of scope.
- Most experiments are single-member; multi-member validation was done only for a subset.
- Absolute magnitudes are inflated by LLM over-compliance and are not claimed.
- EV and PV phenomena are structurally blocked (valley ceiling; no adoption mechanism).

---

## 9 Conclusion

LLMWorld is an end-to-end, natural-language-intervention testbed whose emergent behaviour we validated
against the demand-response literature while being explicit about its boundaries. Its reliable outputs are
the **direction of structural "stay-home" and weather shocks** and **peak-shifting under concrete,
per-appliance pricing** — with peak shaving governed by a **dose × substitutability × device/window**
mechanism. Equally important is the negative space: text-only prices, global demand charges, cross-day
learning and PV/EV effects are not attainable, and a previously claimed peak-shaving result is withdrawn.
We argue this calibrated boundary — rather than any single effect size — is the contribution that makes
LLM-agent energy simulation trustworthy, and we release the pipeline, the intervention surface, and the
full experimental record for replication.

---

## References

1. Albadi, M. H., & El-Saadany, E. F. (2008). A summary of demand response in electricity markets. *EPSR*, 78(11), 1989–1996.
2. Alexeenko, P., & Bitar, E. (2023). Achieving reliable coordination of residential plug-in electric vehicle charging: A pilot study. *arXiv:2112.04559*.
3. Allcott, H. (2011). Social norms and energy conservation. *Journal of Public Economics*, 95(9–10), 1082–1095.
4. Almashor, M., et al. (2024). Can private LLM agents synthesize household energy consumption data? *Energy and AI*, 16, 100360.
5. Ayres, I., Raseman, S., & Shih, A. (2013). Evidence from two large field experiments that peer comparison feedback can reduce residential energy usage. *JLEO*, 29(5), 992–1022.
6. Barnes, J., Islam, M. R., & Morshed, S. (2022). Passive and active peer effects in the spatial diffusion of residential solar panels. *ERSS*, 86, 102458.
7. Cabezas-Rivière, N., et al. (2025). Identifying and understanding obstacles to heating sobriety and thermal comfort in collective housing. *arXiv:2512.16949*.
8. Capasso, A., Grattieri, W., Lamedica, R., & Prudenzi, A. (1994). A bottom-up approach to residential load modeling. *IEEE TPWRS*, 9(2), 957–964.
9. Chen, H., et al. (2025). Multi-agent consensus seeking via large language models. *arXiv:2310.20151*.
10. Chetty, N., et al. (2025). An LLM framework for inferring household energy consumption through behaviour simulation. *Applied Energy*, 355, 122335.
11. Costa, D. L., & Kahn, M. E. (2010). Energy conservation "nudges" and environmentalist ideology. *JEEA*, 11(3), 680–702.
12. Escarrega, C., et al. (2025). Demand charge management: Prototype design and testing. *arXiv:2509.10713*.
13. Faruqui, A., & Sergici, S. (2010). Household response to dynamic pricing of electricity: A survey of 15 experiments. *Journal of Regulatory Economics*, 38(2), 193–225.
14. Fidone, G., et al. (2025). Evaluating online moderation via LLM-powered counterfactual simulations. *arXiv:2511.07204*.
15. Ghesla, C., Grieder, M., & Schmitz, J. (2019). Pro-environmental incentives and loss aversion: A field experiment on electricity saving behavior. *Energy Policy*, 128, 102–112.
16. Gunkel, P. A., et al. (2023). Uniform taxation of electricity: Incentives for flexibility and cost redistribution among household categories. *arXiv:2306.11566*.
17. Jessoe, K., & Rapson, D. (2012). Knowledge is (less) power: Experimental evidence from residential energy use. *AER*, 104(4), 1417–1438.
18. Jin, L., et al. (2021). Investigating underlying drivers of variability in residential energy usage patterns with daily load shape clustering of smart meter data. *arXiv:2102.11027*.
19. Koley, S. (2025). SALM: A multi-agent framework for language model-driven social network simulation. *arXiv:2505.09081*.
20. Michelon, F., Zhou, Y., & Morstyn, T. (2025). Large language model interface for home energy management systems. *Applied Energy*, 358, 122590.
21. Monacchi, A., et al. (2015). An open solution to provide personalized feedback for building energy management. *arXiv:1505.01311*.
22. Murakami, K., Shimada, K., & Tanaka, M. (2022). Heterogeneous treatment effects of nudge and rebate. *Energy Economics*, 105, 105737.
23. Park, J. S., et al. (2023). Generative agents: Interactive simulacra of human behavior. *UIST '23*.
24. Pellerano, J. A., et al. (2017). Do extrinsic incentives undermine social norms? Evidence from a field experiment in energy conservation. *Environmental and Resource Economics*, 67(3), 413–431.
25. Piao, J., et al. (2025). AgentSociety: Large-scale LLM-driven generative agents. *arXiv*.
26. Richardson, I., Thomson, M., Infield, D., & Clifford, C. (2010). Domestic electricity use: A high-resolution energy demand model. *Energy and Buildings*, 42(10), 1878–1887.
27. Schröder, C., et al. (2013). Household formation and residential energy demand: Evidence from Japan. *Energy Economics*.
28. Thorvaldsen, K., et al. (2021). Long-term value of flexibility from flexible assets in building operation. *arXiv:2105.11952*.
29. Wang, X., et al. (2023). Self-consistency improves chain of thought reasoning in language models. *ICLR*.
30. Wang, Y., et al. (2021). Electricity price and habits: Which would affect household electricity consumption? *Energy Policy*.
31. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
32. Wei, Y., et al. (2026). Eco3S: Complex socio-economic system simulation via agent-based models. *arXiv:2607.26588*.
33. Widén, J., & Wäckelgård, E. (2010). A high-resolution stochastic model of domestic activity patterns and electricity demand. *Applied Energy*, 87(6), 1880–1892.
34. Xia, H., et al. (2026). Empirical grounding improves the realism of LLM agents simulating human behavior during disruptions. *arXiv:2607.17437*.
35. Xu, et al. (2026). Agent-based modeling and neural network for residential customer demand response.
36. Yao, S., et al. (2023a). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
37. Yao, S., et al. (2023b). Tree of thoughts: Deliberate problem solving with large language models. *NeurIPS*.
38. Zhang, et al. (2026). CoRenew: A large language model agent-based policy simulation platform for multifamily residential redevelopment. *arXiv:2607.25447*.
39. Zhou, D., Balandat, M., & Tomlin, C. (2016). Residential demand response targeting using machine learning with observational data. *arXiv:1607.00595*.

---

*Appendix A (reproducibility): the repository contains `run.py`, `src/engine/{policy,tariff,news,social,weather}.py`,
`src/steps/{world,simulate}/*`, `src/analyze/*`, 298 offline unit tests (`tests/`), and the full
experimental record `reports/R001–R222`. All interventions are natural-language only; the intervention
surface and the four validity rules are exercised throughout the reports.*
