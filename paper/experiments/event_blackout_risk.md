# Experiment: Rolling-blackout warning (`blackout_risk`)

> 状态：**撤回（基线漂移伪影）**：R104 证明所谓峰段削减是**拿旧 baseline（峰段 4.686）比较**的伪影——
> 全新 baseline（峰段 3.441）与事件同区间，且**中性事件**同样"削峰"。**不作有效结论**。

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

> ⚠️ **R104 更正**：上述"削峰"是**基线跨时段漂移**造成的伪影。全新 baseline（同配置/同日/紧邻跑）
> 峰段 mean=3.441，事件 2.9–3.8 **同区间**；**中性事件**亦 −32.9%。**故撤回本实验的连续削峰结论**。

**Same-era 决定性验证（R105）**：与 fresh 基线**同期**跑 3 个 blackout_risk → 峰段 mean **3.988（+15.9%）**，
**无削峰**（差异 < 处理 std）。**确证伪影**。

## 6. Comparison with Literature

- 方向与 guide §5.1 一致（预警 → 避开晚峰）；幅度大，须跨世界复现。

## 7. Validity Check

- 事件为中性预警文本（无行为指令）；单户/单成员/1 天、N=3 → 初步；峰段为低噪指标。

## 8. Conclusion

- **撤回**：连续"削峰"为**基线漂移伪影**（R104）；不作有效结论。
- **教训**：跨时段比较**连续指标**无效；须**同批次紧邻**跑 baseline，或只用**二值/结构**指标。
