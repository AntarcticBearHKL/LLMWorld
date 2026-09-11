# Experiment: Group heterogeneity (grouped policy response)

> 状态：**不可定论（方差压倒）**：R053 名义方向一致（Medium 降幅 > Low），但 R054 显示组内离散（±25~45pp）**远超**组间差，7 人中 3 人反增。

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

**初步（描述性，n=1/组）**：world_172148 `house_0002`，`nudge` vs baseline（1 天）：

| 成员 | awareness | baseline kWh | nudge kWh | 变化 |
|---|---|---|---|---|
| Member 1 | Low | 8.959 | 8.054 | −10.10% |
| Member 2 | Medium | 9.589 | 7.920 | −17.41% |

Medium（较高意识）降幅大于 Low——**方向与 Costa & Kahn (2010) 及 guide §3.4 预期一致**，
但每组 n=1，纯描述性。

**扩大样本（R054，world_172148 两户）**：Low（n=4）均值 **+3.44%**，Medium（n=3）均值 **−18.00%**；
组内离散度（Low: −25~+39pp；Medium: −45~+9pp）**远超组间差**
→ **不具统计意义**。分组方向**名义一致但被方差压倒**，**不能**作为 RQ3 结论；须大规模平均。

## 6. Comparison with Literature

待填（对照 Costa & Kahn 2010 的 2–4% / ~0 分化）。

## 7. Validity Check

待填（样本量、分组是否退化、是否 prompt 偏置）。

## 8. Conclusion

- **不可定论**：分组方向名义一致（Medium 更负），但 R054 显示**组内方差压倒组间差**；须大规模多种子平均。
- **可复现命令**：`run.py --mode simulate --world world_172148 --house house_0001 --days 1 --policy nudge`（对照 `--env ...` 无政策）。
