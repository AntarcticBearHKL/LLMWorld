# Experiment: Group heterogeneity (grouped policy response)

> 状态：**占位（待验证）**。第 1–4 节就绪；第 5 节待跑后填。

## 1. Research Question

对应 **RQ3**（宏观涌现与实证对齐）；研究计划 Phase Two 的"同政策分组分化"。
核心问题：同一干预是否对**不同价值/性格群体**产生**分化甚至相反**的响应？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §3.4）**：高能源意识/高尽责性家庭对政策（尤其 nudge）响应更强。
- **文献基准（Costa & Kahn 2010）**：同一 nudge 下，自由派家庭约 −3%，
  部分保守派家庭反而 **+1%**（分化/反向）。
- **合理区间**：组间差异显著、方向可相反。

## 3. Experimental Setup（计划）

- World：`world_838587`（后续用 ≤5 户）；Dates/Days：≤3 天；
- Intervention：`--policy nudge`（或 TOU）；
- Label source：`personality.energy_awareness`（B2 派生）或 `analyze_variability`；
- Analysis：`python src/analyze/analyze_groups.py <world> --label-source awareness`
  （可选 `--label-source variability`）。

## 4. Metrics

各组 **总电量变化 %**、**组间差异**、响应**方向**（是否出现反向组）；样本量每组 ≥ 数户/成员。

## 5. Results

**待验证。** 需多人户/多成员样本以形成有意义的组。

## 6. Comparison with Literature

待填（对照 Costa & Kahn 2010 的 2–4% / ~0 分化）。

## 7. Validity Check

待填（样本量、分组是否退化、是否 prompt 偏置）。

## 8. Conclusion

待填。
