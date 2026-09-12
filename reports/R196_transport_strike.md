# R196 — 交通罢工（transport_strike）事件：**总电量 +33.9%（p=0.028）**

- **轮次**：Round 196
- **日期**：2026-09-12
- **验证层级**：**L1**（278 绿）+ **L2 真调**（world_838587 h002 M1；baseline×15 + `transport_strike`×15；~120 calls）
- **结论**：✅ 总电量 **+33.9%（t=+2.45, p=0.028）**、峰 +5.4% n.s. → 又一 **stay-home** 事件效应（候选 headline）。

---

## 1. 背景

stay-home 机制族（lockdown/holiday/wfh）已确立。**交通罢工**使通勤者无法出行 → 被动居家，
是**非强制、非日历、非办公安排**的第 4 类 stay-home 信号。

## 2. 改动
- `src/engine/news.py`：新增 `transport_strike` → **13 模板**；`tests/test_news.py` 更新为 13。**278 绿**。

## 3. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "ts_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "ts_t_$i" --event-template "2026-09-11|transport_strike" --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix ts_b --treat-prefix ts_t --n 15 --tag baseline
```

## 4. 结果（n=15）

| 指标 | baseline | transport_strike | Δ | t | p |
|---|---|---|---|---|---|
| **总电量** | 8.780 | 11.756 | **+33.9%** | **+2.45** | **0.028** |
| 峰段 16–21 | 3.775 | 3.981 | +5.4% | +0.61 | 0.55（n.s.） |
| 谷期 22–7 | 2.116 | 1.904 | −10.0% | −0.37 | 0.72（n.s.） |
| 峰值功率 | 3694 | 4146 | +12.3% | +1.14 | 0.27（n.s.） |

## 5. 解读

1. **+33.9% 与 wfh（+30.6%）/ holiday（+48.3%）同量级** → stay-home 机制族第 4 类信号再现；
2. **峰 +5.4% n.s.**（"峰住户相关"一贯）；
3. **机制统一**：**任何使居民日间在家的结构性冲击 → 总用电 +~30%**（lockdown/holiday/transport_strike/wfh）；
4. **候选 headline**：待跨世界。

## 6. token
- 约 **120 次调用**。
