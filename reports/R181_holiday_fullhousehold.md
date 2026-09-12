# R181 — 假日**全户级**验证（2 成员）：总 +44.9%（p=0.022）——非 M1 伪影

- **轮次**：Round 181
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 **全 2 成员**；baseline×9 + `holiday`×9；~144 calls）
- **结论**：✅ **全户级成立**：总电量 **+44.9%（t=+2.84, p=0.022）**、峰 +24.1%（n.s.）→
  holiday 效应**不是 M1-only 伪影**（此前全部实验仅模拟成员 1）。

---

## 1. 目的（最大方法学缺口）

此前所有实验只模拟 **成员 1（M1）**，未验证"住户级"结论。本轮对 **world_172148 h002 的 2 个成员全部模拟**
（`--member` 省略），检验 holiday 效应在**全户聚合负荷**上是否成立。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..9) {
  python run.py --mode simulate --world world_172148 --house house_0002 --date 2026-09-11 --env "fh_b_$i" --workers 1         # 全成员 baseline
  python run.py --mode simulate --world world_172148 --house house_0002 --date 2026-09-11 --env "fh_h_$i" --event-template "2026-09-11|holiday" --workers 1  # 全成员 holiday
}
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix fh_b --treat-prefix fh_h --n 9 --tag baseline
```

## 3. 结果（n=9，全户聚合）

| 指标 | baseline | holiday | Δ | t | p |
|---|---|---|---|---|---|
| **总电量** | 11.727 | 16.991 | **+44.9%** | **+2.84** | **0.022** |
| 峰段 16–21 | 3.388 | 4.204 | +24.1% | +1.87 | 0.098（n.s.） |
| 谷期 22–7 | 3.214 | 2.869 | −10.7% | −0.24 | 0.82（n.s.） |
| 峰值功率 | 4830 | 4744 | −1.8% | −0.13 | 0.90（n.s.） |

## 4. 解读

1. **全户级 +44.9%（p=0.022）**：与 M1-only 的 **+31.9%（R167）** 同向、量级相近 →
   **holiday 效应在住户级成立**，非单成员伪影；
2. **首次住户级（多成员）验证**：回应了全部既往报告的 "single member (M1)" 限制；
3. 峰段 +24.1% n.s. → 与"峰效应住户相关、不作断言"一致；
4. 限制：n=9、单户（2 成员）；更大户（4–5 人）待测。

## 5. 论文更新

- `paper/experiments/event_holiday.md` §7：补"**全户级（2 成员）** 总 +44.9%（p=0.022）"。

## 6. token

- 约 **144 calls**（2 成员 × 9 对 × 2 臂）。
