# 00 — Introduction / Research Questions（草稿）

> 状态：草稿（骨架 + 要点）。正式撰写时以 `FIT5216/研究计划.md` §1–§3 与文献库为准。

## Positioning

We build a **population-level, multi-LLM-agent framework** for residential electricity-behaviour
simulation. Each household is an autonomous agent whose daily activities are planned by an
LLM from structured profiles; activities are then mapped to **minute-resolution, appliance-level
electricity load**. External inputs — electricity tariffs, social-norm messages, and social/news
events — are injected **only as natural language**; aggregate behaviour is emergent.

## Research Questions

- **RQ1 — Large-Scale Heterogeneous Population Simulation.** How to simulate many heterogeneous
  households (composition, roles, income, personality) in parallel and produce realistic,
  diverse minute-resolution load profiles?
- **RQ2 — Behavioural Transmission of External Inputs.** When policies (TOU, demand charge,
  subsidies) or social events (heatwaves, holidays) are injected via natural-language prompts,
  how do agents respond at the appliance-decision level, and how does that surface in load?
- **RQ3 — Emergent Population Patterns & Empirical Alignment.** Do aggregate responses match the
  empirical literature (peak shaving/valley filling, price elasticity, heterogeneous
  non-price-intervention effects), and do phenomena beyond individual behaviour emerge?
- **RQ4 — Scalability & Practicality.** How can distillation, parallel scheduling, and caching
  make LLM-based population simulation practical at scale?

## Contributions (draft)

1. An end-to-end pipeline **behaviour → appliance decision → minute-resolution load**.
2. A natural-language intervention surface (pricing / norms / events) with emergent effects.
3. Alignment experiments against empirical benchmarks (Faruqui & Sergici 2010; Allcott 2011;
   Costa & Kahn 2010; Xia et al. 2026; …), yielding **four statistically significant natural-language
   event results**, each replicated across three synthetic worlds — heatwave → cooling (two-sided
   p≈0.00003), lockdown → stay-home (p≈0.000003) **plus a judgeable daytime-load magnitude
   (+220.7%, same-era n=9, p≈0.010)**, cold-snap → heating (p≈0.011), and **air-conditioner peak tax
   → AC-off/peak-shaving** (AC-on 15/15→7/15, p≈0.0022; peak −22.5%/−24.6%/−20.6%).
4. A **mechanistic account of peak-shaving** — the effect of a device-targeted intervention scales with
   the device's **peak-window load × behaviour-change rate** (a 3-world dose–response), with a distinct
   *window+price* path (`ac_tax`) that additionally shifts non-AC evening load. **Energy-saving ≠
   peak-shaving.**
5. Three **validity red lines** for LLM-agent energy simulation: (i) continuous metrics **drift across
   session time** → use same-era baselines or binary/structural signals; (ii) continuous magnitudes are
   unreliable below **n≈15**; (iii) mechanistic claims require **cross-world** replication.

## Notes

- Alignment targets and the experiment plan: see `FIT5216/研究计划.md` §2.7, §4.3.
- Experiment checklist: `paper/README.md`.
