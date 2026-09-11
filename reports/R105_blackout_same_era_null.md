# R105 — same-era 验证：blackout_risk **无削峰**（伪影确证）

- **轮次**：Round 105
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 h002M1；blackout_risk×3 与 fresh834 基线同期；~12 calls）
- **结论**：❌ **确证伪影**：same-era 下 blackout_risk 峰段 **+15.9%**（未降，且在噪声内）

---

## 1. 目标

R104 判定早前"削峰"为基线漂移伪影。本轮做**决定性 same-era 验证**：在同一批次时代
（与 `fresh834` 基线同期）跑 **3 个** `blackout_risk`，与 fresh 基线直接比较。

## 2. 方法（可复现）

```powershell
foreach ($i in 1,2,3) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 --env "fb834_$i" --event-template "2026-09-11|blackout_risk" --workers 1
}
# baseline: fresh834_1/2/3（R104 同期，无事件）
```

## 3. 结果（峰段 16–21 kWh）

| 臂 | vals | mean | std |
|---|---|---|---|
| fresh baseline | 3.472 / 3.098 / 3.753 | **3.441** | 0.268 |
| fresh blackout_risk | 5.018 / 3.474 / 3.472 | **3.988** | 0.728 |

**same-era effect = +15.9%**（未下降；且差异 < 处理 std）→ **无削峰**。

## 4. 解读

- **确证 R104**：早前 −7%~−32% 的"削峰"纯属**拿旧基线（4.686）比较**的伪影；
- **same-era 下无效应**（+15.9%，噪声内）；
- 至此 `blackout_risk`（及 `price_hike`、屏幕四事件）的**连续削峰结论全部撤回**；
- **二值结论不受影响**（热浪/寒潮/封锁：旧、新基线的设备态均=0）。

## 5. token 消耗（估算）

- 3 个 run × (4 步 × 1 成员 × 1 天） ≈ **12 次调用**。

## 6. 论文更新

- `event_blackout_risk.md`：补 same-era null 确认（已撤回连续结论）。

## 7. 结论

**R104/R105 共同确立红线**：跨时段比较**连续指标**无效；**same-era（同批次紧邻）**或**二值/结构**指标方可靠。
本工作可信结论**仅剩三个二值事件**（热浪/寒潮/封锁）+ 封锁的 same-era 幅度。
