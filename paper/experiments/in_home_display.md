# Experiment: In-home display / real-time feedback (`in_home_display`)

> 状态：**占位（待验证）**。第 1–4 节就绪；第 5 节待跑后填。

## 1. Research Question

对应 **RQ2**。实时反馈（IHD）单独及与 TOU 叠加，节能/削峰效果如何？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §4.2）**：即时反馈带来 3~10% 节能；与 nudge 可叠加。
- **文献基准**：Monacchi et al. 2015（细粒度实时反馈显著优于月账单）；
  Faruqui & Sergici 2010（TOU + 实时反馈把削峰从 3~6% 提到 10~30%）。

## 3. Experimental Setup（计划）

- World：`world_838587`；Days：≤3；
- Command：`--policy in_home_display`；对照 `--policy tou` 与 `--policy "tou,in_home_display"`（组合）。
- Analysis：总电量/峰段 kWh 对比。

## 4. Metrics

总电量变化 %、峰段削减 %、IHD 单独 vs 叠加 TOU 的增量。

## 5. Results

**待验证。**

## 6. Comparison with Literature

待填（对照 3~10% 与 10~30%）。

## 7. Validity Check

待填。

## 8. Conclusion

待填。
