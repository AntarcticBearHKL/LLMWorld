# R018 — analyze_event_response 纯函数 L1（事件日分析路径）

- **轮次**：Round 18
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 202/202 单测绿）

---

## 1. 目标

R16 的热浪效应后续需用 `analyze_event_response.py` 做"事件日 vs 非事件日"的模式转移度量。
本轮先把它依赖的两个纯函数锁进 L1，降低后续误读风险。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §5.1（事件→`analyze_event_response.py` 观察行为模式转移）。
- R16/R14（事件实验）；goal.md §4 L1（纯逻辑离线测试）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_event_response.py`（新增） | 5 个用例：`hourly_means` 与 `normalize_shape` |

覆盖：
- `hourly_means`：单小时恒载 600W → 该小时 600、其余 0；全零曲线 → 24 个 0；长度恒为 24；
- `normalize_shape`：总和为 0 → 全 0；`[1,3]` → `[0.25,0.75]` 且总和 1；长度保持。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 202 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 202 tests — OK**（轮前 197 + 本轮 5） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思

- 补充说明（未改代码）：`analyze_event_response._normalize_date` 存在**明显的空替换**语句
  （`.replace("-", "-").replace("-", "-").replace("", "")`，疑似历史编辑把 Unicode 破折号/零宽字符
  吃掉后留下的死代码）。本轮不改它以防越界；**列为下一轮候选**（规范化 Unicode 日期分隔符 + L1）。
- 属测试基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **`_normalize_date` 规范化修复**（Unicode 破折号/8 位数字 → ISO）+ L1；
2. **复现热浪效应**（多人户/多日，token-gated）；
3. `population_runner.py`（peer-nudge / policy-schedule）恢复或 guide 校正。
