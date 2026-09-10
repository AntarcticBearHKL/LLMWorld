# Experiment: Lockdown event (`lockdown`)

> 状态：**有效果（二值，跨 3 世界，极显著）**：lockdown 使外出行程 **13/13 → 1/13** 归零
> （Fisher 双侧 p≈0.000003），日间负荷激增（单例 +294%）。数值来自 R068/R069/R086。

## 1. Research Question

对应 **RQ2**。公共卫生封锁（居家令）以自然语言注入后，居民的**居家时间与日间用电**是否显著上升？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §5.1）**：lockdown → 更多时间在家 → 日间用量上升。
- **文献基准**：Xia et al. (2026)（disruption 下行为真实性）。
- **合理区间**：Out 时间减少、日间负荷上升（方向为正）。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（单人）。
- **Dates / Days**：2026-09-11（1 天）。
- **Intervention / Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env lockdown_run --event-template "2026-09-11|lockdown" --workers 1
  # baseline: --env tou_ctl
  ```
- **Model / Params**：DeepSeek，thinking on；事件经 `engine/news.py` 注入（s1 与 s4）。
- **Analysis**：`load_model`（总/日间 kWh）+ `s1_macro` 的 `Out` 分钟数。

## 4. Metrics

Out 分钟数、日间(9–17) kWh、总电量变化 %。

## 5. Results

**单例（R068）**

| 臂 | 总 kWh | 日间 9–17 kWh | Out 分钟 |
|---|---|---|---|
| baseline | 8.193 | 0.649 | 615 |
| **lockdown** | **12.107（+47.8%）** | **2.558（+294%）** | **0** |

**跨成员/世界汇总二值统计（R069；Out 分钟 >0 记为"外出"）**

| 世界/住户/成员 | baseline Out(min) | lockdown Out(min) |
|---|---|---|
| w838 house_0001 Member 1 | 600 | 0 |
| w838 house_0001 Member 2 | 465 | 0 |
| w838 house_0001 Member 3 | 280 | 0 |
| w838 house_0001 Member 4 | 570 | 0 |
| w838 house_0002 Member 1 | 615 | 0 |
| w172 house_0002 Member 1 | 600 | 0 |
| w172 house_0002 Member 2 | 600 | 0 |

**累计（含 R086 world_143345 house_0001 六成员）：baseline Out>0 13/13 vs lockdown 1/13；
Fisher 双侧 p ≈ 0.000003（跨 3 世界）。**

## 6. Comparison with Literature

- 方向与 guide §5.1 及 Xia et al. (2026) 一致（事件驱动的行为/负荷变化）。

## 7. Validity Check

- 事件文本为中性公共卫生告知（无行为指令）→ 非硬编码；
- n=1；Out 归零是准二值信号，须跨成员/世界复现。

## 8. Conclusion

- **显著且最强**：lockdown 使户外时间近乎归零（baseline **13/13** → lockdown **1/13**, 双侧 p≈0.000003，
  跨 3 世界），日间负荷随之激增（单例 +294%）。是本项工作**效应量最大**的结论。
- **可复现命令**：见第 3 节。
