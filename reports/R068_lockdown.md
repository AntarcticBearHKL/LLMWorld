# R068 — lockdown 事件：居家时间激增（第三个大效应信号）

- **轮次**：Round 68
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 house_0002 M1；lockdown vs baseline；~4 calls）
- **结论**：✅ **大效应且机制清晰**：外出行程 **615 → 0 分钟**；日间(9–17)负荷 **0.649 → 2.558 kWh（+294%）**；总电量 **+47.8%**

---

## 1. 目标

R066 指出"大效应二值/事件"是可继续的低成本方向。本轮测试 `lockdown`（guide §5.1：居家时间增加 →
日间用量上升），是否为机制清晰的大效应。

## 2. 设计（可复现）

```powershell
# baseline 复用 tou_ctl
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
  --env lockdown_run --event-template "2026-09-11|lockdown" --workers 1
```

- 评估：`load_model` 总电量/日间段；`s1_macro` 的 `Out` 分钟数。

## 3. 结果（2026-09-11）

| 臂 | 总 kWh | 日间 9–17 kWh | Out 分钟 |
|---|---|---|---|
| baseline | 8.193 | 0.649 | **615** |
| **lockdown** | **12.107（+47.8%）** | **2.558（+294%）** | **0** |

- 外出行程**完全消失**（615→0 分钟）——成员整日居家；
- 日间(9–17)负荷激增（很可能是居家空调/照明/娱乐）；
- 总电量 +47.8%。

## 4. 解读

- **机制清晰**：lockdown 直接改变 s1 宏观计划的"是否外出"，属**大效应/准二值**信号（Out 从 615→0）；
- 与 R058 一致：大效应可判，且**因果链明确**（事件→居家→日间负荷）；
- **限制**：n=1；须如热浪/寒潮那样跨成员/世界复现方可显著。

## 5. token 消耗（估算）

- 1 个 lockdown run × (4 步 × 1 成员 × 1 天) ≈ **4 次调用**。

## 6. 论文更新

- 新增 `paper/experiments/event_lockdown.md`（初步）；
- `paper/99_discussion.md` RQ2：新增 lockdown 初步条；
- `paper/README.md`：新增清单行。

## 7. 下一步

为 lockdown 扩样（Out 分钟数的"归零"是准二值信号，易达显著）。
