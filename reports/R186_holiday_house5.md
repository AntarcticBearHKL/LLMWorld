# R186 — 假日跨住户 #5（world_143345 h001，6 口）：**总 +19.3%（p=0.019）** → 7/7 住户

- **轮次**：Round 186
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_143345 **house_0001**（6 口）M1；baseline×15 + `holiday`×15；~120 calls）
- **结论**：✅ 总电量 **+19.3%（t=+2.66, p=0.019）**；峰 +19.7% n.s.、谷 −22.1%（p=0.069）
  → holiday **总量效应 7/7 住户显著**。

## 1. 方法

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_143345 --house house_0001 --member 0 --date 2026-09-11 --env "hol3h1_b_$i" --workers 1
  python run.py --mode simulate --world world_143345 --house house_0001 --member 0 --date 2026-09-11 --env "hol3h1_h_$i" --event-template "2026-09-11|holiday" --workers 1
}
python src/analyze/compare_cpp.py --world world_143345 --house house_0001 --date 2026-09-11 --base-prefix hol3h1_b --treat-prefix hol3h1_h --n 15 --tag baseline
```

## 2. 结果（n=15）

| 指标 | baseline | holiday | Δ | t | p |
|---|---|---|---|---|---|
| **总电量** | 9.617 | 11.477 | **+19.3%** | **+2.66** | **0.019** |
| 峰段 16–21 | 2.949 | 3.530 | +19.7% | +1.36 | 0.20（n.s.） |
| 谷期 22–7 | 1.907 | 1.485 | −22.1% | −1.97 | 0.069 |

## 3. holiday 总量效应汇总（7 住户 / 3 世界，全部显著）

| 住户 | 总 Δ | p |
|---|---|---|
| W1h002(1口) | +48.3% | 3.5e-4 |
| W1h001(4口) | +20.8% | 0.0063 |
| W2h002(2口) | +31.9% | 3.8e-7 |
| W2h001(5口) | +59.1% | 5.3e-7 |
| W3h002(2口) | +39.8% | 0.0014 |
| W3h003(3口,AC) | +64.5% | 2.0e-4 |
| **W3h001(6口)** | **+19.3%** | **0.019** |

## 4. 解读

- **7/7 住户显著正向**（+19.3%~+64.5%）→ holiday 为**最稳健**事件效应；
- 幅度与户规模无单调关系（1口 +48%、6口 +19%、5口 +59%）→ 住户特异；
- 峰效应仍不作断言（+7.8%~+232%）。

## 5. 论文更新

- `paper/README.md` / `experiments/event_holiday.md`：更新为"**7 住户（3 世界）**"。

## 6. token
- 约 **120 次调用**。
