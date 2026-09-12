# R192 — wfh 跨世界复现 ✅：总 +28.7%（p=6.3e-5）→ 候选 headline

- **轮次**：Round 192
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 M1；baseline×15 + `wfh`×15；~120 calls）
- **结论**：✅ **跨世界复现**：总 **+28.7%（t=+5.62, p=6.3e-5）**、峰 **+27.4%（p=0.007）**；
  与 W1（+30.6%, p=0.006）一致 → **wfh = 第 2 个 stay-home headline（跨 2 世界）**。

---

## 1. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "wfh2_b_$i" --workers 1
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "wfh2_t_$i" --event-template "2026-09-11|wfh" --workers 1
}
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix wfh2_b --treat-prefix wfh2_t --n 15 --tag baseline
```

## 2. 结果（n=15，两世界对照）

| 指标 | W1 `838587` h002 | W2 `172148` h002 | 复现? |
|---|---|---|---|
| **总电量** | **+30.6%**（p=0.006） | **+28.7%**（t=5.62, p=6.3e-5） | ✅ **是** |
| 峰段 16–21 | +17.5%（p=0.044） | **+27.4%**（p=0.007） | ✅ 方向一致 |
| 谷期 22–7 | −9.0%（n.s.） | −15.8%（n.s.） | 方向一致 |
| 峰值功率 | −8.9%（n.s.） | +21.0%（p=0.039） | 不一致 |

## 3. 解读

1. **wfh 跨 2 世界显著升总量**（+28.7%/+30.6%）→ 与 holiday 同 **stay-home** 机制；
2. **峰 +17.5%/+27.4% 均显著**（比 holiday 更稳定地抬峰）→ wfh 更像"全天居家"（工作日结构最接近）；
3. **候选 headline**：待 **第 3 世界**（world_143345）达成跨 3 世界；
4. **机制族**：lockdown（强制）/ holiday（假日）/ **wfh（居家办公）** 同属"居家时间↑ → 日间用电↑"。

## 4. 论文更新
- `paper/experiments/event_wfh.md`（新建）；`README.md` 加 wfh 行（跨 2 世界，待第 3 世界）。

## 5. token
- 约 **120 次调用**。
