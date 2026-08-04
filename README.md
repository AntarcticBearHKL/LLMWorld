# LLMWorld —— LLM 多智能体家庭用电模拟（Clayton 3168）

FIT5216 研究项目"LLM Society"的核心实现：用 LLM 生成式智能体模拟 Clayton 3168 家庭日常行为，
打通"行为 → 电器决策 → 分钟级负荷"管线，研究政策/新闻/环境信号对聚合用电的影响。

## 快速开始

```bash
# 1. 生成人口（0 LLM 调用，Big Five 人格 + 8 类家庭；LLM 混合版见 population_llm.py）
python Implement/population.py pop03 --count 3

# 2. 单家庭模拟（交互/命令行；--date 缺省=自动续跑）
python Implement/simulate.py 495 --days 1 --date "2026年4月21日" --no-input

# 3. 人口级并行模拟（多户并行，聚合负荷；系统级后台可用 background_runner）
python Implement/population_runner.py pop03 --days 1
python Implement/population_runner.py pop03 --policy tou          # tou/subsidy/nudge/nudge_loss/peak_demand/ev_delay/night_setback
python Implement/population_runner.py pop03 --policy "tou,nudge"  # 政策组合（Faruqui & Sergici 2010）
python Implement/population_runner.py pop03 --peer-nudge --days 3 # 个性化邻居反馈（Ayres 2013）
python Implement/population_runner.py pop03 --policy-schedule "2026-04-25,2026-04-28,tou"  # 政策时间表
python Implement/population_runner.py pop03 --event-template "2026-01-15|heatwave"        # 新闻模板
python Implement/population_runner.py pop03 --event "2026-04-21|标题|内容"  # 上帝注入

# 4. 后台运行 + 监控（系统级进程，模拟期间可继续开发）
python Implement/background_runner.py start pop03 --days 1
python Implement/background_runner.py status
python Implement/background_runner.py watch job_001
python Implement/background_runner.py stop job_001

# 5. 可视化服务器（系统级常驻；前后端修改后重启）→ http://localhost:8080
python Implement/background_runner.py server start
python Implement/background_runner.py server restart
python Implement/background_runner.py server stop
python Implement/server.py --query profile --world pop03 --scenario baseline --date 2026-04-21

# 6. 分析（一键化：聚类/变异性/模式/归因/分组/矩阵，0 token；也可在浏览器"一键分析"按钮）
python Implement/make_analysis_all.py --world pop03
python Implement/validate_baseline.py --world pop03        # vs 维州真实负荷
python Implement/compare_policies.py --world pop03 --all   # 政策矩阵（含峰值形态列）
python Implement/analyze_anomalies.py pop03                # 异常户检测（z-score）
python Implement/analyze_event_response.py pop03           # 新闻事件 × 模式迁移
python Implement/compare_worlds.py --worlds pop03 pop04    # 多世界政策对比
python Implement/make_report.py --world pop03              # 论文素材报告

# 7. 测试
python Implement/test_offline.py                            # 148 项
```

## 世界日期时间线约束（用户指令）

- 世界**未开始**（无 state.json）→ 可随意设定开始日期
- 世界**已开始** → 只能继续模拟：`--date` 留空=自动从上次日期+1 天续跑；
  指定日期必须恰好等于下一天，禁止覆盖/回退/跳日
- 想重新开始同一时间线 → **新建世界 ID**

## 架构

