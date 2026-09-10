# R051 — 会话交接（Handoff）

- **轮次**：Round 51（**0 token**）
- **日期**：2026-09-11
- **完整状态**：见 `reports/R047_consolidation_v3.md`（覆盖 R1–R46）。本文件补充 R47–R50 并给出**下一阶段前置条件**。

---

## 1. 当前状态一览

- **提交**：R1–R50 共 50 次，全部 push 到 `origin/main`（最新 `eef9a0c`）。
- **测试**：`tests/` **262/262 全绿**（全离线、mock `SubAgent`）；`compileall` 干净。
- **能力**：guide §1 全部干预入口 + 采样控制 + `--policy-schedule` + `--peer-nudge` + news/community；
  **漂移账本清零**。
- **论文**：`paper/README.md`（清单）+ `00_intro`/`01_method`/`99_discussion`（含 Threats-to-validity）
  + 12 个 `experiments/*.md`（4 个有初步结果，其余为第 1–5 节占位）。

## 2. 结果摘要（含置信度）

| 结论 | 置信度 | 关键证据 |
|---|---|---|
| 热浪→空调启用（二进制信号） | 初步-中 | baseline AC 恒 0；heatwave 多数启用（2 户；house_0001 3 人中 2/3） |
| 事件须与天气一致 | 高 | R14→R15→R16 |
| nudge 方向多成员稳健 | 初步-中 | 2 户 5 成员-日全负（−5.8%~−23.3%）；R040 去指令→≈0（措辞驱动） |
| nudge_loss 未复现损失厌恶 | 反例 | R041 总量 +6% |
| TOU 幅度不可定论 | 无 | 采样翻转（R026）；DiD 被对照证伪（R046） |
| **单次/单臂结果不可信** | **高（决定性）** | R024/R026/R045→R046 |

## 3. 下一阶段的前置条件（关键）

R050 复核发现：**现有 `world_838587` 生成于 R8 修复之前**，`energy_awareness` 全部退化
→ 无法据此做 RQ3 分组实验。因此：

1. **RQ3（群体异质性）**：需**重新生成世界**（`--mode world --count 3~5`，启用 awarenss 构念化）；
2. **subsidy / ev_delay**：需**含 EV 的世界**（生成不预设 EV，需事件/配置注入）；
3. **多成员平均**（升格幅度结论）：在（新）世界上重复干预，报告**均值 ± 离散度**。

> 以上均需集中 token 预算，建议作为下一阶段一次性 campaign 执行。

## 4. 立即可用的复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe run.py --mode world    --count 3 --seed 42
.venv\Scripts\python.exe run.py --mode simulate --world <w> --house house_0001 --days 2 --policy nudge
.venv\Scripts\python.exe run.py --mode simulate --world <w> --house house_0002 --days 3 --policy-schedule "2026-09-11,2026-09-12,tou"
.venv\Scripts\python.exe run.py --mode simulate --world <w> --house house_0002 --days 2 --event-template "2026-09-11|heatwave"
```

## 5. 纪律提醒

- 干预只以自然语言注入（红线）；事件须与环境天气一致；
- 单成员幅度不写结论；用二进制/定性或多成员均值；
- 每轮 commit+push；`output/` 不入库。
