# Experiment: Night setback (`night_setback`)

> 状态：**占位（待验证）**。第 1–4 节就绪；第 5 节待跑后填。

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

## 5. Results

**待验证。**

## 6. Comparison with Literature

待填（对照 5~10%）。

## 7. Validity Check

待填。

## 8. Conclusion

待填。
