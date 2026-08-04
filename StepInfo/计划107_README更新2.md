# 计划107:README 全面更新第二轮

## 做什么

README 全面同步当前系统状态(计划63 首轮更新后新增
约 10 个工具/2 政策/15 面板):
- 快速开始:分析工具全清单(20 个)、CSV 导出、政策 8 种
- 架构:新增模块(analyze_advice/forecast/appliance_usage/
  world_summary/tradeoffs/export_csv 等)
- 前端能力:新增面板清单
- 测试数 202

## 为什么(依据)

**§七.6 README 更新 + 读档契约**(运维经验):README 是
新用户/读档 agent 的第一入口,须与代码库同步。

## 怎么做

1. README 重写"快速开始/架构/前端能力"三节
2. 测试:202 项全绿(纯文档)

## 怎么验证

- `python Implement/test_offline.py` 202 项全绿
