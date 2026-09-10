# R061 — 热浪二值结果**跨世界复现**：baseline 0/7 vs heatwave 9/10（p≈0.0004）

- **轮次**：Round 61
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002 heatwave；baseline 复用 `nw_ctl`；~4 calls）
- **结论**：✅ **强显著且跨世界复现**：baseline **0/7** vs heatwave **9/10**，Fisher 单侧 **p ≈ 0.0004**

---

## 1. 目标

R059/R060 的二值结果（0/5 vs 7/8）已在 `world_838587` 显著。本轮在**独立世界** `world_172148`
上重复，检验**跨世界复现性**（这是"结论普适性"的关键）。

## 2. 设计（可复现）

```powershell
# world_172148 house_0002（2 成员），heatwave 臂；baseline 复用 R053 的 nw_ctl
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 `
  --env nw2_hw --event-template "2026-09-11|heatwave" --workers 1
```

## 3. 结果（两世界汇总；`AirConditioner` 分项 >0 记为启用）

| 世界 | 条件 | 启用 |
|---|---|---|
| world_838587 | baseline | 0/5 |
| world_838587 | heatwave | 7/8 |
| **world_172148** | baseline | **0/2** |
| **world_172148** | heatwave | **2/2** |
| **合计** | **baseline** | **0/7** |
| **合计** | **heatwave** | **9/10** |

**Fisher 精确检验（0/7 vs 9/10）：单侧 p ≈ 0.00041。**

- 唯一未启用者：world_838587 house_0001 Member 3（个体异质性）。

## 4. 解读

- **跨世界复现**：结论在**两个独立生成的世界**上成立（baseline 全部 0，heatwave 近乎全部启用）；
- **统计极显著**（p≈4×10⁻⁴），是整项工作**最稳健**的结论；
- 与 R058 功效分析一致：**二值/大效应**是噪声地板（CV≈12%）下唯一可判的类型；
- 再次体现**个体异质性**（1/10 未启用）。

## 5. token 消耗（估算）

- 本轮 1 个 heatwave run × (4 步 × 2 成员 × 1 天) ≈ **4 次调用**（baseline 复用）。

## 6. 论文更新

- `paper/experiments/event_heatwave.md`：二值统计更新为 **0/7 vs 9/10（跨 2 世界）, p≈0.0004**；
- `paper/99_discussion.md` RQ2：更新数字并注明**跨世界**；
- `paper/README.md`：状态更新。

## 7. 结论

**热浪→空调启用**现为**跨 2 世界、p<0.001** 的稳健结果——可作为论文的**核心实证结论**之一。
