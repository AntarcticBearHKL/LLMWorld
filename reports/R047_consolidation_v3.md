# R047 — 合并检查点 v3（覆盖 R1–R46，含决定性方法学结论）

- **轮次**：Round 47（检查点；0 token）
- **日期**：2026-09-11
- **用途**：汇总整段工作（R1–R46）、测试状态、能力完备性、实验结论与**下一步的唯一关键路径**。

---

## 1. 仓库与测试

- `tests/` 全部离线（mock `SubAgent`）—— **262/262 全绿**；`compileall` 干净。
- R1–R46 共 46 次提交，全部 push 到 `origin/main`（最新 `1739adc`）。
- 产物：`reports/R001–R046`、`paper/`（README + 00/01/99 + 12 个 experiment 文件）。

## 2. 能力完备性（对照 guide §1）

**全部具备入口**：tou / tou_soft / nudge / nudge_soft / nudge_loss / subsidy / peak_demand /
ev_delay / night_setback / in_home_display；news（10 模板 + 自定义 + 天气联动）；community-notice；
`--policy-schedule`；`--peer-nudge`；`--temperature/--no-thinking/--reasoning-effort`。
原 `population_runner.py` 职能并入 `run.py`。**漂移账本清零**。

## 3. 实验结论（含置信度）

| 结论 | 证据 | 置信度 |
|---|---|---|
| 热浪→降温负荷上升（二进制） | 2 户 / 3 event-day：control AC=0、heatwave AC>0 | 初步-中 |
| 事件须与环境天气一致 | R14→R15→R16 | 高 |
| **nudge 效应由规范性措辞驱动** | R040 去指令 −6~−10%→≈0；跨 2 户方向一致（R043） | 初步-中 |
| **nudge_loss 未复现损失厌恶** | R041 +6%（方向相反） | 反例 |
| TOU 幅度**不可定论** | 方向随采样翻转（R026）；DiD 被对照证伪（R046） | 无 |
| **单次/单臂结果不可信** | R024/R026/R045→R046（对照推翻同臂结论） | **高（决定性）** |

## 4. 决定性方法学结论

> **在两个独立采样的运行之间，差异可与处理效应同量级甚至更大。**
> 因此任何幅度结论必须建立在**多种子 / 多成员平均**之上；单次单成员结果（乃至单臂内前后对比、
> 乃至一对平行臂的 DiD）都可能给出**假阳性**（R045 的"回弹"即被 R046 对照证伪）。

## 5. 论文状态

- `00_intro` / `01_method` / `99_discussion`（Threats-to-validity 已记录"过度遵从 + 框架不稳定 +
  单次不可信"）草稿完成。
- experiment 文件：`event_heatwave`（初步-中）、`tou`（不可定论 + 习惯黏性被证伪）、
  `nudge`（措辞驱动）、`nudge_loss`（反例）、`peer_nudge`（不一致），其余 7 个为占位（第 1–5 节）。

## 6. 下一步（唯一关键路径，token 较高）

**多成员/多种子的平均实验**：同一干预在 ≥2 户 / ≥3 成员 / 固定星期上重复（或同世界多种子），
报告**均值 ± 离散度**。建议优先：
1. `nudge` vs baseline（措辞驱动的稳健性）；
2. 热浪（二进制信号，最快可达显著）；
3. TOU（若平均后仍不可分离，则正式标注"本平台 TOU 幅度不可评估"）。

> 该campaign 需集中 token 预算；在此之前，论文所有幅度结论保持"待验证/不可定论"。

## 7. 复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v     # 262 全绿
.venv\Scripts\python.exe run.py --help                         # 全部干预/采样入口
```