```
Implement/
  engine/
    world.py               世界（时间/记忆/新闻台/每日五阶段管线/state落盘恢复/日期时间线校验）
    planner.py             第一~三层：宏观计划→渐进协调→丰富描述
    executor.py            第四层：用电决策（政策/新闻注入，决策校验）
    energy_calculator.py   第五层：能耗计算（基载+1440分钟曲线+超限截断+峰值叠加事件）
    subagent.py            DeepSeek 调用层（并发不限/重试3次/超时600s/effort=low）
    memory.py              跨天记忆（昨日摘要→今日计划 + 新闻记忆）
    news.py                新闻台（events.json/投递进度/状态序列化）
    news_templates.py      新闻模板库（10 类预置事件）
    policy.py              政策（tou/subsidy/nudge/nudge_loss/peak_demand/ev_delay/组合）
    environment_interface.py 环境三模式（real API/config 气候随机/manual 手工）
    generator.py           世界生成（LLM 版，地区→分布→家庭）
    weather_api.py         真实天气/节假日 API（含兜底）
    utils.py               公共工具（JSON/日志/时间/校验/季节）
    load_features.py       负荷特征族（24h形状/负荷率/kmeans(sklearn)/肘部/跨日变异性/峰值叠加）
  population.py            人口构建 v2（Big Five + 8 类家庭 + census 校准，0 LLM）
  population_llm.py        人口 LLM 混合生成（骨架+细节，校验回退）
  population_runner.py     人口级并行模拟 + 聚合 + 政策/场景/事件/peer-nudge/时间线校验
  simulate.py              单家庭模拟入口（时间线校验）
  background_runner.py     后台任务管理器（start/status/watch/stop + server 子命令）
  server.py                可视化后端（常驻 HTTP + CLI 查询；模拟/分析/停止/删除端点）
  frontend/index.html      浏览器前端（曲线/矩阵/聚类/变异性/模式/分组/异常/事件/时间线/
                           多世界对比/开启模拟闭环/一键分析/上帝面板/新闻模板）
  config.py                全局配置中心
  load_profile_cluster.py  负荷曲线聚类（计划40，Michalakopoulos 2023）
  analyze_variability.py   跨日行为变异性（计划41，Zhou 2016）
  analyze_behavior_patterns.py 行为模式迁移（计划42，Jin 2021）
  analyze_groups.py        分组政策响应（计划45，--label-source awareness|variability）
  make_analysis_all.py     分析一键化（计划46）
  analyze_event_response.py 事件响应（计划55，Fidone 2026）
  analyze_anomalies.py     异常户检测（计划62，z-score）
  compare_worlds.py        多世界政策对比（计划51）
  compare_policies.py      政策对比（--base-date 同日公平对比；峰值形态）
  test_offline.py          离线测试（148 项）
  Design/                  架构设计文档（.aas）
  prompts/                 LLM 提示词模板
  worlds/<id>/             世界数据（household.json / events.json / state.json 存档）
  outputs/<id>/population/ 聚合结果（按场景/日期分目录）
  outputs/<id>/analysis/   分析产物（聚类/变异性/模式/分组/异常/事件响应）
  StepInfo/                开发日志（计划N/执行N，00_需求与规则=最高优先级存档）
```

## 前端能力（http://localhost:8080）

- **开启模拟**：选世界→政策下拉（6 政策+组合+peer_nudge）→天数/日期→确认启动
  （系统级后台执行，自动跟踪进度，完成后自动刷新全部结果）
- **一键分析**：0 token 跑完聚类/变异性/模式/归因/分组/矩阵
- **面板**：负荷曲线/矩阵/聚类/变异性/模式迁移/分组响应/异常户/
  事件响应/世界时间线/多世界对比/任务（停止/删除）
- **上帝面板**：事件注入 + 新闻模板一键填入

## 关键设计决策

| 决策 | 理由 |
|---|---|
| API 并发不设上限 | 用户 2026-08 指令：解除限制；户级并行多少只取决于世界家庭数 |
| 每世界最多 10 户 | 用户 2026-08 指令：world 级约束（population.py 校验）；更大人口用 combine_worlds 联合 |
| 世界日期连续+时间线约束 | state.json 断点续跑：--date 缺省自动续跑；已开始世界禁止覆盖/回退/跳日（用户指令） |
| 生成去作弊化 | 生成时无 EV/节能意识/省电预设，用电行为由 LLM 自发涌现 |
| 服务器系统级常驻 | background_runner server start/restart；前后端修改即重启 |
| thinking 默认关闭 | 基准测试：开=3分钟/条，关=2秒/条（90 倍）；开启时 effort=low（官方最低档）|
| 电器日使用上限 | 防止 LLM 不真实决策（EV 充 12 小时），超限截断+警告 |
| 常开电器基载计入 | 冰箱等 always_on 必须进日总用电（修复前系统性偏低）|
| 场景目录隔离 | 政策/新闻实验互相覆盖的历史教训 |
| 聚类等算法用库实现 | 用户指令 §一.22：sklearn KMeans 等成熟算法不手写 |
| Big Five 人格 | PsyAgent 等 12 篇 arXiv 文献支撑（见 StepInfo/计划22）|

## 环境配置（config.py / .env）

- `DEEPSEEK_APIKEY`（.env）：DeepSeek API
- `ENV_MODE = real/config/manual`：天气来源（真实 API / 墨尔本气候表随机 / env_manual.json 手工）
- `WEATHER_API_KEY`（.env）：可选，real 模式用
- Python 依赖：`numpy` / `scipy` / `scikit-learn`（聚类分析）/ `matplotlib`（基线图，可选）

## 论文素材

`reports/paper_material_pop02.md` 自动汇总：基线对齐/政策矩阵/弹性/分组分析/图表清单。
运行 `python Implement/make_report.py --world pop02` 刷新。
