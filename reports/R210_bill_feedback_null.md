# R210 — P4 账单反馈（共享 day-2 时间线）：**clean null**（峰 −0.7% n.s.）

- **轮次**：Round 210（P4 重做，消除计划方差）
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002；2 天；**两臂共享 day-2 的 s1–s3**；n=9；~50 calls）
- **结论**：⚪ **null**：注入"昨日账单/峰段费用"后，**day-2 峰 −0.7%（t=−1.00, n.s.）**、总 −0.2%（n.s.）、
  谷 +0.0% → 账单反馈**不改变次日行为**（消除计划方差后为干净 null）。

## 1. 目的

R208 的多日对比因**两臂 day-2 计划不同**（计划方差）而不可定论。本轮**共享 day-2 的 s1–s3**，
只保留 s4 差异 → 干净检验反馈效应。

## 2. 方法（可复现）

```powershell
# 种子：2 天完整 baseline（得到 day1/day2 的 s1–s3）
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env bf_seed --workers 1
# 复制 day1+day2 的 s1–s3 到各臂；两臂共享 day-2 时间线
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env "bfa_$i" --policy "tou:0.9,0.18" --cost-context --s4-only --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env "bfb_$i" --policy "tou:0.9,0.18" --cost-context --bill-feedback --s4-only --workers 1
# 只比较 day-2
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-12 --base-prefix bfa --treat-prefix bfb --n 9 --tag tou --base-tag tou
```

## 3. 结果（day-2，n=9）

| 指标 | 无反馈 | 有反馈 | Δ | t | p |
|---|---|---|---|---|---|
| 峰段 16–21 | 5.732 | 5.695 | −0.7% | −1.00 | 0.35（n.s.） |
| 谷期 22–7 | 0.972 | 0.972 | +0.0% | 0.00 | 1.00 |
| 总电量 | 13.825 | 13.793 | −0.2% | −0.18 | 0.86（n.s.） |
| Dishwasher | 0.048 | 0.048 | +0.0% | n/a | — |

## 4. 解读
1. **反馈无效应**（峰 −0.7% n.s.，效应≈0）：即使消除计划方差，"昨日账单"**也不改变次日 s4 决策**；
2. **对比 R208**：R208（计划方差）不可定论 → 本轮（共享时间线）**干净 null**；
3. **机制**：当前 agent 无**跨日记忆/学习**——单日 cost-context 有效，但**不累积/不适应**；
4. **与文献**：Wang 2021"习惯主导"在本平台**未获支持**（无习惯通道）；与 R140（时间线不可定论）一致。

## 5. 论文更新
- `paper/99_discussion.md`：R208 条目更新为"**共享时间线后为 clean null（R210）**"。

## 6. token
- 约 **50 次调用**（种子 8 + 两臂 2 天 × 9 × ~2）。
