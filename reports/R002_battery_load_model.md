# R002 — 充电池上限 + 行为可归因负荷（Feature B1）锁定与提交

- **轮次**：Round 2（永续协议）
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 50/50 单测绿，含本轮新增 20 项）

---

## 1. 目标（现状 → 期望）

**现状**：`ChargingAppliance`（EV / E-bike / Phone）的 `charge_home` 只受
`config.APPLIANCE_DAILY_CAP_MINUTES` 的**分钟数上限**约束，没有物理电量上限。
结果：一台 EV 一天可充 4 h × 7 kW = 28 kWh，而默认 `soc=0.5` 时电量缺口只有 30 kWh——
更关键的是 Phone：240 min × 20 W = 0.08 kWh，而手机电池只有 0.02 kWh，**一天能充 4 块电池**，
负荷被高估、锚点失真。

**期望**：给充电设备加**电池电量上限**——一天的家用充电量不得超过
`(1 - soc) × battery_kwh`；并让 `analyze_behavior_load` 使用"行为可归因"负荷
（剔除 EV/E-bike/冰箱/冷柜/路由器等恒定或纯充电型负载），以正确衡量"活动-负荷"一致性。

**性质**：能耗核算正确性 + 分析口径修正，属 goal.md §5 允许范围；不改研究语义（LLM 只被**告知**
"一块电池/天、优先夜间充"，不硬编码行为）。

## 2. 依据（先读后做）

- **文献**：Alexeenko & Bitar (2023) 住宅 EV 协同充电试点、Thorvaldsen et al. (2021) 柔性资产长期价值
  —— 两者均以"一次充电不超过一块电池容量、夜间充满即停"为物理前提；`RefPaper/README.md` 标注对应
  **计划43/47**。本轮的电池上限正是 EV 峰移类实验（subsidy / ev_delay）可信度的物理约束。
- **研究计划**：`研究计划.md` §4.2 领域模型层——设备按 on-demand / charging / always-on 抽象，
  充电类需"额定功率 + 状态机"；本轮补上充电类的储能状态（capacity/soc）。
- **干预指南**：`intervention_experiment_guide.md` §2.2/§2.4（EV 期望峰移 30~60%）——若单日可充多块电池，
  峰值负荷会被系统性高估，基准对齐失效。
- **analyze**：`src/analyze/load_model.py`（能耗核算）、`analyze_behavior_load.py`（活动-负荷一致性）。

## 3. 改动（已在工作树中未提交，本轮审阅 + 离线锁定 + 入库）

| 文件 | 改动 |
|---|---|
| `src/appliances/catalog.py` | 新增 `BATTERY_KWH`/`DEFAULT_SOC` 与 `battery_kwh()`/`default_soc()`（EV 60kWh/0.5、Ebike 0.5/0.5、Phone 0.02/0.3） |
| `src/appliances/base.py` | `ChargingAppliance` 增加 `battery_kwh`/`soc` 参数（缺省取 catalog）与 `charge_deficit_kwh()`；`to_dict` 暴露两字段 |
| `src/appliances/{electric_vehicle,ebike,phone}.py` | `from_config` 透传 `battery_kwh`/`soc` |
| `src/analyze/load_model.py` | `_accumulate` 增加电池上限（按时间顺序截断，跨界分钟按缺口精确缩放）；`build_load_profile(..., exclude_families=...)` 产出行为可归因负荷 |
| `src/analyze/analyze_behavior_load.py` | 用 `BEHAVIOR_EXCLUDE_FAMILIES={ElectricVehicle,Ebike,Refrigerator,Freezer,Router}` 计算 `behavior_profile_watts`；报告同时给出原始/行为 `total_kwh` |
| `src/prompts/simulate_step4_batch_appliance_decision.md` | 明确告知 LLM"一块电池/天、充满即 idle、优先夜间" |

**相互作用**：`APPLIANCE_DAILY_CAP_MINUTES` 先裁剪分钟数，电池上限再裁剪电量，二者取更紧者。
例：Phone 上限 240min(0.08kWh) 与缺口 0.014kWh → 电池上限绑定；EV 上限 240min(28kWh) 与缺口 30kWh → 分钟上限绑定。

## 4. 测试（L0/L1）

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py          # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests -v     # Ran 50 tests - OK
```

新增 `tests/test_battery_load_model.py`（20 例）：

- catalog 已知/未知类型；`ChargingAppliance` 缺省值、`charge_deficit_kwh` 数学、显式覆盖、`soc=1` 零缺口、未知电池为 `None`、`to_dict` 暴露字段；
- EV/Ebike/Phone `from_config` 透传与缺省回退；
- `_accumulate`：**电池上限在分钟上限之后绑定**（Phone 结果==缺口 0.014）、**分钟上限更紧时生效**（EV==28kWh）、低于缺口不裁剪、未知电池不裁剪、**跨界精确落在缺口**（Widget 1.0kWh）；
- `build_load_profile`：手机电池下限进入 profile、`exclude_families` 归零且键保留（shape 稳定）、部分剔除只影响匹配族；
- `analyze_behavior_load.build_report`：新键 `total_kwh`/`behavior_total_kwh`/`exclude_families` 正确产出。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 50 tests — OK**（本轮前 30 + 本轮 20） |

**是否符合预期**：是。电池上限与分析口径均被 L1 锁定。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思

- **发现（正确的设计）**：EV 的 4h 分钟上限已隐含 28kWh，恰小于 60kWh×0.5 的 30kWh 缺口，
  因此对 EV 而言电池上限**当前是冗余安全网**；对 Phone/E-bike 才是实际绑定约束。已在报告显式记录。
- **遗留（下轮处理）**：`build_load_profile` 的 `exclude_families` 属"行为可归因"口径，仍需在真实 world 上做
  L2 小范围验证（`analyze_behavior_load` 的 `scan_world` 依赖文件，本层只测了纯函数 `build_report`）。
- **分流**：本轮为正确性/核算基础设施，**无与文献可对照的"有效果"结论 → 仅入 `reports/`**，不进 `paper/`。
- 工作树仍余 **Feature B2**（`s3_household_build.py` 的 Big Five/energy_awareness + 冗余房间去除、
  `generate_world_step3_home/member.md`）与一个 `output/` 分析产物，留待 Round 3。

## 8. 可复现命令

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 9. 下一步（候选，Round 3）

1. Feature B2：人格 Big Five/energy_awareness 落地 + 冗余房间去除的离线单测 → 提交；
2. 上一条的 L2 小范围真调：单户 × 1 天，确认 `exclude_families` 行为负荷与原始负荷差异合理；
3. 文档漂移修复：`population_runner.py`/`engine/news*.py`/`compare_worlds.py` 缺失。
