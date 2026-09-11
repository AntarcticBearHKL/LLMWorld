# 01 — Method（草稿）

> 状态：草稿。以当前代码为准确认（`run.py`、`src/steps/world/*`、`src/steps/simulate/*`）。

## 1. System overview

Single entry point `run.py`:

- `--mode world`  : synthesize households — **s1** household types → **s2** persona alignment →
  **s3** household build → **s4** world assembly.
- `--mode simulate`: generate behaviour — **s1** macro plan → **s2** coordination →
  **s3** contextual enrichment → **s4** appliance decisions.

Both modes persist structured JSON under `output/`.

## 2. Domain model

- A household = **members + rooms + appliances**.
- Appliance categories: **on-demand** (`use`/`idle`), **charging** (`charge_home`/`charge_external`/
  `use`/`idle`), **cycle** (`run`/`idle`), **always-on** (auto).
- 28 appliance types + 4 base classes; a shared `appliances/catalog.py` supplies rated power,
  power bounds, always-on daily energy, experiment metadata, and (new) **battery capacity/soc**.
- Charging appliances are capped by a **battery deficit** `(1-soc) × capacity` per day, in addition
  to per-type daily minute caps.

## 3. Behaviour → load pipeline

1. **Macro plan** (s1): each member's 00:00–24:00 activity segments, constrained to real rooms,
   full-day coverage, exact adjacency; **cross-day carry-over** prevents "teleport home" at 00:00
   (previous end-state injected into the prompt + a deterministic day-boundary rewrite).
2. **Coordination** (s2): reconcile shared activities/resources across members.
3. **Enrichment** (s3): add detail to activities.
4. **Appliance decision** (s4): map activities to appliance operations, validated/repaired against
   the household registry (unknown ids repaired by family/prefix, out-of-home operations dropped).
5. **Energy calculation** (`src/analyze/load_model.py`): minute-resolution load + per-appliance kWh.

## 4. Heterogeneity parameters

`personality.big_five` (5 dims, 0–1) and `energy_awareness` (Low/Medium/High) are derived
**deterministically** from the sampled persona row (BFI-2 columns + energy-attitude/conscientiousness
composite), falling back to a portrait-marker mapping. This makes group-level analysis reproducible.

## 5. External inputs (all natural-language)

- **Pricing**: TOU / TOU-soft / subsidy / demand charge / EV-delay policies render text into the s4
  prompt (`engine/policy.py`, `--policy`).
- **Social norms**: fixed-text comparison (`nudge`) and loss framing (`nudge_loss`); dynamic
  neighbour comparison (`--peer-nudge`, community mean of the previous day).
- **Behaviour guidance**: night setback (`night_setback`) and real-time feedback (`in_home_display`).
- **Policy timeline**: `--policy-schedule "start,end,policy"` activates a policy over a date window
  (announcement → effective → removal).
- **News events**: 10 preset templates + custom events (`engine/news.py`, `--event`/`--event-template`).
  Environment-type presets (**heatwave / cold_snap**) also adjust the weather context so text and
  structured fields agree.
- **Social signals**: community notices (`--community-notice`).

## 6. Analysis tooling

`src/analyze/` computes the paper's quantities: population summary, appliance usage, behaviour–load
consistency, grouped response (`analyze_groups.py`, by awareness/conscientiousness), event response,
policy trade-offs, multi-world comparison (`compare_worlds.py`), TOU window attribution, …
Outputs are JSON/CSV under `output/.../analysis/`.

## 7. Reproducibility & cost control

- Offline **L1** tests (mock `SubAgent`) over pure logic; **L2** small real runs (≤5 households,
  ≤3 days); L3 only when necessary. See `tests/` and `reports/`.
- **Validity controls (R104–R116)**: (i) LLM-agent **continuous** behaviour drifts across session time
  → always compare against a **same-batch (same-era) baseline**, or rely on **binary/structural**
  signals (appliance on/off, out-of-home), which are drift-immune; (ii) continuous-effect magnitudes
  are unreliable below **n≈15** (TOU: −17.5% → +13.1% → −3.2% as n grew 3→9→15); (iii) the noise floor
  is std≈1.0 kWh (**CV≈12%**), so only large effects (≥10–20%) are judgeable. See `99_discussion.md`.
