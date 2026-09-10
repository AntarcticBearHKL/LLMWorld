# R013 — 恢复 compare_worlds.py（多世界对照，guide §7）

- **轮次**：Round 13
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 186/186 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（drift）**：`intervention_experiment_guide.md` §7 把
`compare_worlds.py --worlds pop03 pop04` 列为"同一政策在不同人口结构下的稳健性"工具，
但当前 `src/analyze/` 中该脚本**缺失**（goal.md §1 记录的漂移）。

**期望**：恢复一个最小可用的多世界对照脚本：对每个世界计算同一 scenario/date 的聚合负荷指标，
便于检验"同政策跨结构一致性"（RQ3）。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §7（Multi-world control，Eco3S 2026 交叉检验范式）。
- 研究计划 §4.3 Phase One/Two（人口基线 + 政策响应的群体稳健性）。
- 现有 `dataset.population_profile(world_id, policy, date, env)` 已能聚合单世界负荷曲线（复用）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/analyze/compare_worlds.py`（新增） | `profile_metrics(profile_watts)` 纯函数（总电量/峰值/峰时/峰均比/晨晚电量与晚晨比）；`compare_worlds(worlds, scenario, date)`；CLI `--worlds --scenario --date --out`，输出表格 + `output/analysis/compare_worlds_<scenario>.json` |
| `tests/test_compare_worlds.py`（新增） | 4 个离线用例（空曲线、已知曲线精确值、零曲线无比值、无晨峰时晚晨比为 None） |

**指标定义**：晨 = 6–9h，晚 = 17–21h；`peak_to_mean = peak/mean`；`evening_morning_ratio = evening/morning`（无晨峰→None）。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 186 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 186 tests — OK**（轮前 182 + 本轮 4） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思与限制

- 仅恢复**聚合对照**这一最小形态；`compare_worlds` 的端到端运行需要多个已模拟世界（当前只有 `world_838587`），
  故本轮只对纯函数做 L1；真调运行留待有 2+ 世界时。
- 属分析工具恢复，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **事件效果探针**（token-gated）：同一世界/成员，`heatwave` vs 无事件，2–3 天，
   `analyze_event_response.py` 对比（注意 LLM 随机性）；
2. 触发 R1 "Out→通勤"重写分支的真实样本；
3. `population_runner.py`（policy-schedule / peer-nudge）恢复或 guide 校正。
