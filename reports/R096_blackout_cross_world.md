# R096 — C1：`blackout_risk` 跨世界复现（方向一致，幅度较弱）

- **轮次**：Round 96
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002 M1；baseline 复用+2新 vs blackout_risk×3；~20 calls）
- **结论**：✅ **方向跨世界复现**（world_838587 −31.7%、world_172148 −11.7%）；但第 2 世界幅度较弱、方差大

---

## 1. 目标（C1）

`blackout_risk` 在 world_838587 上显著削峰（−31.7%，R094）。本轮在**第二世界** world_172148 复现，
检验普适性（提升为跨世界结论）。

## 2. 设计（可复现）

```powershell
# world_172148 house_0002 Member 1, 1 天
python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env bp172_1 --workers 1
python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env bp172_2 --workers 1
foreach ($i in 1,2,3) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env "bo172_$i" --event-template "2026-09-11|blackout_risk" --workers 1
}
# baseline 另含既有 nw_ctl
```

指标：峰段(16–21) kWh。

## 3. 结果

| 世界 | baseline peak_win (n=3) | blackout_risk (n=3) | 变化 | z |
|---|---|---|---|---|
| world_838587 | 4.686 ± 0.154 | 3.203 ± 0.298 | **−31.7%** | −9.6 |
| **world_172148** | **3.461 ± 0.187** | **3.056 ± 0.645** | **−11.7%** | −2.2 |

## 4. 解读

- **方向跨世界一致**（两世界均负）→ `blackout_risk` 削峰**可复现**；
- **幅度异质**：第 2 世界弱得多（−11.7% vs −31.7%），且 treatment 方差大（std 0.645）→ 与"不同群体响应分化"一致；
- 与 R058 一致：中等效应在低噪峰段指标上**可检出但不强**；
- **限制**：各 n=3、单成员、1 天；须更多成员/世界方能给幅度区间。

## 5. token 消耗（估算）

- 5 个 run × (4 步 × 1 成员 × 1 天) ≈ **20 次调用**。

## 6. 论文更新

- `paper/experiments/event_blackout_risk.md`：state → **跨 2 世界方向复现（−11.7%~−31.7%）**；
- `paper/README.md`：状态更新。

## 7. 结论

`blackout_risk` 削峰**跨 2 世界方向复现**（−11.7%~−31.7%），幅度世界异质。列入 `paper` 有效结果。
下一步：如需更强结论，扩成员/世界（C1 续）或用峰段低噪指标评估更多干预。
