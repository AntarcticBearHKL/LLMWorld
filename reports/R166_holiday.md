# R166 — 公共假日事件：**总电量 +48.3%（p≈0.0004）**（stay-home 效应；峰值不显著）

- **轮次**：Round 166
- **日期**：2026-09-12
- **验证层级**：**L1**（278 单测全绿）+ **L2 真调**（world_838587 h002 M1；baseline×15 + `holiday`×15；~120 calls）
- **结论**：✅ **新事件效应**：公共假日使总电量 **+48.3%（t=+4.68, p≈0.0004）**，
  由 **stay-home** 行为驱动（照明/TV/烹饪↑）；峰段 **+7.8%（n.s.）**。

---

## 1. 目标（补计划点名缺口）

`研究计划.md §4.3 Phase Three` 明确点名 **public holidays**，但 `news.py` 10 模板中**没有** holiday。
新增预设事件 `holiday` 并检验其行为效应（对照 lockdown / Xia et al. 2026 的 disruption 范式）。

## 2. 改动

- `src/engine/news.py`：`NEWS_TEMPLATES` 新增 `holiday`（"Today is a public holiday; most workplaces and
  schools are closed and people are staying at home."）→ **11 模板**。
- `tests/test_news.py`：更新为 11 模板 + 名称集合含 `holiday`。**278 绿**。

## 3. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "hol_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "hol_h_$i" --event-template "2026-09-11|holiday" --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix hol_b --treat-prefix hol_h --n 15 --tag baseline
```

## 4. 结果（n=15，配对 t，df=14）

| 指标 | baseline | holiday | Δ | t | p |
|---|---|---|---|---|---|
| **总电量** | 8.239 | 12.220 | **+48.3%** | **+4.68** | **0.0004** |
| 峰段 16–21 | 3.395 | 3.661 | +7.8% | +0.74 | 0.47（n.s.） |
| 谷期 22–7 | 1.963 | 1.458 | −25.7% | −1.27 | 0.23（n.s.） |
| 峰值功率 | 3667 | 4066 | +10.9% | +1.01 | 0.33（n.s.） |
| kitchen_light | 0.069 | 0.133 | **+92.9%** | **+5.90** | <0.001 |
| living_room_light | 0.088 | 0.197 | **+125.4%** | **+5.01** | <0.001 |
| living_room_tv | 0.347 | 0.572 | **+64.7%** | **+3.53** | 0.003 |
| InductionCooker | 2.567 | 3.478 | **+35.5%** | **+4.04** | 0.001 |
| bathroom_light | 0.050 | 0.072 | +43.8% | +3.64 | 0.003 |

## 5. 解读

1. **假日 = stay-home 事件**：总电量 **+48.3%（p<0.001）**，增益集中在**日间**（峰 +7.8% n.s.、谷 −25.7% n.s.，
   增加落在肩段 9–16h）；
2. **行为通道清晰**：照明（厨房 +92.9%、客厅 +125.4%）、TV（+64.7%）、烹饪（+35.5%）齐升 →
   与"居家时间增加 → 日间用电上升"一致；
3. **与 lockdown 同型但更温和**：lockdown（R068/R107，Xia 2026）→ Out 归零、日间 **+220.7%**；
   假日无强制居家 → 总量 +48.3%（同方向、幅度小）；
4. **与 headline 一致**：结构性/社会事件（heatwave/lockdown/cold_snap）能强烈改变行为与负荷形态。

## 6. 文献对比

| 来源 | 预期 | 本研究 |
|---|---|---|
| Xia et al. 2026（disruption → 居家行为改变） | 日间用量上升 | **+48.3% 总电量** ✅（同 lockdown 型） |
| 计划 §4.3 Phase Three（public holidays） | 行为改变 | **显著** ✅ |

## 7. Validity

- same-era 配对、n=15；**单住户、单世界、单日** → **跨世界待验**（红线 3），
  故暂列 **"有效果（单世界）"**，未入 headline（须跨世界复现）。

## 8. token

- 约 **120 次调用**（baseline×15 + holiday×15）。
