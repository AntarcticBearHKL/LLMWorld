# R056 — 多run平均工具 `aggregate_runs.py`（关键路径的基础设施）

- **轮次**：Round 56
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 267/267 单测绿；compileall exit 0）

---

## 1. 目标

R047/R054 的决定性结论：**单次运行方差压倒处理效应**，可信幅度必须来自**多种子/多成员平均**。
目前却缺少把多次运行聚合成"均值 ± 离散度"的工具——每次都靠临时脚本。本轮补齐，使平均实验一键可跑。

## 2. 依据

- R047（单次不可信）、R054（nudge 大样本 3/7 增耗、方差压倒）。
- 研究计划 §4.3（评估需报告分布/离散度）。
- 现有分析工具风格（`src/analyze/*.py`）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/analyze/aggregate_runs.py`（新增） | 纯函数 `summarize(values)`（n/mean/std/min/max，忽略 None，总体标准差）；`env_total_kwh(...)` 读取指定 env 的 s4 决策并算总电量；CLI `--world --house --member --date --envs ... [--tag]` 输出 per-env 与汇总 |
| `tests/test_aggregate_runs.py`（新增） | 5 个离线用例（summarize） |

**用法**：
```powershell
python src/analyze/aggregate_runs.py --world <w> --house house_0002 --date 2026-09-11 `
  --member "Member 1" --envs run1 run2 run3
# {'per_env': {...}, 'summary': {'n':3,'mean':...,'std':...,'min':...,'max':...}}
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 267 tests - OK
```

覆盖：空→全 None、单值 std=0、已知 [1,2,3]（mean 2.0、std≈0.8165）、忽略 None、全 None。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 267 tests — OK**（轮前 262 + 本轮 5） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思与限制

- 本轮只建**工具**；真正的平均 campaign（同一干预跑 N 个种子/环境）仍**需集中 token 预算**，
  由该工具汇总。
- 属基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **平均 campaign**（token 昂贵）：对最可跑的干预（如 nudge 或热浪）跑 N=3~5 次，
   用本工具报告 mean±std——这是把任何幅度结论升格的唯一路径；
2. 若预算不允许，论文保持"方向 vs 幅度"的谨慎措辞。
