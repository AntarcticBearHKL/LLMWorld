# R191 — 居家办公（wfh）事件：**总电量 +30.6%（p=0.006）**（第 2 个 stay-home 事件）

- **轮次**：Round 191
- **日期**：2026-09-12
- **验证层级**：**L1**（278 单测全绿）+ **L2 真调**（world_838587 h002 M1；baseline×15 + `wfh`×15；~120 calls）
- **结论**：✅ **新事件效应**：wfh 使总电量 **+30.6%（t=+3.25, p=0.006）**、峰 +17.5%（p=0.044）
  → 与 holiday 同 **stay-home** 机制；候选 **headline**（待跨世界）。

---

## 1. 背景

holiday（stay-home）跨 7 住户成立。**居家办公（wfh）** 是另一**结构性 stay-home** 事件——若同样有效，
则 **stay-home 机制具一般性**（工作/上学日 → 在家 → 日间用电↑）。

## 2. 改动

- `src/engine/news.py`：新增 `wfh`（"Today is a work-from-home day; many residents are working from home
  instead of commuting to the office."）→ **12 模板**；`tests/test_news.py` 更新为 12 并含 `wfh`。**278 绿**。

## 3. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "wfh_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "wfh_t_$i" --event-template "2026-09-11|wfh" --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix wfh_b --treat-prefix wfh_t --n 15 --tag baseline
```

## 4. 结果（n=15）

| 指标 | baseline | wfh | Δ | t | p |
|---|---|---|---|---|---|
| **总电量** | 8.437 | 11.020 | **+30.6%** | **+3.25** | **0.006** |
| **峰段 16–21** | 3.458 | 4.063 | **+17.5%** | **+2.21** | **0.044** |
| 谷期 22–7 | 2.030 | 1.847 | −9.0% | −0.55 | 0.59（n.s.） |
| 峰值功率 | 3987 | 3633 | −8.9% | −1.23 | 0.24（n.s.） |

## 5. 解读

1. **wfh 显著升总量（+30.6%）**，方向与 holiday（同户 +48.3%）一致 → **stay-home 机制一般化**
   （强制居家 lockdown / 假日 holiday / 居家办公 wfh 同族）；
2. **峰 +17.5% 显著**（与 holiday 在该户 +7.8% n.s. 略不同）→ 峰仍属"住户相关"范畴；
3. **候选 headline**：需 **跨世界**复现（红线 3）后方可入 headline；本户（W1h002）基线日间占比低（8.9%，R190）→ 通勤型，stay-home 增幅大。

## 6. 论文更新

- `paper/README.md` / `experiments/`：wfh 行（待跨世界）。

## 7. token
- 约 **120 次调用**。
