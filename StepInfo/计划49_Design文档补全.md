# 计划49:Design 架构文档补全(计划40-48 新模块)

## 做什么

为计划40-48 新增的全部模块补 Design/.aas 架构文档,并同步
00_需求与规则 §三 系统能力清单与 README 架构段。
计划40-48 的 9 个新模块(load_features / load_profile_cluster /
analyze_variability / analyze_behavior_patterns / make_analysis_all /
分组扩展 / 峰值叠加 / 组合政策 / 峰值形态指标)目前只有代码与
StepInfo,缺架构存档——任何无上下文的 agent 无法从 Design/ 了解它们。

## 为什么(依据)

1. **§一.7 记录要求 + §七.5 明确候选项**:Design 文档补全
   (population_llm/news_templates/政策时间表)在 00_需求与规则
   第七节已列出;本轮代码库 40-48 新增模块同样需补齐
   (运维经验/存档维护来源,§一.21 允许)。
2. **§一.2 代码可读性**:可读性靠命名与结构,但模块间关系
   需要 Design 存档承载(零注释标准下文档性内容放 Design/,§一.18)。
3. **读档连续性**(00 文件开头):"任何没有上下文的 agent,读
   StepInfo + README 即可接续"——Design 是架构层存档,必须同步。

## 怎么做

1. 新增 Design/engine/:
   - `LoadFeatures.aas`:engine/load_features.py
     (hourly_means/normalize_shape/load_factor/peak_hour/valley_hour/
     peak_to_mean/kmeans(sklearn)/elbow_scores/auto_k/hourly_cv_curve/
     variability_index/peak_hour_shift/daily_kwh_cv/peak_overlap_*)
   - `LoadProfileCluster.aas`:load_profile_cluster.py
     (扫描→形状特征→kmeans→clusters_*.json,肘部/退化降级)
   - `AnalyzeVariability.aas`:analyze_variability.py
     (多日扫描→变异指数/峰时漂移/日kWh CV→variability_*.json)
   - `AnalyzeBehaviorPatterns.aas`:analyze_behavior_patterns.py
     (household-days 聚类→簇序列/迁移次数→patterns_*.json)
   - `MakeAnalysisAll.aas`:make_analysis_all.py
     (一键化编排:聚类/变异性/模式/归因/分组/矩阵)
2. 更新:
   - `AnalyzeTools.aas`:加入新分析工具清单
   - `Policy.aas`:peak_demand/ev_delay/combine(组合)
   - `EnergyCalculator.aas`:peak_overlap_events 字段
   - `Frontend.aas`:新增面板(聚类/变异性/模式/分组/叠加)
   - `Server.aas`:新端点(clusters/variability/patterns/groups)
3. 00_需求与规则 §三 能力清单加入新模块;README 架构段更新
4. 测试:无代码变更,122 项保持全绿(验证一遍)

## 怎么验证

- `python Implement/test_offline.py` 122 项全绿(未动代码)
- git status 确认仅文档变更
