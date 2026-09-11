# Experiment: Policy multi-objective trade-offs

> 状态：**初步（工具可用；TOU 结果混杂）**：峰值 −9.9% 但峰段 +18.9%、平台 +28.6%（world_838587）。数值来自 R102。

## 1. Research Question

对应 **RQ2/RQ3**（政策设计三难）。核心问题：削峰、用户负担、公平性之间如何权衡？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §7）**：削峰越强，用户负担/公平代价可能越大；
  不同政策（TOU vs 需量电费 vs nudge）在"峰削减 / 总电量 / 负担分布"上排序不同。
- **文献基准（CoRenew 2026）**：政策设计需在峰削减、参与负担与公平性间权衡。

## 3. Experimental Setup（计划）

- World：`world_838587`（后续多户）；Dates/Days：≤3 天；
- Interventions：`--policy tou`、`--policy peak_demand`、`--policy nudge`（逐一或 `tou,nudge` 组合）；
- Analysis：`python src/analyze/analyze_policy_tradeoffs.py <world>`；
  跨结构稳健性用 `compare_worlds.py --worlds <w1> <w2>`。

## 4. Metrics

峰段削减 %（`peak_hours_change_pct`/`peak_load_cut_pct`）、总电量变化 %、
平台率（`peak_plateau_cut_pct`）、峰均比（`peak_to_mean`）；负担/公平（需扩展）。

## 5. Results（初步）

`python run.py --mode simulate --world world_838587 --days 1 --env world_838587 --policy tou --workers 4`
后运行 `analyze_policy_tradeoffs.py world_838587`（% vs baseline；越负越好）：

| Policy | Total | Peak hrs | Peak | Plateau | P/M |
|---|---|---|---|---|---|
| baseline | — | — | — | — | 4.64 |
| tou | −13.4% | +18.9% | −9.9% | +28.6% | 4.83 |

**混杂**：最大峰值下降，但峰段总电量与平台率上升 → 不可定论（与 TOU 采样敏感一致）。

## 6. Comparison with Literature

待填（CoRenew 2026 三难；Faruqui & Sergici 2010 组合非简单相加）。

## 7. Validity Check

待填（幅度是否超基准、是否 prompt 偏置、样本量）。

## 8. Conclusion

- **初步（混杂）**：多目标权衡工具可用；TOU 在此显示"峰值↓但峰段/平台↑"的混杂结果，不作有效结论。

