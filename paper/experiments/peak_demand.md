# Experiment: Demand charge (`peak_demand`)

> 状态：**null（N=3 交错）**：需量电费未削峰（峰值 +4.2%、峰段 −3.2%，均在噪声内）。数值来自 R092。
> ⚠️ **N=3 小样本**（R112/R114：连续幅度须 **n≥15** 方稳）——此 null 未足功效，方向可能不稳。

## 1. Research Question

对应 **RQ2**。需量电费（按日最高 60 分钟计费）是否促使家庭错开高功率家电、削平峰值？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §2.3）**：单户峰值功率下降、使用错峰；
  依赖空调的家庭（夏季）响应更强。
- **文献基准**：Escarrega et al. 2025（实时需量反馈下峰值可削 **10~20%**，高需量用户更强）。

## 3. Experimental Setup（计划）

- World：`world_838587`；Days：≤3；
- Command：`python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 --policy peak_demand --workers 1`
- Analysis：`load_model` 峰值/平台率；可结合 `analyze_policy_tradeoffs.py`。

## 4. Metrics

峰值 W 下降 %、峰均比、平台分钟数（≥80% 峰值）、总电量变化 %。

## 5. Results（初步；N=3 平均）

world_172148 house_0002 M1，baseline×3 vs `peak_demand`×3（1 天）：

| 指标 | baseline (n=3) | peak_demand (n=3) | 变化 |
|---|---|---|---|
| 总电量 kWh | 9.402 ± 0.624 | 9.491 ± 0.125 | +0.9% |
| 峰值 W | 3183 ± 94 | 3316 ± 163 | **+4.2%** |
| 峰段 kWh (16–21) | 3.753 ± 0.620 | 3.633 ± 1.062 | **−3.2%** |

**无削峰**（变化均小于噪声；baseline 峰段 CV≈17%）→ **null**（R092）。期望 −10~20% 未出现。

## 6. Comparison with Literature

待填（对照 −10~20%）。

## 7. Validity Check

待填。

## 8. Conclusion

- **初步 null**：需量电费在 N=3 平均下未削峰（峰值 +4.2%、峰段 −3.2%，均在噪声内）。
- 与主线一致：软/价格干预效应弱、噪声大；仅大效应事件可判。

