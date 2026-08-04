# LLMWorld 论文素材报告（world: __no_such_world）
生成时间：2026-08-05 01:19:35

## 1. 政策场景概览

（无 policy_matrix.json，先跑 compare_policies --all）

## 2. 基线对齐（RQ1/RQ3）

（无 baseline_report.json，先跑 validate_baseline）

## 3. 价格弹性粗算（TOU 峰段）

## 4. 节能意识分组（Costa & Kahn 2010 对照）

（无 groups.json，先跑 analyze_groups）

## 5. 成本与规模（RQ4）

- 单户单日 token ≈ 80k~90k（thinking=False 快速模式）
- thinking=True 慢约 90 倍（3 分钟 vs 2 秒/调用）→ 大规模模拟必须关闭
- 并发实测峰值 = 10 = 硬上限（多户并行不破限）
- 峰均比随 N：4 户 4.83 → 10 户 2.52（平滑效应）

## 6. 行为聚类（Michalakopoulos 2023 / Dent 2014）

（无 clusters_*.json，先跑 load_profile_cluster）

## 7. 行为变异性（Zhou 2016 / Jin 2021）

（无 variability_baseline.json，先跑 analyze_variability）

## 8. 行为模式迁移（Jin 2021 household-days）

（无 patterns_baseline.json，先跑 analyze_behavior_patterns）

## 9. 异常户检测（Banik 2023 / Glauner 2017）

（无 anomalies_baseline.json，先跑 analyze_anomalies）

## 10. 行为-负荷一致性（Xia 2026）

（无 behavior_load_*.json，先跑 analyze_behavior_load）

## 11. 事件响应（Fidone 2026）

（无 event_response_baseline.json，先跑 analyze_event_response）

## 12. 多世界对比（Eco3S 2026 稳健性）

（无 worlds_matrix.json，先跑 compare_worlds）

## 13. 已产出图表清单
