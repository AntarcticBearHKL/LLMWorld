# Experiment: Cold-snap event (`cold_snap`)

> 状态：**初步（n=1）**：cold_snap 使采暖设备由全 0 变为启用（SpaceHeater 3.0 + AC 7.2 kWh），
> 总电量 **+158%**。数值来自 R062；须跨成员/世界复现（同热浪）。

## 1. Research Question

对应 **RQ2**。冬季/寒潮事件以自然语言注入后，居民是否自发启用采暖设备？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §5.1）**：cold_snap → 采暖能耗上升。
- **文献基准**：Xia et al. (2026)（disruption 下行为真实性）；Cabezas-Riviere 2025（采暖/舒适）。
- **合理区间**：事件日采暖设备启用、总电量上升（方向为正）。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（含 SpaceHeater、AC）。
- **Dates / Days**：2026-09-11（1 天）。
- **Intervention / Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env cold_run --event-template "2026-09-11|cold_snap" --workers 1
  # baseline: --env tou_ctl (无政策/事件)
  ```
- **Model / Params**：DeepSeek，thinking on；`--workers 1`；事件经 `engine/news.py` 注入并触发天气联动（ColdSnap/−10°C）。
- **Analysis**：`load_model.build_load_profile` 计算采暖类分项。

## 4. Metrics

采暖类分项（SpaceHeater/AirConditioner）kWh 与**启用率**（>0）、总电量变化 %。

## 5. Results（初步）

| 臂 | 总 kWh | SpaceHeater | AirConditioner |
|---|---|---|---|
| baseline | 8.193 | 0.0 | 0.0 |
| **cold_snap** | **21.140** | **3.000** | **7.200** |

总电量 **+158%**；采暖设备由全 0 → 启用（二值信号）。

## 6. Comparison with Literature

- 方向与 guide §5.1 及 Xia et al. (2026) 一致（事件驱动的行为变化）。

## 7. Validity Check

- n=1；事件与天气一致（R015 联动机制）→ 非提示偏置的排除需复现；
- 与热浪对称，属"大效应二值"类型（R058）。

## 8. Conclusion

- **初步**：cold_snap 可使 LLM 居民自发启用采暖（+158%），与热浪对称。
- **下一步**：按热浪同法（跨成员/跨世界）扩展样本，检验启用率是否同样显著。
