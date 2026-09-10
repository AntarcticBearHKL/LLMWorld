# R042 — 合并检查点 v2（覆盖 R29–R41）

- **轮次**：Round 42（检查点；0 token）
- **日期**：2026-09-11
- **用途**：汇总 R29–R41 的成果、测试状态、**能力完备性**、**实验结论**与**下一步**，替代已过时的 R028。

---

## 1. 仓库与测试

- **测试**：`tests/` 全部离线（mock `SubAgent`）—— **262/262 全绿**；`compileall` 干净。
- **提交**：R1–R41 共 41 次提交，全部 push 到 `origin/main`（最新 `d896267`）。

## 2. R29–R41 关键轮次

| 轮 | commit | 内容 | token |
|---|---|---|---|
| R29 | 92086ee | `run_simulate` 逐日政策时间线接线集成测试 + 3 L1 | 0 |
| R30 | 256f3e6 | 家电能耗公式 L1（on-demand/always-on/cycle）+ 10 | 0 |
| R31 | 9f289e2 | 日期上下文 `Time` L1 + 13 | 0 |
| R32 | a7de3d3 | 恢复 `--peer-nudge`（动态邻居均值）+ 7 L1 | 0 |
| R33 | 3d4200d | peer-nudge 端到端冒烟 | 8 |
| R34 | df03ebe | 恢复 `nudge` / `nudge_loss` + 4 L1 | 0 |
| R35 | a1566bf | 恢复 subsidy/peak_demand/ev_delay/night_setback/in_home_display + 5 L1 | 0 |
| R36 | e4f48fb | 文档同步（method 干预面＝实现） | 0 |
| R37 | 2c878eb | `nudge` vs `peer-nudge` A/B + paper/nudge.md | 16 |
| R38 | aed676a | 新增 `nudge_soft` 消融入口 + 2 L1 | 0 |
| R39 | 12c6422 | 论文 validity 小节：prompt 过度遵从 | 0 |
| R40 | df7e28c | `nudge_soft` 消融（支持过度遵从） | 8 |
| R41 | d896267 | `nudge_loss` 反例（+6%，与预期相反） | 8 |

## 3. 能力完备性（guide §1 对照）

**全部具备入口**：TOU / TOU-soft / **nudge / nudge_soft / nudge_loss** / subsidy / peak_demand /
ev_delay / night_setback / in_home_display；news（10 模板 + 自定义 + 天气联动）；community-notice；
`--policy-schedule`（时间线）；`--peer-nudge`（动态邻居均值）。原 `population_runner.py` 职能并入 `run.py`。

## 4. 实验结论与置信度

| 结论 | 证据 | 置信度 |
|---|---|---|
| 热浪→降温负荷上升 | 2 户 / 3 event-day：control AC=0、heatwave AC>0 | 初步-中 |
| 事件须与环境天气一致 | R14→R15→R16 | 高 |
| **TOU 幅度不可定论** | 方向随采样翻转（−18~−26% ↔ +8~+30%） | 无 |
| **nudge 效应由规范性措辞驱动** | R040 去指令消融 −6~−10%→≈0 | 初步-中 |
| **nudge_loss 未复现损失厌恶** | R041 +6% vs nudge −6~−10% | 初步反例 |
| 单成员 A/B 方差主导 | R024/R026 | 高（方法学） |

## 5. 论文状态

- 章节：`00_intro.md` / `01_method.md` / `99_discussion.md`（含 Threats-to-validity：过度遵从 + 框架不稳定）。
- 实验条目：`event_heatwave.md`（初步-中）、`tou.md`（不可定论）、`nudge.md`（措辞驱动）、`nudge_loss.md`（反例）。
- 其余实验（subsidy/peak_demand/ev_delay/night_setback/in_home_display/peer_nudge/group/heterogeneity/tradeoffs）待做。

## 6. 下一步（token 受控）

1. **多人户实验**（首要）：同一设计在 ≥2 户 / ≥3 成员 / 固定星期上取均值，检验
   "措辞主导"与"热浪方向"是否稳健；这是把初步结论升格为正式结论的关键。
2. `nudge` / `nudge_soft` / `nudge_loss` 三人户×多日；
3. `--policy-schedule` 真调（习惯黏性，≈20 次调用）；
4. 视结果把 `paper/999_discussion.md` 的"措辞主导"升级为独立方法学小节。

**纪律**：单成员幅度不写结论；只用二进制/定性或在多人均值上做幅度比较。

## 7. 复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v     # 262 全绿
.venv\Scripts\python.exe run.py --help                         # 全部干预入口
```
