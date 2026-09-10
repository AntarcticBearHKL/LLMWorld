# LLMWorld — Paper Draft (论文初稿导航)

> 本目录是论文初稿。**只有产生"有效果"、且可与文献基准对照的结论**才按论文"实验部分"写法
> 沉淀到 `experiments/`；未定论/失败/纯基础设施内容只留在 `reports/`（见 goal.md §6 分流规范）。

## 章节结构

| 章节 | 文件 | 状态 |
|---|---|---|
| 引言 / 研究问题（RQ1–RQ4） | `00_intro.md` | 草稿 |
| 方法：五阶段管线 + 领域模型 + 调度 | `01_method.md` | 草稿 |
| 实验 | `experiments/*.md` | 见下表 |
| 讨论：与 RQ1–RQ4 / 实证对齐 | `99_discussion.md` | 草稿 |

## 实验清单

状态取值：待做 / 跑通 / 有效果 / 已入稿。

| 实验 | 对应 RQ | 文献基准 | 期望区间 | 状态 | 文件 |
|---|---|---|---|---|---|
| TOU 分时电价 | RQ2 | Faruqui & Sergici 2010 | 峰值 −3~6% | 不可定论(方向随采样翻转) | `experiments/tou.md` |
| 谷期补贴 subsidy | RQ2 | Alexeenko & Bitar 2023 | EV 峰移 30~60% | 占位(待跑,需EV) | `experiments/subsidy.md` |
| 需量电费 peak_demand | RQ2 | Escarrega et al. 2025 | 峰值 −10~20% | 占位(待跑) | `experiments/peak_demand.md` |
| EV 延迟激励 ev_delay | RQ2 | Alexeenko & Bitar 2023 | 异质性可观测 | 占位(待跑,需EV) | `experiments/ev_delay.md` |
| 社会规范 nudge | RQ2 | Allcott 2011 / Ayres 2013 | 总电量 −1~3% | 方向不稳定(大样本3/7增耗;方差主导) | `experiments/nudge.md` |
| 损失框架 nudge_loss | RQ2 | Ghesla et al. 2019 | 比增益框架多 ~5% | 反例(总量+6%,方向相反) | `experiments/nudge_loss.md` |
| 夜间回温 night_setback | RQ2 | Cabezas-Riviere 2025 | 采暖 −5~10% | 占位(待跑) | `experiments/night_setback.md` |
| 实时反馈 in_home_display | RQ2 | Monacchi 2015 / Faruqui 2010 | 3~10%（叠加 TOU 达 10~30%） | 占位(待跑) | `experiments/in_home_display.md` |
| 寒潮事件 cold_snap | RQ2 | Xia et al. 2026 | 采暖上升 | 初步(采暖0→启用,+158%,n=1) | `experiments/event_cold_snap.md` |
| 热浪事件 heatwave | RQ2/RQ3 | Xia et al. 2026 | 峰值 +20~40% | 有效果(二值跨2世界:baseline AC 0/7 vs heatwave 9/10, Fisher p≈0.0004) | `experiments/event_heatwave.md` |
| 邻居比较 peer_nudge | RQ2 | Ayres 2013 | −1~3%，高耗家庭更强 | 初步(不一致：−6.6~+11.6%) | `experiments/peer_nudge.md` |
| 群体异质性 | RQ3 | Costa & Kahn 2010 | 环境派 2~4% / 保守派 ~0 | 名义方向但方差压倒(不可定论) | `experiments/group_heterogeneity.md` |
| 政策组合/多目标权衡 | RQ2/RQ3 | CoRenew 2026 | 峰削减 vs 负担 vs 公平 | 占位(待跑) | `experiments/policy_tradeoffs.md` |

## 每个实验文件模板

见 goal.md §7：`1 Research Question` / `2 Hypothesis & Expected Effect` / `3 Experimental Setup` /
`4 Metrics` / `5 Results`（仅填有效果）/ `6 Comparison with Literature` / `7 Validity Check` / `8 Conclusion`。

> 尚无有效结果时，文件可只保留第 1–4 节，第 5 节写"待验证"。

## 硬约束（每轮必守）

- 世界 ≤5 户，模拟 ≤3 天，单实验 ≤3 天出结果；
- 能 L0/L1 绝不上 L2，能 L2 绝不上 L3；
- 干预只以自然语言注入 prompt，禁止硬编码行为；
- 结果若显著超出"合理区间"，先查 prompt 是否写太强（偏置），再谈涌现。
