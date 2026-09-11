# R097 — C1：`price_hike` 跨世界**未复现**（不稳定 → 降级）

- **轮次**：Round 97
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002 M1；price_hike×3；baseline 复用；~12 calls）
- **结论**：❌ **未复现**：world_838587 −17.9%、world_172148 **+6.8%**（z=1.26）→ `price_hike` 削峰**世界特异/不稳定**

---

## 1. 目标（C1）

`price_hike` 在 world_838587 上显著削峰（−17.9%，R094）。本轮在 world_172148 复现。

## 2. 设计（可复现）

```powershell
foreach ($i in 1,2,3) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env "pi172_$i" --event-template "2026-09-11|price_hike" --workers 1
}
# baseline 复用 nw_ctl + bp172_1 + bp172_2
```

指标：峰段(16–21) kWh。

## 3. 结果

| 世界 | baseline 峰段 (n=3) | price_hike 峰段 (n=3) | 变化 | z |
|---|---|---|---|---|
| world_838587 | 4.686 ± 0.154 | 3.849 ± 0.635 | **−17.9%** | −5.4 |
| **world_172148** | 3.461 ± 0.187 | 3.696 ± 0.761 | **+6.8%** | +1.26 |

## 4. 解读

- **方向不一致**：第 1 世界削峰 −17.9%，第 2 世界反而 +6.8% → **`price_hike` 不稳定**；
- 与 `blackout_risk` 对比形成清晰对照：
  - `blackout_risk`：跨 2 世界**同向**（−31.7% / −11.7%）= **可复现（方向）**；
  - `price_hike`：跨 2 世界**反向**（−17.9% / +6.8%）= **不可复现**（与 R026 的 TOU 类似，措辞/采样敏感）；
- **修正 R094 的初步结论**：不能声称 price_hike 削峰；降级为"不稳定/世界特异"。

## 5. token 消耗（估算）

- 3 个 run × (4 步 × 1 成员 × 1 天) ≈ **12 次调用**。

## 6. 论文更新

- `paper/experiments/event_price_hike.md`：状态 → **未复现/不稳定**；第 5 节加第 2 世界结果；
- `paper/README.md`：状态 → 否定/不稳定。

## 7. 结论

`price_hike` 削峰**未跨世界复现**（−17.9% → +6.8%），**降级**。
`blackout_risk` 仍是唯一跨世界（方向）复现的削峰事件。
