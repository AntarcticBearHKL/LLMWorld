# `import/` — pipeline inputs

Everything the world-generation pipeline reads. Two datasets.

## `persona/` — synthetic persona attribute tables

- `synthetic_001.csv` … `synthetic_040.csv` (~27 MB each, ~1.0 GB total), plus
  `reader.py`, `sampler.py`, `persona_render.py`.
- Each CSV is a wide table of persona attributes (demographics, attitudes,
  lifestyle traits). `reader.py` / `sampler.py` read them, `persona_render.py`
  renders the sampled rows into the English persona texts the pipeline injects.
- The `synthetic_` prefix and the nature of the columns indicate these are
  **generated attribute rows, not records of real people**.
- `dimension_map.json` (an English→Chinese label map read by `reader.py` and
  `sampler.py`) is **not present**. When absent those readers fall back to the
  English labels, so this degrades display only and does not crash.
- These files are stored with **Git LFS** — run `git lfs install` before cloning.

## `world/Melbourne/3168/` — district profile

- `info.md` — a written demographic profile of the Clayton 3168 district
  (Greater Melbourne), summarising the 2021 ABS census.
- `stats.csv` — a census-derived statistics table with columns
  `Table_Source, Column_Code, Chinese_Description, Clayton_Value` (UTF-8, with a
  BOM). Its values are the numeric facts quoted by `info.md`.

## Provenance & licensing

- `world/Melbourne/3168/` is derived from Australian Bureau of Statistics 2021
  Census data (published by the ABS under CC BY 4.0); attribution should be kept.
- **The origin and licence of the synthetic persona tables are not recorded in
  this repository.** Before redistributing them publicly, confirm their upstream
  source and terms and record them here.

`import/` is read-only input: the code never writes to it.
