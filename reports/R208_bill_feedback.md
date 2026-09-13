# R208 — P4 账单反馈（`{bill_feedback}`）：实现完成，**day-2 峰未降（不可定论）**

- **轮次**：Round 208（P4）
- **日期**：2026-09-12
- **验证层级**：**L1**（288 单测全绿，+3）+ **L2 真调**（多日 `--days 2`；n=9/臂；~144 calls）
- **结论**：⚪ **实现完成、效果不可定论**：注入"昨日账单/峰段费用"后，**day-2 峰段 +16.3%（n.s.）**、
  总电量 +15.3%（t=2.58, p=0.032）→ **未降峰**（多日两臂不共享 day-2 时间线 → 计划层方差大）。

## 1. 目的（P4）

多日**账单反馈**（习惯/学习）：把**昨日实际电费/峰段费用**注入次日 prompt，检验是否持续降峰。

## 2. 改动
- `src/engine/tariff.py`：`rate_for_minute` / `cost_from_profile` / `render_bill_feedback`；
- `run.py`：`--bill-feedback`（多日，`--cost-context` 下）；`_bill_feedback_text`（读前一日 s4 → 载荷 → 费用）；
- s4 prompt 增 `{bill_feedback}`；**+3 测试（288 绿）**。
- **注入验证**：`[Bill] 2026-09-12: Yesterday your household electricity cost about 4.17 AUD, of which 2.79 AUD was during the peak window.`

## 3. 方法（可复现）

```powershell
# 两臂均 2 天 TOU+cost；B 额外开账单反馈
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env "fb2_a_$i" --policy "tou:0.9,0.18" --cost-context --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env "fb2_b_$i" --policy "tou:0.9,0.18" --cost-context --bill-feedback --workers 1
# 仅比较 day-2（2026-09-12）
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-12 --base-prefix fb2_a --treat-prefix fb2_b --n 9 --tag tou --base-tag tou
```

## 4. 结果（day-2，n=9）

| 指标 | 无反馈 | 有反馈 | Δ | t | p |
|---|---|---|---|---|---|
| 峰段 16–21 | 3.208 | 3.731 | +16.3% | +0.91 | 0.39（n.s.） |
| 谷期 22–7 | 1.044 | 1.170 | +12.1% | +0.54 | 0.60（n.s.） |
| 总电量 | 10.633 | 12.264 | **+15.3%** | +2.58 | 0.032 |

## 5. 解读（含限制）

1. **未降峰**：账单反馈**未**产生预期的持续降峰（峰 +16.3% n.s.）；
2. **总电量反升（+15.3%）**：疑为**多日两臂的 day-2 计划层方差**（各自独立 s1–s3 重采样）叠加
   潜在"反馈→反应性"，**n=9 不可定论**；
3. **方法学限制**：与单日实验不同，多日两臂**无法共享 day-2 时间线** → 计划噪声大；
   需 (a) 更多样本 或 (b) **共享 day-1 计划**（当前框架未支持跨臂共享多日计划）；
4. **对比**：单日 cost-context 有效（R200–R206，共享时间线）；**多日反馈未过** →
   "习惯/学习"通道在当前平台**未获支持**（与 R140 N3 时间线不可定论一致）。

## 6. 论文更新
- `paper/99_discussion.md`：补"多日账单反馈（R208）→ 未降峰/不可定论（计划方差）"。

## 7. token
- 约 **144 次调用**（2 天 × 2 臂 × 9 × ~4）。
