# 计划54:个性化 nudge(邻居真实用电反馈,peer comparison)

## 做什么

population_runner 新增 `--peer-nudge` 模式:**多日模拟中,
第 2 天起每个家庭收到基于"邻居(同世界其他家庭)前一天实际用电"
的个性化社会规范文本**(如"你的邻居平均每天用电 16.2 千瓦时")。
实现同伴效应的轻量信息耦合:家庭间通过真实反馈相互影响,
而非固定文本("18 千瓦时")。

## 为什么(论文依据 + 思考过程)

搜索过程:arXiv search UI 搜 "personalized feedback energy
conservation smart meter households"(0 结果)→ 采用权威
非 arXiv 田野实验文献:

1. **Ayres, Raseman & Shih (2013)**, Journal of Economic Behavior
   & Organization 92:196-206《Evidence from two large field
   experiments that peer comparison feedback can reduce residential
   energy usage》:两大田野实验,邻居比较反馈(带笑脸/苦脸符号)
   削减用电 1.2-3.3%。
   → 思考:本项目 nudge 是固定对比文本(所有家庭同一"18 千瓦时")。
   论文核心是**邻居反馈必须真实且差异化**才有效。
   个性化邻居均值=该机制的模拟落地,也是计划41变异性×
   政策响应研究的理想干预(高变异性家庭对真实对比更敏感)。
2. **Allcott (2011)**, Journal of Public Economics:
   社会规范信(邻居比较)削减用电约 2% → 佐证机制。
3. **Fidone et al. (2025), arXiv:2511.07204**:LLM-ABM 中
   社会传染涌现的前提是智能体间信息耦合 → peer-nudge 是
   本模拟管线的第一条家庭间信息通道。

## 怎么做

1. `population_runner.py`:
   - `--peer-nudge` 标志(与 --policy 互斥;scenario 名 peer_nudge)
   - 第 1 天:基线(无政策)
   - 第 ≥2 天:读取**前一天** house_results 的 per-house kWh,
     `neighbor_mean_kwh(prev_kwhs, house_id)`(排除自身取均值,
     纯函数可测),构建 Policy.nudge(comparison_text=个性化文本)
   - day_policy 记录 "peer_nudge"
2. 测试:TestPeerNudge——neighbor_mean_kwh 排除自身/空邻居回退;
   多日 nudge 文本构建
3. 前端:政策实验启动器下拉加 "peer_nudge"(可选)

## 怎么验证

- `python Implement/test_offline.py` 全绿
- neighbor_mean_kwh 纯函数断言
