# Experiment: In-home display / real-time feedback (`in_home_display`)

> 状态：**null（same-era 交错确证）**：峰段名义 −10.3%（t≈−1.55，n.s.），总电量 **+4.2%**（无节能）。数值来自 R109。
> ⚠️ **N=3 小样本**（R112/R114：连续幅度须 **n≥15**）——此 null 未足功效。
> ⚠️ 早前 −5.2%/−8.4%（R098）为**跨时段**比较，受 R104 漂移影响，已作废。

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

## 5. Results（same-era 交错；N=3）

world_172148 house_0002 M1，**同批次交错**（`ib_1`/`ii_1`/`ib_2`/`ii_2`/`ib_3`/`ii_3`）：

| 指标 | baseline (n=3) | in_home_display (n=3) | 变化 |
|---|---|---|---|
| 总电量 kWh | 9.279 | 9.673 | **+4.2%** |
| 日间 kWh | 2.076 | 2.093 | +0.8% |
| 峰段 kWh (16–21) | 3.813 | 3.420 | **−10.3%** |
| 外出 min | 590 | 600 | +1.7% |

配对峰段差 [−0.852, −0.327, 0.000] → mean −0.393，std 0.440，**t≈−1.55（n.s., p≈0.26）**。

## 6. Comparison with Literature

- **实测 null**（峰段 −10.3% 不显著；总电量 +4.2%）与 guide/Monacchi 的 3~10% 节能**不符**；
- 支持"文献尺度小效应在本平台不可判（R058）"，且此处方向（总电量升）与节能相反。

## 7. Validity Check

- **有效设计**：baseline 与处理**同批次交错**（规避 R104 跨时段漂移）；
- N=3，峰段效应 < 基线 std；须更大 N 方可判定更小效应（C1，未决）。

## 8. Conclusion

- **null**：IHD 反馈在本平台**无显著峰段削减**（−10.3%，n.s.），且总电量 **+4.2%**（不节能）；
- 早前 −5.2%（R098，跨时段）为噪声，已作废；与 `peak_demand` same-batch null（R092）一致。

