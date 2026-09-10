# Experiment: Lockdown event (`lockdown`)

> 状态：**初步（n=1，大效应）**：lockdown 使外出行程 615→0 分钟、日间负荷 +294%、总电量 +47.8%。
> 数值来自 R068；Out 分钟"归零"为准二值信号，易于扩样达显著。

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

## 5. Results（初步）

| 臂 | 总 kWh | 日间 9–17 kWh | Out 分钟 |
|---|---|---|---|
| baseline | 8.193 | 0.649 | 615 |
| **lockdown** | **12.107（+47.8%）** | **2.558（+294%）** | **0** |

## 6. Comparison with Literature

- 方向与 guide §5.1 及 Xia et al. (2026) 一致（事件驱动的行为/负荷变化）。

## 7. Validity Check

- 事件文本为中性公共卫生告知（无行为指令）→ 非硬编码；
- n=1；Out 归零是准二值信号，须跨成员/世界复现。

## 8. Conclusion

- **初步**：lockdown 使居民整日居家（Out 615→0）、日间负荷激增（+294%）、总电量 +47.8%——
  机制清晰的大效应信号。
- **下一步**：跨成员/世界扩样以判定显著（按"Out 归零"的准二值率）。
