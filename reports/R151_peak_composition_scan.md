# R151 — 各住户峰段构成扫描（0 token）：晚峰由"烹饪"主导 → 统一机制

- **轮次**：Round 151
- **日期**：2026-09-11
- **验证层级**：**L0 分析**（复用既有 baseline；**0 token**）
- **网络状态**：⚠️ **HTTPS 中断**（DeepSeek API + GitHub 均不可达）→ 暂缓 L2 实验与 push（见末）

---

## 1. 结果（峰段 16–21 各户构成）

| 世界 | 住户 | 总峰 kWh | 主导设备（占比） |
|---|---|---|---|
| world_838587 | house_0002 | 3.69 | **InductionCooker 54%**, WaterHeater 20% |
| world_172148 | house_0002 | 4.01 | **InductionCooker 50%**, Vacuum 15% |
| world_172148 | house_0001 | 5.37 | **InductionCooker 47%**, Computer 29% |
| world_143345 | house_0002 | 4.18 | **InductionCooker 48%**, Computer 15% |
| world_143345 | house_0003 | 5.01 | **AirConditioner 28%**, InductionCooker 17% |
| world_143345 | house_0001 | 8.53 | **InductionCooker 27%**, Computer 18%, Oven 18% |
| world_838587 | house_0001 | 2.62 | **Computer 46%**, Refrigerator 10% |

## 2. 解读（统一机制）

- **晚峰普遍由烹饪主导**（InductionCooker 27–54%，5/7 户）；个别户由 **AC**（h003 28%）或 **Computer**（h001 46%）主导；
- 结合 N7/N7b/R149：**烹饪设备可替代**（电磁炉↔烤箱↔微波炉）→ 靶向它们**不削总峰**；
- 结合 R135：**AC 不可替代** → 靶向 AC（ac_tax）**真削峰**；
- → **"某户晚峰是否可削"取决于其主导设备是否可替代**：
  - 烹饪主导户（多数）→ 设备靶向**不削峰**（替代）；
  - AC 主导户（如 h003）→ 靶向 AC **可削峰**。

## 3. 论文意义

- 为 R131/R135/R144 的机制提供**人群级检验**：**晚峰构成的设备-可替代性**决定削峰潜力；
- 政策含义：**对"烹饪主导"的住宅，需"窗口+价格"（移动整段晚峰）而非"设备靶向"**。

## 4. 网络中断与待办

- **DeepSeek API 连接超时**（`ConnectTimeoutError`）→ 无法跑 L2；
- **GitHub push 失败**（ahead 3+）→ 本地已提交，标"**待推送**"；
- **被阻塞的实验**：N7 替代效应的**跨世界**复现（world_172148 h001）——网络恢复后继续；
- 期间按 goal.md §10 熔断规则**切 L0/L1**，继续 0-token 分析。
