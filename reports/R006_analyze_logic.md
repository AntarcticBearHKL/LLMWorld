# R006 — 分析层纯函数 L1 锁定（分组响应 / 政策权衡 / TOU 窗口）

- **轮次**：Round 6
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 148/148 单测绿，本轮新增 17 项）

---

## 1. 目标（现状 → 期望）

**现状**：论文要报的三个核心量——**分组政策响应**（RQ3 异质性）、**峰削减/平台率/峰均比**
（政策权衡）、**峰谷时段用电归因**（TOU）——都由 `src/analyze/` 的纯函数计算，
但此前无离线测试；这些函数一旦算错，`paper/` 的数值会整片失真。

**期望**：为这些纯函数补 L1，锁定指标定义与边界（零均值、空段、非计费动作、缺基线）。

## 2. 依据（先读后做）

- **干预指南** §8 效果对照表：峰值削减%、总量变化%、峰移——正是这些函数输出的量。
- **研究计划** RQ3（宏观涌现/异质分组）、§4.3 Phase Two/Three 评估指标。
- **文献** Costa & Kahn (2010)（同政策分组分化）、Faruqui & Sergici (2010)（峰削减口径）。
- **analyze 脚本**：`analyze_groups.py`、`analyze_policy_tradeoffs.py`、`compare_tou.py`、`dataset.py`。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_analyze_logic.py`（新增） | 17 个离线用例 |

覆盖：

- `analyze_groups.group_stats`：组内均值、`% vs baseline`、分组顺序、**缺 baseline 时值为 None**；
- `analyze_policy_tradeoffs`：`energy_of_hours`（时段电量 kWh）、`peak_plateau_minutes`（≥80% 峰值的分钟数、零 profile）、
  `peak_to_mean_ratio`（零均值返回 None）、`_change_pct`（基准 0 返回 None）；
- `compare_tou`：`minutes_of_day`、`window_of`（peak/valley/shoulder 边界）、
  `segment_minutes`（含 `24:00` 端点与非法输入）、`summarize`（按窗口归因，忽略非计费动作）；
- `dataset.household_features`：读取 `energy_awareness`/`big_five`、缺字段默认 `"?"`、非字典兜底。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 148 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 148 tests — OK**（轮前 131 + 本轮 17） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思

- 外部 `run.py --mode simulate --world world_838587 --days 2` 已结束（进程消失，末次输出 00:53:20），
  工作树源码已干净（仅 `output/` 产物未跟踪）；本轮继续只 stage 新测试与本报告。
- 至此 **goal.md §4 L1 清单 + 分析层核心指标**均有离线覆盖，后续改动有回归网。
- 纯测试基础设施，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **L2 小范围真调**（额度已空闲）：`--mode simulate --house house_0001 --member 0 --days 2`
   验证 R1 跨日连续性 + R2 电池上限 + B2 人格字段落盘；预计 token 受控（单成员 2 天）；
2. 文档漂移修复：`population_runner.py`/`engine/news*.py`/`compare_worlds.py`；
3. 用真实 analyze 输出填 `paper/experiments/tou.md` 的占位（待 L2/L3 有效果后）。
