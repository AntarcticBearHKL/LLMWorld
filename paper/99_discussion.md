# 99 — Discussion（草稿）

> 状态：草稿，随实验推进更新。仅记录**已产生（含初步）有效果**的内容；过程证据见 `reports/`。

## RQ1 — Heterogeneous population

- Implemented: structured personality (big_five / energy_awareness) derived deterministically;
  room/appliance dedup; 28-type catalog with physical parameters.
- Verified offline (L1) and on a real 2-day run (personality fields present on all members).
- Open: population-scale generation and distributional validation vs real aggregate load.

## RQ2 — Behavioural transmission of external inputs

- **Heatwave (preliminary, replicated across 2 households / 3 event-days)**: a natural-language
  heatwave event causes agents to switch the air-conditioner from `idle` to `use` and raises daily
  total energy (control AC = 0 in every run; heatwave AC > 0 in every run; +17%~+64% total).
  Direction consistent with Xia et al. (2026). **Key validity condition**: the news text must agree
  with the environment weather, otherwise agents ignore it (observed failure → fixed by
  event↔weather linkage).
- Pricing interventions: **TOU not robust** — the peak-shaving direction *reverses* with sampling:
  reasoning mode gave peak −18%~−26%, while the low-variance no-thinking retest (R026) gave peak
  **+8%~+30%**; the de-instructionalized `tou_soft` ablation (R024) was self-contradictory. With n=1,
  the effect is not separable from run/day variance, so no alignment claim is made. Requires
  multi-household averaging.
- Social norms: **nudge preliminary** — the fixed-text nudge lowered total energy on both days
  (−5.8%~−10.3%), directionally consistent with Allcott (2011) / Ayres (2013) but above the −1~3%
  benchmark (over-compliance, cf. TOU); the dynamic `--peer-nudge` was inconsistent (+11.6% / −6.6%).
  Again n=1; requires averaging.

## RQ3 — Emergent patterns & empirical alignment

- Group-response analyzer ready (`analyze_groups.py`); awareness labels fixed to avoid single-group
  degeneracy.
- Multi-world comparison tool restored (`compare_worlds.py`).
- Pending: systematic alignment tables vs the benchmarks in `FIT5216/研究计划.md` §2.7.

## RQ4 — Scalability

- Parallel scheduling (`ThreadPoolExecutor`), `--s4-only` reuse, `--member/--house/--days` scoping,
  and prompt caching are in place; distillation not yet implemented.

## Limitations

- Heatwave result so far is **single-household** (n=1) with `temperature=1.0`; needs multi-member/
  multi-seed replication before being treated as a final result.
- Weather is currently a stub; event effects use a fixed temperature offset.
- Some guide-referenced tools were missing after a refactor; restored so far: `engine/news.py`,
  `compare_worlds.py`. Still missing: `population_runner.py` (policy schedule / peer-nudge).

## Next steps

1. Multi-member / multi-seed heatwave replication; `analyze_event_response.py` transition metrics.
2. Pricing (TOU/subsidy) effect experiments vs benchmarks.
3. Restore or formally retire `population_runner.py` capabilities.
