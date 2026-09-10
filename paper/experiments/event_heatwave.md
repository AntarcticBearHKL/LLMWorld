# Experiment: Heatwave event (环境类事件 → 降温负荷)

> 状态：**初步有效果（单成员，2 个日期窗口复现）**。数值来自 R016/R020；在多人户/多种子复现前，
> 不应作为最终论文结论。

## 1. Research Question

对应 **RQ2**（外部输入的行为传导）与 **RQ3**（宏观涌现/实证对齐）；研究计划"计划"中
社会事件（Phase Three）分支。核心问题：当"热浪"以**自然语言**注入时，LLM 居民是否在
**家电操作层**自发启用降温设备，并使聚合负荷上升？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §5.1）**：热浪 → AirConditioner 使用激增、夏季峰值上升。
- **文献基准（Xia et al. 2026）**：empirical grounding 使 LLM agent 在 disruption（极端天气）下更贴近真人；
  热天负荷显著上升。
- **合理区间**：事件日峰值/负荷上扬；方向为正。

## 3. Experimental Setup

- **World**：`world_838587`，住户 `house_0002`（单人居住；含 `bedroom_1_airconditioner`、Fan）。
- **Dates / Days**：2026-09-11 与 2026-09-12（2 天；`NEWS_MEMORY_KEEP=5`，事件持续两天可见）。
- **Intervention / Command**：
  ```powershell
  # 事件臂（修复事件-天气联动后）
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 `
    --env heatwave_probe2 --event-template "2026-09-11|heatwave" --workers 1
  # 对照臂
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env ctrl_probe --workers 1
  ```
- **Model / Params**：DeepSeek（config.MODEL），`temperature=1.0`，thinking on；`--workers 1`。
- **Analysis**：`load_model.build_load_profile` 重算每日总电量/峰值与降温类分项
  （`appliances.catalog.appliance_family` 聚合）。

## 4. Metrics

- 事件日 vs 对照日 **总电量变化 %**、**峰值 W 与峰时**；
- **降温类分项电量**（AirConditioner / Fan / Dehumidifier / SpaceHeater，kWh）；
- **AC 操作形态**（idle vs use 次数）。

## 5. Results（初步；2 个独立日期窗口）

**Window 1（2026-09-11/12，R016）**

| 臂 / 日 | 总 kWh | 峰 W | 峰时 | AC kWh | AC 操作 |
|---|---|---|---|---|---|
| control 09-11 | 9.682 | 5519.1 | 7 | 0.0 | idle×2 |
| control 09-12 | 12.144 | 5519.1 | 8 | 0.0 | idle×4 |
| heatwave 09-11 | **15.898** | 3121.1 | 22 | **7.2** | use×2, idle×1 |
| heatwave 09-12 | **14.218** | 3818.1 | 18 | **1.8** | use×1 |

**Window 2（2026-10-17/18，R020 复现）**

| 臂 / 日 | 总 kWh | AC kWh | AC 操作 |
|---|---|---|---|
| control 10-17 | 13.874 | 0.0 | — |
| control 10-18 | 11.532 | 0.0 | — |
| heatwave 10-17 | **18.689** | **7.2** | use×5 |
| heatwave 10-18 | **14.616** | **2.4** | use×1 |

- 两窗口一致：**control 的 AC 恒为 0**，**heatwave 的 AC 恒 > 0**（全部 `use`）；
- 日总电量相对对照：W1 **+64.2% / +17.1%**；W2 **+34.7% / +26.7%**；
- 方向与文献预期一致（热浪→降冷负荷上升）。

## 6. Comparison with Literature

- **方向一致**：热浪 → 降温负荷上升、负荷上扬，符合 Xia et al. (2026) 与 guide §5.1 预期。
- **幅度**：因单成员/桩天气，无法与"峰值 +20~40%"等区间做严格对照；**不作幅度结论**。

## 7. Validity Check

- 政策/事件文本是否过强？事件为中性新闻陈述（"temperatures above 38C"），**无行为指令** → 非硬编码；
  行为为涌现（AC 由 idle 变 use）。
- **关键对照**：修复前热浪臂与对照臂 AC 均 idle，仅修复后启用 → 归因指向"事件-环境一致性"而非提示偏置。
- 混杂：n=1、2 天、`temperature=1.0` 的随机性 → **需复现**。

## 8. Conclusion

- **初步（2 窗口复现）**：以自然语言注入的热浪事件可使 LLM 居民自发启用空调、抬升日总电量
  （+17%~+64%），方向与文献一致；两独立日期窗口均复现"control AC=0 / heatwave AC>0"。
  前提是新闻与环境天气**一致**（否则 agent 忽略新闻，见 R014）。
- **可复现命令**：见第 3 节（窗口 2 用 `--date 2026-10-17 --env heatwave_rep/ctrl_rep`）。
- **下一步（升格为正式结果前）**：多人户 × 多种子复现；用 `analyze_event_response.py` 度量事件日模式转移。
