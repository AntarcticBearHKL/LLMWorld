# R168 — 公共假日第 3 世界复现 ✅：总电量 +39.8%（跨 3 世界达成）

- **轮次**：Round 168
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_143345 h002 M1；baseline×15 + `holiday`×15；~120 calls）
- **结论**：✅ **跨 3 世界达成**：总电量 **+39.8%（t=+3.98, p=0.0014）**；
  **峰段方向世界相关**（W1 +7.8% n.s. / W2 +24.9% / **W3 −15.2% n.s.**）→ 总量效应稳健、峰效应不稳健。

---

## 1. 目的

holiday 已跨 2 世界（R166/R167）。本轮补 **world_143345 h002**，与其它 headline 一致达成 **跨 3 世界**。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_143345 --house house_0002 --member 0 --date 2026-09-11 --env "hol3_b_$i" --workers 1
  python run.py --mode simulate --world world_143345 --house house_0002 --member 0 --date 2026-09-11 --env "hol3_h_$i" --event-template "2026-09-11|holiday" --workers 1
}
python src/analyze/compare_cpp.py --world world_143345 --house house_0002 --date 2026-09-11 --base-prefix hol3_b --treat-prefix hol3_h --n 15 --tag baseline
```

## 3. 结果（n=15，三世界对照）

| 指标 | W1 `838587` | W2 `172148` | **W3 `143345`** | 一致性 |
|---|---|---|---|---|
| **总电量** | **+48.3%**（p=3.5e-4） | **+31.9%**（p=3.8e-7） | **+39.8%**（t=3.98, **p=0.0014**） | ✅ **3/3 显著** |
| 峰段 16–21 | +7.8%（n.s.） | +24.9%（p=0.039） | **−15.2%**（n.s.） | ⚠️ 方向不一致 |
| 谷期 22–7 | −25.7%（n.s.） | −53.1% | −18.3%（n.s.） | 方向一致 |
| study_computer | — | — | **+107.9%**（t=4.85） | stay-home 通道 |
| study_light | — | — | **+116.7%**（t=2.95） | stay-home 通道 |

## 4. 解读

1. **总量跨 3 世界稳健**（+32%~+48%，p<0.01 全部）→ holiday = 可靠 **stay-home** 事件；
2. **峰段不稳健**：三世界方向 +/+/− → **假日主要抬高日间总量，峰会因该户峰段构成而不同**
   （W3 户含 AC，日间居家可能使晚峰错开）；故**峰段不作断言**；
3. **机制一致**：照明/电脑/烹饪上升（stay-home），与 lockdown（Xia 2026）同型；
4. **headline 升级完成**：总量效应 **cross-3-world ✅**，与 heatwave/lockdown/cold_snap/ac_tax 同级。

## 5. 论文更新

- `paper/README.md`：headline 行改为**跨 3 世界**（W1/W2/W3）；实验行同步。
- `paper/experiments/event_holiday.md`：§5/§7 补 W3，标注"**峰效应世界相关**"。

## 6. Validity

- same-era 配对、n=15、**跨 3 世界**；每世界单户、单日。
- 限制：多户未测；峰幅度不作断言（3 世界方向不一致）。

## 7. token

- 约 **120 次调用**（baseline×15 + holiday×15）。
