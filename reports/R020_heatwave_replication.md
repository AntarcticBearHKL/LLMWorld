# R020 — 热浪效应复现（第 2 个日期窗口）

- **轮次**：Round 20
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（同世界/住户/成员，两条日期窗口各 `heatwave` vs `control`）
- **结论**：✅ **效应复现**（control AC 恒 0；heatwave AC 恒 > 0，方向一致）

---

## 1. 目标

R016 首次观测到"热浪→空调启用、总电量上升"，但仅 **n=1 成员、1 个日期窗口**。
本轮在**第二个日期窗口**（2026-10-17/18）重复 heatwave vs control，检验稳健性。

## 2. 设计（可复现）

- world `world_838587`；house `house_0002`；member `Member 1`；`--days 2`；`--workers 1`；
- heatwave：`--date 2026-10-17 --env heatwave_rep --event-template "2026-10-17|heatwave"`
- control：`--date 2026-10-17 --env ctrl_rep`
- 离线 `load_model.build_load_profile` 重算。

## 3. 结果（与 R016 合并）

| 窗口 / 臂 / 日 | 总 kWh | AC kWh | AC 操作 |
|---|---|---|---|
| W1 control 09-11 | 9.682 | 0.0 | idle×2 |
| W1 control 09-12 | 12.144 | 0.0 | idle×4 |
| W1 heatwave 09-11 | **15.898** | **7.2** | use×2, idle×1 |
| W1 heatwave 09-12 | **14.218** | **1.8** | use×1 |
| W2 control 10-17 | 13.874 | 0.0 | — |
| W2 control 10-18 | 11.532 | 0.0 | — |
| W2 heatwave 10-17 | **18.689** | **7.2** | use×5 |
| W2 heatwave 10-18 | **14.616** | **2.4** | use×1 |

**派生**：
- **control AC 在全部 4 个 control-day 恒为 0**；**heatwave AC 在全部 4 个 heatwave-day 恒 > 0**；
- 日总电量相对对照：W1 `+64.2% / +17.1%`；W2 `+34.7% / +26.7%`；
- 两窗口方向一致，支持"热浪→降冷负荷上升"。

## 4. 解读与限制

- **复现**提升了 R016 结论的可信度（跨日期窗口一致；control 全 0 是关键对照）。
- **仍非统计显著**：n=1 成员、`temperature=1.0` 的 LLM 随机性、天气为桩函数（固定 +12C）。
  幅度（+17%~+64%）**不可**直接对照文献的"峰值 +20~40%"。
- 结论**初步**，已同步进 `paper/experiments/event_heatwave.md`（第 5 节含两窗口表）。

## 5. token 消耗（估算）

- 本轮 2 臂 × (4 步 × 2 天) ≈ **16 次调用**。

## 6. 产物归档

- `reports/R020_heatwave_replication.md`（本文件）；
- `paper/experiments/event_heatwave.md` 更新（第 5 节两窗口 + 结论）；
- `paper/README.md`：状态更新为 `有效果(初步,2窗口复现)`。

## 7. 下一步

1. 多人户 × 多种子正式复现（token-gated）；
2. `analyze_event_response.py` 模式转移度量；
3. `population_runner.py`（peer-nudge / policy-schedule）恢复或 guide 校正。
