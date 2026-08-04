# 计划 2 —— 配置化 + 非交互 CLI + 真实 API 全管线冒烟验证

> 依据：`StepInfo/00_需求与规则.md`（已重读：开发节奏"走一步看结果"，每步必须有验证环节；并发 ≤10；只用 DeepSeek API）。

## 为什么做这步

第 1 轮完成的是**离线逻辑**的可信化（测试全绿）。但五阶段管线是 LLM 驱动的，重构了 subagent/planner/executor 之后，**API 路径一次都还没真跑过**。在做任何上层建筑（跨天记忆、人口级模拟）之前，必须：
1. 用 DeepSeek 真实跑通一次完整管线（宏观计划 → 协调 → 丰富 → 决策 → 能耗），确认重构无回归
2. 同时把"实验运行"自动化：当前 simulate.py 依赖交互式 input()，无法批量实验 → 引入全局配置 + 命令行参数
3. 固定随机种子，让实验可复现（论文硬性要求）

## 做什么

| # | 任务 | 文件 | 验收 |
|---|---|---|---|
| 1 | 全局配置 `config.py`：模型、温度、并发上限（默认10）、模拟默认值（日期/天数/季节/天气/种子） | 新建 `Implement/config.py` | subagent/planner/simulate 引用配置，改一处全生效 |
| 2 | 随机种子统一管理：`utils.set_seed()`，generate.py / simulate.py 入口调用 | `utils.py` + `generate.py` + `simulate.py` | 同种子两次运行结果一致（离线部分） |
| 3 | simulate.py 非交互化：`--world --days --date --house --season --weather --temp --seed --no-input` | `Implement/simulate.py` | 无参数时保留原交互模式；有参数时全自动 |
| 4 | **真实 API 冒烟测试**：world 495 跑 1 天（Clayton 3168 联排，2 成员） | 运行验证 | 五阶段全部成功、token 账单打印、负荷曲线生成、无回归异常 |
| 5 | 把冒烟测试脚本固化为 `Implement/smoke_test.py`（可重复执行，参数化世界/天数） | 新建 | 一行命令复现 |

## 怎么做

- `config.py` 用 dataclass/简单类，读 .env 的 DEEPSEEK_APIKEY，其余常量集中定义，模块引用 `config.MODEL` 等
- seed：`utils.set_seed(seed)` 调用 `random.seed` + `numpy.random.seed`（如可用）
- simulate.py 用 argparse 扩展现有参数（保留旧交互路径），自动模式跳过所有 input()
- 冒烟测试跑完检查：4 个阶段日志文件齐全、`用电信息/总用电汇总.json` 含基载、`house_load_profile_1440min.json` 1440 点、token 统计打印
- API 失败重试已由 subagent 处理；若冒烟失败 → 记录失败原因，计划2不结算，先修

## 怎么验证

1. `python Implement/test_offline.py` 仍全绿（无回归）
2. `python Implement/simulate.py 495 --days 1 --date 2026年4月21日 --no-input` → 五阶段全通，token 账单正常
3. 产物检查：日志/汇总/负荷曲线齐全
4. git 提交

## 学术依据

- 可复现性（seed 固定、配置集中）是 AgentSociety (Piao et al. 2025) 等大规模智能体仿真论文的基础要求：不固定种子，实验结论不可信
- 自动化 CLI 对齐 SALM (Koley 2025) 的工程化主张：批量、低摩擦的模拟运行是规模化的前提

## 下一步候选

- 计划3：跨天记忆（昨日摘要 → 今日 prompt）——论文行为引擎核心卖点
- 计划3：人口级并行模拟 runner（RQ1）
- 计划3：真实电力数据基线对比（vic_electricity_data.csv，RQ3）
