# R213 — price_sensitivity **人格化**（A2）：从住户特质自动派生

- **轮次**：Round 213（A2）
- **日期**：2026-09-12
- **验证层级**：**L1**（289 单测全绿，+1）+ L0 验证（0 token）
- **结论**：✅ `price_sensitivity` 从**手工开关**升级为**住户特质自动派生**：
  由 `household.json` 的 `energy_awareness` / `big_five.conscientiousness` 推得 high/low/neutral，
  自动注入成本上下文 → **人口异质性无需手填**。

## 1. 目的（A2）

R207 用命令行开关证明敏感度机制；本轮将其**人格化**（进住户档案），实现"**同价不同响应**"的人群分析。

## 2. 改动
- `src/engine/tariff.py`：新增 `sensitivity_from_traits(energy_awareness, conscientiousness)`：
  `energy_awareness==high` 或 `conscientiousness≥0.66` → **high**；`low` 且 `<0.34` → **low**；否则 neutral。
- `src/steps/simulate/s4_appliance_decision.py`：新增 `_raw_member_personality()` 读 `household.json`；
  当未显式给 `--price-sensitivity` 且有 tariff 时，**自动派生**并前置到 `{cost_context}`。
- `tests/test_tariff.py`：+1（派生规则）。**289 绿**。

## 3. 验证（L0）

```powershell
python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env pctx2_c_1 --policy "tou:0.9,0.18" --cost-context --s4-only --workers 1
```
注入验证（world_172148 h002，`energy_awareness=Low, conscientiousness=0.1`）：
> **"You are not very price-sensitive; comfort and convenience matter more than the bill."**

## 4. 现状与限制
- 各世界 persona schema 不一：`world_172148`（Low）→ 自动 low；`world_838587`（Medium）→ neutral；
  `world_143345`（无 awareness 字段）→ neutral。**当前无 high 派生户**（conscientiousness 多为 0.1）。
- 效果等价于 R207（高/低敏感 → 移峰 −7.0%/+14.6%）；本轮实现**自动化/人格化**。

## 5. 论文更新
- `paper/99_discussion.md`：补"price_sensitivity 由住户特质派生（R213）"。

## 6. token
- **0**（验证；代码改动仅本地）。
