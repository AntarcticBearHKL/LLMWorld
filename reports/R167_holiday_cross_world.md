# R167 — 公共假日**跨世界复现** ✅：总电量 W1 +48.3% / W2 +31.9%（升级为 headline 级事件）

- **轮次**：Round 167
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 M1；baseline×15 + `holiday`×15；~120 calls）
- **结论**：✅ **跨世界复现**：R166（W1 +48.3%, p=3.5e-4）→ 本轮（W2 **+31.9%, t=+8.92, p=3.8e-7**）；
  **照明/TV/烹饪**在**两世界**均显著上升 → holiday 升为 **cross-world✅ 事件效应**（第 5 个）。

---

## 1. 目的

R166 的 holiday 效应（+48.3%）为**单世界**，违反红线 3。本轮在 **world_172148 h002** 同法复现。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "hol2_b_$i" --workers 1
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "hol2_h_$i" --event-template "2026-09-11|holiday" --workers 1
}
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix hol2_b --treat-prefix hol2_h --n 15 --tag baseline
```

## 3. 结果（n=15，两世界对照）

| 指标 | W1 `world_838587` h002 | W2 `world_172148` h002 | 复现? |
|---|---|---|---|
| **总电量** | **+48.3%**（t=4.68, p=3.5e-4） | **+31.9%**（t=8.92, p=3.8e-7） | ✅ **是** |
| 峰段 16–21 | +7.8%（n.s.） | **+24.9%**（t=2.28, p=0.039） | 方向一致，幅度世界相关 |
| 谷期 22–7 | −25.7%（n.s.） | **−53.1%**（t=−4.66, p=3.7e-4） | 方向一致 |
| 峰值功率 | +10.9%（n.s.） | +3.8%（n.s.） | 均 n.s. |
| kitchen_light | **+92.9%**（t=5.90） | **+93.4%**（t=5.47） | ✅ 强复现 |
| living_room_tv | **+64.7%**（t=3.53） | **+109.4%**（t=7.87） | ✅ 强复现 |
| InductionCooker | **+35.5%**（t=4.04） | **+33.6%**（t=6.57） | ✅ 强复现 |
| bathroom_light | +43.8%（t=3.64） | +29.5%（t=3.11） | ✅ 复现 |

## 4. 解读

1. **跨世界稳健**：总量、照明、TV、烹饪在**两世界**均显著上升 → holiday = **stay-home 事件**，
   机制与 lockdown 同型（Xia 2026），幅度更温和/世界相关（+32%~+48%）；
2. **谷期大降**（W2 −53.1%）：居家使作息前移/夜间用电减少 → 负荷形态由"晚峰"转向"日间"；
3. **峰段**：W1 n.s.、W2 +24.9% 显著 → **方向一致（升），幅度世界特异**，不作精确断言；
4. **升级**：holiday 现满足**跨 2 世界**（红线 3）→ 建议列为**第 5 个 headline 事件效应**。

## 5. 论文更新

- `paper/README.md`：headline 表新增 **公共假日 → 总电量 +32~48%（跨 2 世界）**；
  实验行状态改"有效果（跨 2 世界）"。
- `paper/experiments/event_holiday.md`：补 §5 跨世界表 + §7 升级为 cross-world。

## 6. Validity

- same-era 配对、n=15、**跨 2 世界**；每世界单户、单日。
- 限制：仍缺第 3 世界 / 多户；峰段幅度未定。

## 7. token

- 约 **120 次调用**（baseline×15 + holiday×15）。
