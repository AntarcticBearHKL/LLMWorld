# LLMWorld — Paper Draft (论文初稿导航)

> 本目录是论文初稿。**只有产生"有效果"、且可与文献基准对照的结论**才按论文"实验部分"写法
> 沉淀到 `experiments/`；未定论/失败/纯基础设施内容只留在 `reports/`（见 goal.md §6 分流规范）。

## 核心结论（headline）

| 结论 | 证据（跨 3 世界） | 双侧 Fisher p |
|---|---|---|
| **热浪事件 → 空调启用** | baseline AC 0/9 vs heatwave 11/12 | **≈0.00003** |
| **封锁事件 → 外出归零** | baseline Out>0 13/13 vs lockdown 1/13 | **≈0.000003** |
| **封锁事件 → 日间负荷 +220.7%** | same-era 交错 **n=9**：0.649→2.081 kWh（t=3.34, p≈0.010） | 有效设计可判幅度 |
| **寒潮事件 → 采暖启用** | baseline 0/10 vs cold_snap 6/10 | **≈0.011** |
| **空调峰税 ac_tax → 关空调/削峰** | 热浪背景峰段 −22.5%/−24.6%/−20.6%（跨 3 世界，合并 p≈1e-7；AC-on 15/15→7/15） | **≈0.0022** |
| **公共假日 holiday → 总电量上升（stay-home）** | 跨 3 世界 **5 住户**：+20.8%~+59.1%（**5/5 显著**，p≤0.0063）；照明/TV/烹饪齐升；峰效应住户相关（−15%~+232%，不作断言） | **≤0.0063** |
| ~~停电预警/电价上涨 → 峰段削减~~ | **已撤回**：连续指标跨时段基线漂移伪影（R104） | — |

**方法学**：运行间噪声地板 std≈1.0 kWh（CV≈12%，R057）；单次/单臂不可信；功效分析表明文献尺度
幅度（~3%）不可行，仅大效应（≥10–20%）可判（R058）。平台适合**定性/方向、异质性、大效应二值**结论。
详见 `99_discussion.md` 与 `reports/R087_final_status_v9.md`。

## 章节结构

| 章节 | 文件 | 状态 |
|---|---|---|
| 引言 / 研究问题（RQ1–RQ4） | `00_intro.md` | 草稿 |
| 方法：五阶段管线 + 领域模型 + 调度 | `01_method.md` | 草稿 |
| 实验 | `experiments/*.md` | 见下表 |
| 对齐表（结果 vs 实证基准） | `02_alignment.md` | 草稿 |
| 讨论：与 RQ1–RQ4 / 实证对齐 | `99_discussion.md` | 草稿 |

## 实验清单

状态取值：待做 / 跑通 / 有效果 / 已入稿。

