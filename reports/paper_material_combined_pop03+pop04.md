# LLMWorld 论文素材报告（world: combined_pop03+pop04）
生成时间：2026-08-04 21:43:08

## 1. 政策场景概览

（无 policy_matrix.json，先跑 compare_policies --all）

## 2. 基线对齐（RQ1/RQ3）

- 模拟晚峰：18:00，真实晚峰：18:00（偏移 0 小时）
- 峰均比：模拟 3.166 vs 真实 1.204
- 逐小时相关性：0.7079
- 数据源：C:\Users\antar\Desktop\研究项目\LLMWorld\outputs\combined_pop03+pop04\baseline\baseline_report.json

## 3. 价格弹性粗算（TOU 峰段）

## 4. 节能意识分组（Costa & Kahn 2010 对照）

（无 groups.json，先跑 analyze_groups）

## 5. 成本与规模（RQ4）

- 单户单日 token ≈ 80k~90k（thinking=False 快速模式）
- thinking=True 慢约 90 倍（3 分钟 vs 2 秒/调用）→ 大规模模拟必须关闭
- 并发实测峰值 = 10 = 硬上限（多户并行不破限）
- 峰均比随 N：4 户 4.83 → 10 户 2.52（平滑效应）

## 6. 已产出图表清单

- `outputs\combined_pop03+pop04\baseline\baseline_shape.png`