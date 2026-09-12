# R197 — 交通罢工跨世界复现 ✅：总 +22.2%（p=4e-4）→ 候选 headline

- **轮次**：Round 197
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 M1；baseline×15 + `transport_strike`×15；~120 calls）
- **结论**：✅ **跨世界复现**：总 **+22.2%（t=+4.61, p=4.2e-4）**、峰 +17.6%（p=0.041）；
  与 W1（+33.9%, p=0.028）一致 → **stay-home 族第 4 类信号（跨 2 世界）**。

## 1. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "ts2_b_$i" --workers 1
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "ts2_t_$i" --event-template "2026-09-11|transport_strike" --workers 1
}
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix ts2_b --treat-prefix ts2_t --n 15 --tag baseline
```

## 2. 结果（n=15，两世界）

| 指标 | W1 `838587` h002 | W2 `172148` h002 | 复现? |
|---|---|---|---|
| **总电量** | **+33.9%**（p=0.028） | **+22.2%**（t=4.61, p=4.2e-4） | ✅ 是 |
| 峰段 16–21 | +5.4%（n.s.） | **+17.6%**（p=0.041） | 方向一致 |
| 谷期 22–7 | −10.0%（n.s.） | −30.6%（p=0.076） | 方向一致 |

## 3. 解读

1. **两世界总 +22.2%/+33.9%** → stay-home 机制族（lockdown/holiday/wfh/**transport_strike**）进一步一般化；
2. **候选 headline**：待第 3 世界（world_143345）；
3. **谷期一致下降**（−10%/~−31%）→ 早间/日间前移（与 holiday/wfh 同型）。

## 4. 论文更新
- `paper/experiments/event_transport_strike.md`（新建）；`README.md` 加行（跨 2 世界，待第 3 世界）。

## 5. token
- 约 **120 次调用**。
