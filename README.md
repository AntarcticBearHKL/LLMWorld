# LLMWorld —— LLM 多智能体家庭用电模拟（Clayton 3168）

FIT5216 研究项目"LLM Society"的核心实现：用 LLM 生成式智能体模拟 Clayton 3168 家庭日常行为，
打通"行为 → 电器决策 → 分钟级负荷"管线，研究政策/新闻/环境信号对聚合用电的影响。

## 快速开始

```bash
# 1. 生成人口（0 LLM 调用，Big Five 人格 + 8 类家庭）
python Implement/population.py pop03 --count 12

# 2. 单家庭模拟（交互/命令行）
python Implement/simulate.py 495 --days 1 --date "2026年4月21日" --no-input

# 3. 人口级并行模拟（多户并行，聚合负荷）
python Implement/population_runner.py pop03 --days 1
python Implement/population_runner.py pop03 --policy tou          # 政策干预
python Implement/population_runner.py pop03 --scenario war_news  # 新闻剧本（worlds/pop03/events.json）
python Implement/population_runner.py pop03 --event "2026-04-21|标题|内容"  # 上帝注入

# 4. 后台运行 + 监控（模拟期间可继续开发）
python Implement/background_runner.py start pop03 --days 1
python Implement/background_runner.py status
python Implement/background_runner.py watch job_001

# 5. 可视化（浏览器）
python Implement/server.py            # → http://localhost:8080
python Implement/server.py --query profile --world pop03 --scenario baseline --date 2026-04-21

# 6. 分析
python Implement/validate_baseline.py --world pop03   # vs 维州真实负荷
python Implement/compare_policies.py --world pop03 --all   # 政策矩阵
python Implement/analyze_groups.py --world pop03     # 节能意识分组
python Implement/make_report.py --world pop03        # 论文素材报告

# 7. 测试
python Implement/test_offline.py
```

## 架构

```
Implement/
  engine/
    world.py               世界（时间/记忆/新闻台/每日五阶段管线）
    planner.py             第一~三层：宏观计划→渐进协调→丰富描述
    executor.py            第四层：用电决策（政策/新闻注入）
    energy_calculator.py   第五层：能耗计算（基载+1440分钟曲线+超限截断）
    subagent.py            DeepSeek 调用层（并发≤10/重试/Token统计）
    memory.py              跨天记忆（昨日摘要→今日计划）
    news.py                新闻台（上帝剧本 events.json/--event/POST API）
    policy.py              政策（tou/subsidy/nudge/nudge_loss）
    environment_interface.py 环境接口（real API/config 气候随机/manual 手工）
    generator.py           世界生成（LLM 版，地区→分布→家庭）
    weather_api.py         真实天气/节假日 API（含兜底）
    utils.py               公共工具（JSON/日志/时间/校验）
  population.py            人口构建 v2（Big Five + 8 类家庭 + census 校准，0 LLM）
  population_runner.py     人口级并行模拟 + 聚合 + 政策/场景支持
  simulate.py              单家庭模拟入口
  background_runner.py     后台任务管理器（start/status/watch/stop）
  server.py                可视化后端（常驻 HTTP + CLI 查询）
  frontend/index.html      浏览器前端（曲线叠加/矩阵/新闻/上帝控制台）
  config.py                全局配置中心
  test_offline.py          离线测试（58+ 项）
Design/                    架构设计文档（.aas）
prompts/                   LLM 提示词模板
worlds/<id>/               世界数据（household.json / events.json 剧本）
outputs/<id>/population/   聚合结果（按场景分目录）
StepInfo/                  开发日志（计划N/执行N）
```

## 关键设计决策

| 决策 | 理由 |
|---|---|
| 并发硬上限 10 | 用户要求；SubAgent 全局信号量 + 实测峰值监控 |
| thinking 默认关闭 | 基准测试：开=3分钟/条，关=2秒/条（90 倍），JSON 质量无差异 |
| 电器日使用上限 | 防止 LLM 不真实决策（EV 充 12 小时），超限截断+警告 |
| 常开电器基载计入 | 冰箱等 always_on 必须进日总用电（修复前系统性偏低）|
| 场景目录隔离 | 政策/新闻实验互相覆盖的历史教训 |
| Big Five 人格 | PsyAgent 等 12 篇 arXiv 文献支撑（见 StepInfo/计划22）|

## 环境配置（config.py / .env）

- `DEEPSEEK_APIKEY`（.env）：DeepSeek API
- `ENV_MODE = real/config/manual`：天气来源（真实 API / 墨尔本气候表随机 / env_manual.json 手工）
- `WEATHER_API_KEY`（.env）：可选，real 模式用

## 论文素材

`reports/paper_material_pop02.md` 自动汇总：基线对齐/政策矩阵/弹性/分组分析/图表清单。
运行 `python Implement/make_report.py --world pop02` 刷新。
