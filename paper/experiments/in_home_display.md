# Experiment: In-home display / real-time feedback (`in_home_display`)

> 状态：**初步（不显著）**：总量 −5.2%、峰段 −8.4%（N=3），方向与 guide 3~10% 一致但在噪声内。数值来自 R098。
> ⚠️ **R104 caveat**：baseline 为**跨时段**（nw_ctl/bp172）→ 连续指标不可靠；须**同批次紧邻**重做。

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

## 5. Results（初步；N=3）

world_172148 house_0002 M1，baseline×3 vs `in_home_display`×3：

| 指标 | baseline (n=3) | in_home_display (n=3) | 变化 |
|---|---|---|---|
| 总电量 kWh | 9.340 ± 1.388 | 8.850 ± 0.792 | −5.2% |
| 峰段 kWh (16–21) | 3.461 ± 0.187 | 3.169 ± 0.475 | −8.4% |

**方向一致（节能）但 N=3 不显著**（变化在噪声内；z<1）。

## 6. Comparison with Literature

待填（对照 3~10% 与 10~30%）。

## 7. Validity Check

待填。

## 8. Conclusion

- **方向一致但不显著**：IHD 反馈节能 −5.2%（N=3，噪声内）；需更大 N 方能判定（C1）。

