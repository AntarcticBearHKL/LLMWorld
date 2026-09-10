# R028 — 会话合并检查点（drift 账本 + 结论置信度 + 下一步实验协议）

- **轮次**：Round 28（检查点；0 token）
- **日期**：2026-09-11
- **验证层级**：L0（汇总）
- **用途**：本文件汇总 R1–R27 的成果、测试状态、文献漂移账本、实验结论及其**置信度**，
  并给出**可执行的下一步实验协议**，便于后续会话在 token 受限下继续。

---

## 1. 测试与仓库状态

- **测试**：`tests/` 全部离线（mock `SubAgent`）—— **218/218 全绿**；`compileall` 干净。
- **提交**：R1–R27 共 27 次提交，全部 push 到 `origin/main`（最新 `7384f56`）。
- **产物**：`reports/R001–R027`、`paper/`（README + 00_intro/01_method/99_discussion +
  experiments/{event_heatwave,tou}）、`tests/`（9 个测试模块）。

## 2. 轮次账本（关键）

| 轮 | commit | 内容 | token |
|---|---|---|---|
| R1 | 912966f | 跨日延续 `day_state` 防瞬移 + 30 L1 | 0 |
| R2 | 58a1e73 | 充电池上限 + 行为可归因负荷 + 20 L1 | 0 |
| R3 | d24ba77 | 核心干预/解析/校验 + 44 L1 | 0 |
| R4 | 42157ea | `create_home_from_household` 去重 + 7 L1 | 0 |
| R5 | a192833 | B2 人格 Big Five/energy_awareness + 冗余房间 + 30 L1 | 0 |
| R6 | 60f5cd2 | 分析层纯函数 + 17 L1 | 0 |
| R7 | 9a4cd3d | world_838587 真实产物离线验证 | 0 |
| R8 | 5d6a46f | energy_awareness 构念化修复分组退化 + 8 L1 | 0 |
| R9 | af60e44 | 恢复 news 引擎（10 模板）+ 23 L1 | 0 |
| R10 | 3a6689f | news 接线 run.py/s1/s4 + 2 L1 | 0 |
| R11 | b455d50 | news 注入 L2 冒烟 | 4 |
| R12 | 859482f | community-notice 接线 + 1 L1 | 0 |
| R13 | a16013a | 恢复 compare_worlds.py + 4 L1 | 0 |
| R14 | dbbb137 | 热浪探针（null）+ 定位事件-天气不一致 | ~20 |
| R15 | 809b11b | 事件-天气联动 + 8 L1 | 0 |
| R16 | 3bca119 | 热浪效应（修复后）+ paper 初步 | 8 |
| R17 | da37927 | s1 连续性重写集成测试 + 3 L1 | 0 |
| R18 | 91b4414 | event_response 纯函数 + 5 L1 | 0 |
| R19 | ee13bce | 修 `_normalize_date` 死代码 + 4 L1 | 0 |
| R20 | 5af1cc8 | 热浪第 2 窗口复现 | 16 |
| R21 | c0fec3c | 论文骨架 00/01/99 | 0 |
| R22 | 1b87e4f | 热浪跨住户（house_0001）复现 | 8 |
| R23 | 625db1f | TOU 实验（峰 −18~−26%） | 16 |
| R24 | 6dc40c2 | tou_soft 去指令消融（自相矛盾） | 8 |
| R25 | ec5a30e | 采样控制 `--temperature/--no-thinking/--reasoning-effort` + 4 L1 | 0 |
| R26 | b02a2fe | 低方差 TOU（方向翻转） | ~24 |
| R27 | 7384f56 | 恢复 `--policy-schedule` + 6 L1 | 0 |

> 真调总额 ≈ **120 次调用**（L2 小范围），其余均 L0/L1。

## 3. 实验结论与置信度

| 结论 | 证据 | 置信度 |
|---|---|---|
| **热浪→降温负荷上升** | 2 户 / 3 个 event-day：control AC 恒 0，heatwave AC 恒 >0（7.2/1.8/7.2/2.4/3.6 kWh） | **初步-中**（二进制信号稳健；n 小） |
| 事件须与环境天气一致 | R14 无效应 → R15 联动 → R16 出现效应 | 高（机制清晰） |
| **TOU 削峰** | 推理模式 −18~−26%；去指令消融与低方差复测**方向翻转**（+8~+30%） | **无**（对采样/推理模式敏感，n=1 不可分离） |
| 单成员 A/B 方差主导 | R24/R26 | 高（方法学结论） |

## 4. 文献漂移账本

- **已恢复**：`engine/news.py`（10 模板；原 `news_templates.py` 合并）、
  `--event/--event-template/--community-notice`、`src/analyze/compare_worlds.py`、
  `--policy-schedule`（并入 `run.py`）。
- **仍缺**：`population_runner.py` 的 **`--peer-nudge`**（邻居均值注入）——需要日内跨户负荷，
  设计较复杂；其 policy-schedule 部分已由 R27 覆盖。

## 5. 建议的下一步实验协议（token 受控）

1. **多人户热浪复现（首选，稳健信号）**：`house_0001`（4 人）1 天，heatwave vs control
   → 2 臂 × 4 成员 × 4 步 ≈ **32 次调用**；度量每户 AC on/off 计数。
2. **多人户 TOU（次选，验证是否可救）**：固定**同一星期几**、≥3 成员、≥2 户，两臂取**均值**；
   ≈ **48 次调用**；若仍不可分离则正式标注"本平台 TOU 幅度不可评估"。
3. **政策时间线（习惯黏性）**：`--policy-schedule`，5 天，观察移除后回弹；≈ **20 次调用**。

**纪律**：单成员幅度不写结论；只用二进制/定性或在多人均值上做幅度比较。

## 6. 复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v     # 218 全绿
.venv\Scripts\python.exe run.py --help                         # 查看 --policy/--policy-schedule/--event/--community-notice/--temperature 等
```
