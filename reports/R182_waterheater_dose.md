# R182 — 热水器高剂量靶向（B-x4）：**不削峰，反升**（+16%，受 W1h002 混淆）

- **轮次**：Round 182
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002 M1；baseline×15 + 热水器峰税×15；~120 calls）
- **结论**：⚪ **不削峰（反升）**：总 **+10.7%（p=0.047）**、峰 **+16.0%（p=0.009）**、热水器 **+12.0%（n.s.）**
  → 热水器（"不可替代"）高剂量靶向**未削峰**；且受 **W1 h002 自定义通用事件反升**混淆（R157）。

---

## 1. 目的（B-x4）

检验"**高剂量 + 不可替代 ⇒ 削峰**"预测：对 **热水器**（world_838587 h002 峰占 **20%**，R151；高于 R147 的 8.5%）
施加 20% 峰税，观察是否削峰。

## 2. 方法（可复现）

```powershell
$EV = "2026-09-11|Water-heater peak tax|A 20 percent tax applies to electric water-heater use during the evening peak (5pm to 8pm) today; taking hot showers before 5pm or after 8pm avoids the tax."
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "wh_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "wh_t_$i" --event $EV --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix wh_b --treat-prefix wh_t --n 15 --tag baseline
```

## 3. 结果（n=15）

| 指标 | baseline | 热水器峰税 | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.673 | 9.600 | **+10.7%** | **+2.18** | 0.047 |
| 峰段 16–21 | 3.565 | 4.136 | **+16.0%** | **+3.03** | 0.009 |
| 谷期 22–7 | 2.122 | 2.044 | −3.7% | −0.28 | 0.78（n.s.） |
| **WaterHeater** | 1.800 | 2.017 | **+12.0%** | +1.68 | 0.11（n.s.） |

## 4. 解读

1. **热水器未削、反升**（+12%）：高剂量靶向**未使设备移峰**；
2. **总量/峰反升**（+10.7%/+16.0%）：与 **W1 h002 的"自定义通用事件 → 负荷反升"** 一致（R157，+11~21%）；
   **本实验被该住户特异反应性混淆**（custom event 路径）；
3. **B-x4 结论**：在 W1 h002 上**不可判**（混淆）；需在**无该反应性**的住户（如 W2 h002，R165 同内容对照无抬升）重测；
4. **与 R147 一致**：热水器靶向（低剂量）null；高剂量在此户亦无效（受混淆）。

## 5. 论文更新

- `paper/99_discussion.md`：补"热水器高剂量靶向（R182）→ 未削峰（受 W1 h002 混淆，待 W2 重测）"。

## 6. Validity

- same-era 配对、n=15；**单住户（含已知反升反应性）**、单世界、单日。
- 限制：confounded by W1 h002 custom-event reactivity；待 W2 重测。

## 7. token

- 约 **120 次调用**。
