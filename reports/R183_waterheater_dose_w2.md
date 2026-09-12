# R183 — 热水器高剂量靶向 W2 重测：**仍不削峰（峰 +26.7%）**；B-x4 **不可定论**

- **轮次**：Round 183
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 M1；baseline×15 + 热水器峰税×15；~120 calls）
- **结论**：⚪ **不削峰**：峰 **+26.7%（t=+3.64, p=0.003）**、热水器 **+2.6%（n.s.）**、总 +3.7%（n.s.）
  → 去混淆后**仍未见削峰**；但 W2 h002 热水器占比低 → **B-x4（高剂量）不可定论**。

---

## 1. 目的

R182 在 W1 h002（高剂量 20%）受"自定义事件反升"混淆。本轮在 **W2 h002**（R165 证其**无**该反应性）重测同一热水器峰税。

## 2. 方法（可复现）

```powershell
$EV = "2026-09-11|Water-heater peak tax|A 20 percent tax applies to electric water-heater use during the evening peak (5pm to 8pm) today; taking hot showers before 5pm or after 8pm avoids the tax."
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "wh2_b_$i" --workers 1
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "wh2_t_$i" --event $EV --workers 1
}
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix wh2_b --treat-prefix wh2_t --n 15 --tag baseline
```

## 3. 结果（n=15）

| 指标 | baseline | 热水器峰税 | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 9.652 | 10.008 | +3.7% | +0.71 | 0.49（n.s.） |
| 峰段 16–21 | 3.395 | 4.303 | **+26.7%** | **+3.64** | 0.003 |
| 谷期 22–7 | 2.545 | 1.891 | −25.7% | −2.12 | 0.052 |
| **WaterHeater** | 1.900 | 1.950 | **+2.6%** | +0.19 | 0.85（n.s.） |

## 4. 解读

1. **去混淆后仍不削峰**：W2 h002 无自定义事件反应性（R165），热水器峰税仍使**峰 +26.7%**、热水器**不变**（+2.6%）；
2. **两世界一致**：W1（+16.0%）与 W2（+26.7%）**水器税均抬峰**（奇特，但与"通用/模糊税信号不削峰"一致）；
3. **B-x4 不可定论**：W1 h002 高剂量（20%）但与反应性混淆；W2 h002 无混淆但**热水器占比低**（非高剂量）→
   **无满足"高剂量 + 无混淆"的住户**；
4. **对机制的限定**：热水器（"可推迟不可替代"）靶向**未见削峰**——与"仅设备+窗口联合锚定且设备真正响应（AC）才削峰"一致。

## 5. 论文更新

- `paper/99_discussion.md`：补"热水器靶向（R147/R182/R183）→ 三例均未削峰"。

## 6. Validity

- same-era 配对、n=15；单住户、单世界、单日。
- 限制：无"高剂量 + 无混淆"住户 → B-x4 留待满足条件的世界。

## 7. token

- 约 **120 次调用**。
