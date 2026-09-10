# R049 — 热浪跨成员（house_0001 M1/M2/M3）：2/3 启用空调

- **轮次**：Round 49
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（house_0001 三成员，各 1 天；heatwave vs 同成员 baseline）
- **结论**：✅ 方向成立且更细：**baseline 三成员 AC 全 0；heatwave 下 2/3 启用空调**（M3 未用）

---

## 1. 目标

R016/R020/R022/R043 显示热浪在单成员上触发空调。本轮在 house_0001 的**三个成员**上配对测试，
检验"热浪→空调"是否**跨成员**成立，以及是否存在**异质性**。

## 2. 设计（可复现）

- 基线复用：M1 `ctrl_h1`（R022）、M2 `m2_ctl`、M3 `m3_ctl`（R048，均无政策无事件）；
- 新跑热浪臂（仅 2 个 run）：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0001 --member 1 --days 1 --env m2_hw --event-template "2026-09-11|heatwave" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0001 --member 2 --days 1 --env m3_hw --event-template "2026-09-11|heatwave" --workers 1
  ```
  （M1 热浪臂 `hw_h1` 复用 R022。）
- 共享空调 uid：`living_room_airconditioner`（Living Room）。

## 3. 结果（2026-09-11）

| 成员 | 臂 | 总 kWh | AC kWh | AC 操作 |
|---|---|---|---|---|
| Member 1 | baseline | 10.081 | 0.000 | — |
| Member 1 | **heatwave** | 13.788 | **3.600** | use（19:30–22:30） |
| Member 2 | baseline | 10.566 | 0.000 | — |
| Member 2 | **heatwave** | 10.261 | **1.500** | use（21:00–22:15） |
| Member 3 | baseline | 12.609 | 0.000 | — |
| Member 3 | **heatwave** | 10.620 | **0.000** | — |

**派生**：
- **baseline 三成员 AC 恒 0**（强对照）；
- **heatwave 下 2/3 成员启用空调**（M1 3.6、M2 1.5 kWh），**M3 未用**（异质性）。

## 4. 解读

- **方向更稳健**：跨 3 成员，baseline 全 0，heatwave 多数启用 → 事件→降温行为的**方向**成立。
- **异质性可观测**：M3 未启用空调 → 与"同一信号、个体分化"一致（可对接 RQ3）。
- **总电量非稳健信号**：M2/M3 的 heatwave 总量反低于 baseline（其他家电随机波动），
  再次说明应看**二进制/定性信号**（AC on/off）而非单成员总量幅度。

## 5. token 消耗（估算）

- 本轮 2 个热浪 run × (4 步 × 1 天) ≈ **8 次调用**（基线复用）。

## 6. 论文更新

- `paper/experiments/event_heatwave.md`：新增多成员表，结论补充"baseline 3/3 AC=0、heatwave 2/3 AC>0（含异质性）"。

## 7. 下一步（候选）

1. 用 `analyze_groups.py` 检查 AC 启用的异质性是否与 awareness/尽责性相关；
2. 继续为 TOU 增加多成员样本（或正式标注"不可评估"）。
