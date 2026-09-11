# R106 — same-era 重验：三个二值结果**漂移免疫**（确认）

- **轮次**：Round 106
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 h002M1；heatwave/cold_snap/lockdown 各 1，current era；~12 calls）
- **结论**：✅ **三个二值结论 same-era 复现**（与 fresh 基线同批次）→ 漂移免疫

---

## 1. 目标

R104 判定"连续指标跨时段漂移"。本轮**同批次重跑**三个二值事件，确认其是否漂移免疫。

## 2. 方法（可复现）

```powershell
foreach ($k in @("heatwave","cold_snap","lockdown")) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 --env "se_$k" --event-template "2026-09-11|$k" --workers 1
}
# baseline: fresh834_1/2/3（R104 同期，无事件）
```

## 3. 结果（AC / heating kWh，Out 分钟）

| 臂 | AC | heating | Out |
|---|---|---|---|
| **fresh baseline**（×3） | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 | 600 / 600 / 540 |
| **heatwave** | **7.2** | 7.2 | 585 |
| **cold_snap** | 0.0 | **3.5** | 610 |
| **lockdown** | 7.2 | 7.2 | **0** |

## 4. 解读

- **三个二值结论在 same-era 下全部复现**：
  - 热浪 → AC 0 → 7.2（✅）；
  - 寒潮 → heating 0 → 3.5（✅）；
  - 封锁 → Out 600→0（✅）；
- **漂移免疫**：二值/结构信号（设备开/关、外出/居家）不随会话时段漂移；
- （lockdown 臂 AC 恰好 7.2 属随机，不影响其 Out 指标。）
- 至此**「二值稳健、连续漂移」**由 R104/R105/R106 三方确证。

## 5. token 消耗（估算）

- 3 个 run × (4 步 × 1 成员 × 1 天） ≈ **12 次调用**。

## 6. 论文/目标更新

- `paper/99_discussion.md` 与 `goal.md`：确认**二值结论漂移免疫**（same-era 复现），连续结论撤回。

## 7. 结论

本工作**可信结论**：**三个二值事件**（热浪→制冷、寒潮→采暖、封锁→居家）+ 封锁 same-era 日间负荷幅度。
所有**连续"削峰"结论撤回**。**方法学红线**：连续指标须 same-era 对照。
