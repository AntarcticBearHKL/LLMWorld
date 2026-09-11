# Experiment: Night setback (`night_setback`)

> 状态：**初步（null）**：cold_snap 背景下 night_setback 未降采暖（10.2→14.2 kWh，单例）。数值来自 R099。
> ⚠️ **单例**（R112/R114：连续幅度须 **n≥15**）——仅无证据支持，不能断言有害。

## 1. Research Question

对应 **RQ2**。夜间回温建议是否降低采暖/制冷能耗，且**温度偏好**不同的家庭响应差异如何？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §4.1）**：采暖能耗下降 5~10%；
  高温度偏好（夏 26 / 冬 22+）的家庭更抗拒回温。
- **文献基准**：Cabezas-Riviere et al. 2025（舒适感知是回温最大障碍）。

## 3. Experimental Setup（计划）

- World：`world_838587`；冬季/寒潮更佳；Days：≤3；
- Command：`--policy night_setback`（可叠 `--event-template "<date>|cold_snap"`）。
- Analysis：采暖相关能耗分项 + `analyze_groups.py`（温度偏好/性格分组）。

## 4. Metrics

采暖能耗变化 %、按温度偏好分组的差异、夜间温度设定行为。

## 5. Results（初步；单例）

world_838587 house_0002，cold_snap 背景下：

| 臂 | 采暖 kWh | 总 kWh |
|---|---|---|
| cold_snap only | 10.200 | 21.140 |
| cold_snap + night_setback | 14.200 | 25.341 |

**未降采暖**（反而 +39%；单例，噪声内）→ **null**。

## 6. Comparison with Literature

待填（对照 5~10%）。

## 7. Validity Check

待填。

## 8. Conclusion

- **null**：night_setback 未产生回温节能（单例 +39%，与 guide −5~10% 不符）；软引导效应弱/不稳。

