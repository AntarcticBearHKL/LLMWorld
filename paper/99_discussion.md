# 99 — Discussion（草稿）

> 状态：草稿，随实验推进更新。仅记录**已产生（含初步）有效果**的内容；过程证据见 `reports/`。

## RQ1 — Heterogeneous population

- Implemented: structured personality (big_five / energy_awareness) derived deterministically;
  room/appliance dedup; 28-type catalog with physical parameters.
- Verified offline (L1) and on a real 2-day run (personality fields present on all members).
- Open: population-scale generation and distributional validation vs real aggregate load.

## RQ2 — Behavioural transmission of external inputs

- **Heatwave (binary signal, statistically significant)**: a natural-language heatwave event causes
  agents to switch the air-conditioner on. Aggregating all post-fix runs **across two independent
  worlds**, the AC was active in **0/7** baseline vs **9/10** heatwave member-days (Fisher one-sided
  **p ≈ 0.0004**); direction
  consistent with Xia et al. (2026). Individual heterogeneity is visible (one heatwave member did not
  use it). **Key validity condition**: the news text must agree with the environment weather,
  otherwise agents ignore it (observed failure → fixed by event↔weather linkage). Note that the
  single-sample *total-energy* increases (+17%~+64%) are noise-dominated (cf. noise floor, R057) and
  are not claimed.
- **Cold-snap (preliminary, n=1)**: a `cold_snap` event switched heating devices from off to on
  (SpaceHeater 3.0 + AC 7.2 kWh; total +158%, R062) — a second large-effect binary signal symmetric
  to the heatwave; needs replication.
- Pricing interventions: **TOU not robust** — the peak-shaving direction *reverses* with sampling:
  reasoning mode gave peak −18%~−26%, while the low-variance no-thinking retest (R026) gave peak
  **+8%~+30%**; the de-instructionalized `tou_soft` ablation (R024) was self-contradictory. With n=1,
  the effect is not separable from run/day variance, so no alignment claim is made. Requires
  multi-household averaging.
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

**Mitigation**: provide de-instructionalized variants (`tou_soft`, `nudge_soft`) and compare; and, for
any magnitude claim, average across multiple households/members at a fixed weekday. Accordingly, this
work treats the platform as suited to **direction** and **heterogeneity** claims, with absolute
magnitude calibration left as future work.

Relatedly, **framing effects are unstable**: the loss-framed `nudge_loss` did not beat the plain
`nudge`; it *raised* total energy (+6% vs nudge's −6%~−10%, R041), contradicting Ghesla et al. (2019).
Both the over-compliance and the framing results point to **wording-driven** rather than
information/psychology-driven behaviour in the current agents.

## Limitations

- Heatwave result so far is **single-household** (n=1) with `temperature=1.0`; needs multi-member/
  multi-seed replication before being treated as a final result.
- Weather is currently a stub; event effects use a fixed temperature offset.
- Refactor-era drift is resolved: `engine/news.py`, `compare_worlds.py`, all documented policies
  (`tou`/`tou_soft`/`nudge`/`nudge_soft`/`nudge_loss`/`subsidy`/`peak_demand`/`ev_delay`/
  `night_setback`/`in_home_display`), `--community-notice`, `--policy-schedule`, and `--peer-nudge`
  are restored (the guide's `population_runner.py` role is now covered by `run.py`).

## Next steps

1. Multi-member / multi-seed heatwave replication; `analyze_event_response.py` transition metrics.
2. Pricing (TOU/subsidy) effect experiments vs benchmarks.
3. Restore or formally retire `population_runner.py` capabilities.
