# R193 — wfh 第 3 世界 ✅：总 +30.6% → **第 6 个 headline（跨 3 世界）**

- **轮次**：Round 193
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_143345 h002 M1；baseline×15 + `wfh`×15；~120 calls）
- **结论**：✅ **跨 3 世界达成**：总电量 **+30.6%（t=+2.81, p=0.014）**；
  三世界 **+30.6% / +28.7% / +30.6%（高度一致）** → **wfh 升为 headline**。

---

## 1. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_143345 --house house_0002 --member 0 --date 2026-09-11 --env "wfh3_b_$i" --workers 1
  python run.py --mode simulate --world world_143345 --house house_0002 --member 0 --date 2026-09-11 --env "wfh3_t_$i" --event-template "2026-09-11|wfh" --workers 1
}
python src/analyze/compare_cpp.py --world world_143345 --house house_0002 --date 2026-09-11 --base-prefix wfh3_b --treat-prefix wfh3_t --n 15 --tag baseline
```

## 2. 结果（n=15，三世界）

| 世界 | 总电量 Δ | p | 峰段 Δ |
|---|---|---|---|
| W1 `838587` h002 | **+30.6%** | 0.006 | +17.5%（p=0.044） |
| W2 `172148` h002 | **+28.7%** | 6.3e-5 | +27.4%（p=0.007） |
| **W3 `143345` h002** | **+30.6%** | **0.014** | +8.1%（n.s.） |

- 三世界总量 **+28.7%~+30.6%**，**高度一致**（远优于 holiday 的 +19~+65% 波动）。

## 3. 解读

1. **wfh 总量效应跨 3 世界稳健且高度一致**（+29~31%）→ 比 holiday 更"标准"的 stay-home 效应（工作日居家=全天在家）；
2. **峰段**：W1/W2 显著、W3 n.s.（+8.1%）→ 与"峰住户相关"一致，**总量为主结论**；
3. **headline 第 6 个**：`wfh → 总电量 +29~31%`（跨 3 世界）；
4. **机制族统一**：lockdown（强制居家）/ holiday（假日）/ **wfh（居家办公）** → 同一 stay-home 增加日间用电。

## 4. 论文更新
- `paper/README.md` headline 表：wfh 行改为**跨 3 世界**；
- `paper/experiments/event_wfh.md` §5/§7：补 W3，升级为 cross-world headline。

## 5. token
- 约 **120 次调用**。
