# Experiment: Electricity price rise (`price_hike`)

> 状态：**未复现（不稳定/世界特异）**：world_838587 峰段 −17.9%，但 world_172148 **+6.8%**。
> 数值来自 R094/R097；**不能声称 price_hike 稳定削峰**。

## 1. Research Question

对应 **RQ2**。电价上涨公告以自然语言注入后，居民是否削减/错开用电？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §5.1）**：price_hike → "大家省电；高敏感家庭响应强"。
- **文献基准**：Faruqui & Sergici (2010)（价格弹性）；Wang et al. (2021)（习惯主导）。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（单人）；日期 2026-09-11。
- **Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env pricehike_runN --event-template "2026-09-11|price_hike" --workers 1   # N=1,2,3
  ```
- **Analysis**：`load_model` 峰段(16–21) kWh + 总电量。

## 4. Metrics

峰段(16–21) kWh、总电量变化 %。

## 5. Results（两世界）

| 世界 | baseline 峰段 kWh (n=3) | price_hike 峰段 kWh (n=3) | 变化 |
|---|---|---|---|
| world_838587 | 4.686 ± 0.154 | 3.849 ± 0.635 | −17.9%（z≈−5.4） |
| world_172148 | 3.461 ± 0.187 | 3.696 ± 0.761 | **+6.8%**（z≈+1.26） |

**方向不一致 → 未复现**（世界特异）。

## 6. Comparison with Literature

- 方向为"削峰"，与价格信号预期一致；幅度与大样本方差下须复现。

## 7. Validity Check

- 中性公告文本；单户/单成员/1 天、N=3 → 初步。

## 8. Conclusion

- **未复现**：`price_hike` 削峰世界特异（−17.9% vs +6.8%）→ **不作有效结论**。
- 对照：`blackout_risk` 跨世界同向（可复现），`price_hike` 反向（不可复现）。
