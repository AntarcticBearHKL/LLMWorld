# R022 — 热浪效应跨住户复现（house_0001 Member 1）

- **轮次**：Round 22
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（第 2 个住户的 heatwave vs control，1 天）
- **结论**：✅ **跨住户复现**（control AC=0；heatwave AC=3.6 kWh，总量 +36.8%）

---

## 1. 目标

R016/R020 在 `house_0002`（单人）复现了"热浪→空调启用"。本轮换到**第二个住户**
`house_0001` 的 `Member 1`（其空调为 `living_room_airconditioner`），检验是否**跨住户**成立。

## 2. 设计（可复现）

- world `world_838587`；house `house_0001`；member `Member 1`；`--days 1`；`--workers 1`；日期 2026-09-11；
- heatwave：`--env hw_h1 --event-template "2026-09-11|heatwave"`
- control：`--env ctrl_h1`
- 离线 `load_model.build_load_profile` 重算。

## 3. 结果

| 臂 | 总 kWh | 峰 W | AC kWh | AC 操作 |
|---|---|---|---|---|
| control_h1 | 10.081 | 3317.8 | 0.0 | — |
| heatwave_h1 | **13.788** | 3317.8 | **3.6** | use（19:30–22:30） |

- 总量较对照 **+36.8%**；AC 由 0 → 3.6 kWh（占 heatwave 总量 ≈26%）；
- 与 `house_0002` 的模式一致。

## 4. 汇总（跨住户）

| 住户 / 日 | control AC | heatwave AC |
|---|---|---|
| house_0002 09-11 | 0.0 | 7.2 |
| house_0002 09-12 | 0.0 | 1.8 |
| house_0002 10-17 | 0.0 | 7.2 |
| house_0002 10-18 | 0.0 | 2.4 |
| house_0001 09-11 | 0.0 | 3.6 |

**3 个 event-day / 3 个 control-day、2 个住户**：模式完全一致（control 全 0；heatwave 全 > 0）。

## 5. 解读与限制

- 跨住户复现显著增强 R016/R020 结论；关键对照是 control 的 AC **恒为 0**。
- **仍非统计显著**：每户 n=1 成员、`temperature=1.0`、天气为桩（固定 +12C）；幅度不可对照文献区间。
- 结论**初步**，已同步 `paper/experiments/event_heatwave.md`（新增 Window 3 与汇总）。

## 6. token 消耗（估算）

- 本轮 2 臂 × (4 步 × 1 天) ≈ **8 次调用**。

## 7. 产物

- `reports/R022_heatwave_house2.md`（本文件）；
- `paper/experiments/event_heatwave.md`（Window 3 + 汇总 + 状态）；
- `paper/README.md` 状态 `有效果(初步,2户3天复现)`。

## 8. 下一步

1. **多种子/多人户**正式复现（token-gated）；
2. 定价（TOU/subsidy）效应实验；
3. `population_runner.py` 恢复或正式废弃。
