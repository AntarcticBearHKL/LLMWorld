# Experiment: Rolling-blackout warning (`blackout_risk`)

> 状态：**有效果（方向跨 3 世界复现）**：`blackout_risk` 使峰段(16–21)电量 **−7.3%~−31.7%**
> （N=3/臂；world_838587 −31.7%、world_172148 −11.7%、world_143345 −7.3%）。数值来自 R094/R096/R103。

## 1. Research Question

对应 **RQ2**。电网"可能晚峰拉闸"预警以自然语言注入后，居民是否主动避免晚峰用电？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §5.1）**：blackout_risk → "避开高晚峰"的行为。
- **文献基准**：Xia et al. (2026)（disruption 下的行为真实性）。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（单人）；日期 2026-09-11。
- **Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env blackout_runN --event-template "2026-09-11|blackout_risk" --workers 1   # N=1,2,3
  ```
- **Analysis**：`load_model` 计算峰段(16–21) kWh；baseline 复用 3 个同配置无事件运行。

## 4. Metrics

峰段(16–21) kWh（低噪，baseline CV≈3.3%）、总电量、峰值。

## 5. Results（初步）

| 世界 | baseline 峰段 kWh (n=3) | blackout_risk 峰段 kWh (n=3) | 变化 |
|---|---|---|---|
| world_838587 | 4.686 ± 0.154 | 3.203 ± 0.298 | **−31.7%**（z≈−9.6） |
| world_172148 | 3.461 ± 0.187 | 3.056 ± 0.645 | **−11.7%**（z≈−2.2） |
| world_143345 | 3.398 ± 0.910 | 3.151 ± 0.239 | **−7.3%** |

**方向跨 3 世界一致（均负）**；幅度世界异质（−7%~−32%）。

## 6. Comparison with Literature

- 方向与 guide §5.1 一致（预警 → 避开晚峰）；幅度大，须跨世界复现。

## 7. Validity Check

- 事件为中性预警文本（无行为指令）；单户/单成员/1 天、N=3 → 初步；峰段为低噪指标。

## 8. Conclusion

- **初步-强**：blackout_risk 显著削减峰段（−31.7%）；下一步跨世界/成员复现（C1）。