| 实验 | 对应 RQ | 文献基准 | 期望区间 | 状态 | 文件 |
|---|---|---|---|---|---|
| TOU 分时电价 | RQ2 | Faruqui & Sergici 2010 | 峰值 −3~6% | null(n=15:峰段−3.2%,总电量+5.4%,均n.s.) | `experiments/tou.md` |
| 尖峰电价 CPP | RQ2 | Faruqui & Sergici 2010 | 峰值 −13~20% | null(**峰两世界均 n.s.**: W1 −2.7%/W2 +13.0%); 总量效应**世界特异**(W1 −14.4% p=0.007 / W2 −4.3% n.s.); cpp_soft W1 总 −10.9% | — |
| 谷期补贴 subsidy | RQ2 | Alexeenko & Bitar 2023 | EV 峰移 30~60% | 占位(待跑,需EV) | `experiments/subsidy.md` |
| 需量电费 peak_demand | RQ2 | Escarrega et al. 2025 | 峰值 −10~20% | null(N=3交错:峰值+4.2%,峰段−3.2%; **n=15 same-era:峰−6.9% n.s.,总−1.2% n.s.**) | `experiments/peak_demand.md` |
| EV 延迟激励 ev_delay | RQ2 | Alexeenko & Bitar 2023 | 异质性可观测 | 占位(待跑,需EV) | `experiments/ev_delay.md` |
| 社会规范 nudge | RQ2 | Allcott 2011 / Ayres 2013 | 总电量 −1~3% | 方向不稳定(大样本3/7增耗;方差主导) | `experiments/nudge.md` |
| 损失框架 nudge_loss | RQ2 | Ghesla et al. 2019 | 比增益框架多 ~5% | 反例(总量+6%,方向相反) | `experiments/nudge_loss.md` |
| 夜间回温 night_setback | RQ2 | Cabezas-Riviere 2025 | 采暖 −5~10% | null(单例:未降采暖反升) | `experiments/night_setback.md` |
| 实时反馈 in_home_display | RQ2 | Monacchi 2015 / Faruqui 2010 | 3~10%（叠加 TOU 达 10~30%） | null(same-era交错:峰段−10.3% n.s.,总电量+4.2%); **TOU+IHD 组合亦 null**(峰−6.8% n.s.,谷+10.5% n.s.,无×3放大,R171) | `experiments/in_home_display.md` |
| 封锁事件 lockdown | RQ2 | Xia et al. 2026 | 日间用量上升 | 有效果(二值跨3世界:Out>0 13/13→1/13, Fisher 双侧 p≈0.000003) | `experiments/event_lockdown.md` |
| 公共假日 holiday | RQ2 | Xia et al. 2026 (disruption) | 日间用量上升 | **有效果(跨3世界)**: 总电量 +48.3%/+31.9%/+39.8%（p≤0.0014）；照明/TV/烹饪齐升；**峰效应世界相关（不作断言）** | `experiments/event_holiday.md` |
| 停电预警 blackout_risk | RQ2 | Xia et al. 2026 | 避开晚峰 | 撤回(连续削峰为基线漂移伪影,R104) | `experiments/event_blackout_risk.md` |
| 电价上涨 price_hike | RQ2 | Faruqui & Sergici 2010 | 削峰省电 | 撤回(基线漂移伪影,R104) | `experiments/event_price_hike.md` |
| 寒潮事件 cold_snap | RQ2 | Xia et al. 2026 | 采暖上升 | 有效果(二值:采暖 0/10 vs 6/10, 双侧 p≈0.011) | `experiments/event_cold_snap.md` |
| 热浪事件 heatwave | RQ2/RQ3 | Xia et al. 2026 | 峰值 +20~40% | 有效果(二值跨3世界:baseline AC 0/9 vs heatwave 11/12, Fisher 双侧 p≈0.00003) | `experiments/event_heatwave.md` |
| 空调峰税 ac_tax | RQ2 | Faruqui & Sergici 2010 | 峰段 −5~20% | 有效果(热浪背景:AC 15/15→7/15 p≈0.0022;峰段−22.5%,n=15) | `experiments/event_ac_tax.md` |
| 节能返利 rebate | RQ2 | Faruqui & Sergici 2010 | 峰段 −3~6% | partial(峰段null −6.0% n.s.;但AC −40.8%/总电量 −21.2%,n=15) | `experiments/event_rebate.md` |
| 靶向信息请求(无价格) | RQ2 | — | 峰段下降 | 世界特异剂量-反应(峰段: w172148 −25.5%显著; w143345 −10% n.s.; w838587 null; 同设备峰段负荷正比) | — |
| 供应紧张预警 energy_crisis | RQ2 | Xia et al. 2026 | 负荷下降 | null(信息型:AC/峰段/总电量皆n.s.,n=9) | — |
| 光伏补贴公告 solar_incentive | RQ2 | — | 负荷下降 | null(未来取向信息型:峰段−13.2% n.s.,总电量+2.3% n.s.,n=15) | — |
| 未来电价公告(自定义) | RQ2 | — | 前瞻行为 | **世界特异**(world_838587 +20.8%显著;world_172148 −1.6% n.s.,R146) | — |
| 社区公告 community_notice | RQ2 | — | 传播效应 | **世界特异**(world_838587 +11.0%显著;跨世界未复现) | — |
| 政策组合 tou+nudge | RQ2 | Pellerano 2017 | 叠加/挤出 | 非加性(实测−13.9% ≠ 加性−2.3%;n=6) | — |
| 事件×政策 heatwave×tou | RQ2 | — | 危机放大响应 | null(TOU效应未放大;n=6) | — |
| 政策时间线/习惯粘性 | RQ2 | — | 撤销后回弹 | 不可定论(n=3,日效应主导) | — |
| 炊具靶向(替代效应) | RQ2 | — | 削峰 | 替代效应(电磁炉−99.7%但烤箱/微波炉替代→总峰−0.2%,n=9) | — |
| 邻居比较 peer_nudge | RQ2 | Ayres 2013 | −1~3%，高耗家庭更强 | 初步(不一致：−6.6~+11.6%) | `experiments/peer_nudge.md` |
| 群体异质性 | RQ3 | Costa & Kahn 2010 | 环境派 2~4% / 保守派 ~0 | 名义方向但方差压倒(不可定论) | `experiments/group_heterogeneity.md` |
| 政策组合/多目标权衡 | RQ2/RQ3 | CoRenew 2026 | 峰削减 vs 负担 vs 公平 | 工具可用/TOU混杂(不可定论) | `experiments/policy_tradeoffs.md` |

## 每个实验文件模板

见 goal.md §7：`1 Research Question` / `2 Hypothesis & Expected Effect` / `3 Experimental Setup` /
`4 Metrics` / `5 Results`（仅填有效果）/ `6 Comparison with Literature` / `7 Validity Check` / `8 Conclusion`。

> 尚无有效结果时，文件可只保留第 1–4 节，第 5 节写"待验证"。

## 硬约束（每轮必守）

- 世界 ≤5 户，模拟 ≤3 天，单实验 ≤3 天出结果；
- 能 L0/L1 绝不上 L2，能 L2 绝不上 L3；
- 干预只以自然语言注入 prompt，禁止硬编码行为；
- 结果若显著超出"合理区间"，先查 prompt 是否写太强（偏置），再谈涌现。
