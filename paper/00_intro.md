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
   Costa & Kahn 2010; Xia et al. 2026; …), yielding **three statistically significant natural-language
   event results**: heatwave → cooling (p≈0.0004), cold-snap → heating (p≈0.038), lockdown → stay-home
   (p≈0.0003), replicated across two synthetic worlds.

## Notes

- Alignment targets and the experiment plan: see `FIT5216/研究计划.md` §2.7, §4.3.
- Experiment checklist: `paper/README.md`.
