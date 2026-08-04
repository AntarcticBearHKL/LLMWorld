# 执行 2 —— 配置化 + 非交互 CLI + 真实 API 冒烟验证

> 对应 `计划2_配置化与API冒烟.md`。

## 实际做了什么

### 1. 新建 `Implement/config.py`（全局配置中心）
- LLM：模型 `deepseek-v4-flash`、温度 1.0、max_tokens 64000
- 并发/重试：MAX_WORKERS=10（硬性上限）、重试 3 次
- 模拟默认值：日期/天数/季节/天气/温度/种子(42)
- **新增 THINKING / REASONING_EFFORT 开关**（本轮最大收获，见下）

### 2. 随机种子管理
- `utils.set_seed()`：固定 random + numpy 种子
- generate.py / simulate.py / smoke_test.py 入口统一调用，`--seed` 参数

### 3. simulate.py 非交互化
- argparse 全参数化：`--days --date --house --season --weather --temp --seed --no-input`
- 无参数时保留原交互模式（向后兼容）

### 4. 新建 `Implement/smoke_test.py`
- 一行命令跑通五阶段 + 校验产物（日志齐全/基载>0/1440点）+ Token 账单

### 5. 真实 API 全管线验证（world 495，Clayton 联排，Alice+Bob）

## 关键结果

### 冒烟测试（首轮 thinking=True）暴露重大性能问题
- 每条 thinking=True 调用耗时 **3~5 分钟**（宏观计划 4 分钟、协调 5 分钟、丰富描述 3 分钟）
- 15 分钟超时被强制终止时，第四层还没跑完 → **单家庭单日 >15 分钟**，人口级模拟完全不可行

### 基准测试（同一 prompt，两个配置）
| 配置 | 耗时 | JSON 可解析 | 输出长度 |
|---|---|---|---|
| A: thinking=True (effort=high) | **约 3 分钟** | 是 | 253 |
| B: thinking=False + json_mode | **约 2 秒**（快 ~90 倍） | 是 | 253 |

→ 决策质量（JSON 有效性/长度）无差异。将 `config.THINKING` 默认设为 False，全管线切换，改一处全生效。

### 冒烟测试（thinking=False）通过 ✅
- 五阶段全通，1 天全程约 1~2 分钟
- 日总用电 **10.6943 kWh**（基载 1.2 + 决策 9.4943；Alice 6.282 + Bob 3.212）
- Token 账单：prompt 19,980 + 输出 48,501 = **68,481**（1 天 1 家庭）
- 0 条校验警告，四层日志 + 汇总 + 1440 点曲线齐全
- 负荷曲线形状真实：夜间 ~90W（冰箱 50W 基载+手机充电）、早晨 ~160W 小峰（8 点洗漱早餐）、晚高峰 **4530W @ 18:30**（做饭+空调+照明叠加）、0-6 点全程 ≥50W 基载存在

## 与计划的偏差
- 计划内 5 项任务全部完成
- **新增**：thinking 性能基准测试 + THINKING 全局开关（计划外的重大优化，直接对应论文 RQ4）
- **新增**：REASONING_EFFORT 可配置（medium）

## 学术应用

- **RQ4 的实证**：本次基准数据（thinking 开/关 = 3 分钟 vs 2 秒）直接回答了"大规模模拟的 LLM 调用成本如何优化"——90 倍差距是本项目可扩展性的关键杠杆
- 可复现性（固定种子 + 集中配置）对齐 AgentSociety (Piao et al. 2025) 的工程要求

## 下一步候选（计划3）

1. **跨天记忆**（昨日摘要 → 今日 prompt）：行为引擎核心卖点，且当前"每天失忆"是论文最大缺口
2. **人口级并行模拟 runner**（RQ1）：多家庭并行 + 聚合负荷
3. **真实电力数据基线对比**（vic_electricity_data.csv vs 模拟负荷，RQ3 起点）：本次产出曲线已有早晚双峰结构，可以量化比对了
4. 模拟日间的**状态连续性**（昨天今天同世界对象但无记忆传递——第 1 项的子问题）
