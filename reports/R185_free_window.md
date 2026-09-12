# R185 — "免费电窗口"事件：**谷段填充方向**但 **null**（midday +90% 名义，p=0.31）

- **轮次**：Round 185
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002 M1；baseline×15 + "12–14h 免费电"×15；~120 calls）
- **结论**：⚪ **null（方向为谷段填充）**：midday 12–14h **+90% 名义**（0.204→0.387 kWh）但 **t=1.06, p=0.31 n.s.**；
  总 −3.3%、峰 −7.3%、谷 −12.7%（均 n.s.）→ 方向与"免费电吸引用电"一致，但**低于功效下限**。

---

## 1. 目标

新颖"**谷段填充**"测试（削峰的反面）：宣布 **12:00–14:00 免费**，检验 agents 是否把用电移向该窗口
（动态定价文献 Faruqui & Sergici 2010 的 valley-filling 方向）。

## 2. 方法（可复现）

```powershell
$EV = "2026-09-11|Free electricity at midday|Electricity is free between 12:00 and 14:00 today; any energy used in this window costs nothing."
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "free_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "free_t_$i" --event $EV --workers 1
}
```

## 3. 结果（n=15）

| 指标 | baseline | 免费窗口 | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.920 | 8.630 | −3.3% | −0.64 | 0.53（n.s.） |
| 峰段 16–21 | 3.784 | 3.506 | −7.3% | −0.84 | 0.42（n.s.） |
| 谷期 22–7 | 1.901 | 1.659 | −12.7% | −0.67 | 0.51（n.s.） |
| **midday 12–14** | 0.204 | 0.387 | **+90.0%** | 1.06 | **0.31（n.s.）** |

## 4. 解读

1. **方向正确**：midday +90%、峰 −7.3%、谷 −12.7% → 移向免费窗口的迹象；
2. **不显著**：midday 绝对增量仅 **+0.18 kWh**，远低于噪声地板（std≈1 kWh，R057）→ **不可判**（R058）；
3. **与价格型 null 一致**：数值价格信号（TOU/CPP/税）在此平台**难以分辨**；
4. **意义**：作为"谷段填充"的**方向性证据**（非结论），提示 agents 对"免费"措辞有**弱**反应。

## 5. 论文更新

- `paper/README.md` / `99_discussion.md`：补"免费电窗口 → 谷段填充方向但 null（R185）"。

## 6. Validity

- same-era 配对、n=15；单住户、单世界、单日。
- 限制：绝对效应低于平台下限；"免费"措辞强度未变体测试。

## 7. token

- 约 **120 次调用**。
