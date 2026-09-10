# R019 — 修复 analyze_event_response._normalize_date 死代码（Unicode 日期规范化）

- **轮次**：Round 19
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 206/206 单测绿）

---

## 1. 目标（现状 → 期望）

**现状（R18 发现）**：`analyze_event_response._normalize_date` 含三个**空替换**
`.replace("-", "-").replace("-", "-").replace("", "")`——即历史编辑把 Unicode 破折号/零宽字符
丢失后留下的**死代码**，实际只做了"8 位数字→ISO"一件事。若 events/日期来自不同来源
（如含 en-dash 或零宽字符），日期比对会失败，导致事件日被漏配。

**期望**：恢复其本意——规范化 Unicode 破折号与不可见字符，再统一 8 位数字为 ISO；
不改变既有 ASCII 行为。

## 2. 依据（先读后做）

- R18 反思（死代码定位）。
- `src/analyze/analyze_event_response.py` 用 `_normalize_date` 对齐事件日期与模拟日期。
- goal.md §5（正确性 bug / 健壮性允许优化）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/analyze/analyze_event_response.py` | 新增模块常量 `_DATE_DASH_VARIANTS`（en/em/minus/fullwidth）与 `_DATE_INVISIBLE`（零宽空格/BOM/空格/制表）；`_normalize_date` 先替换破折号、去不可见字符，再做 8 位数字→ISO |
| `tests/test_event_response.py` | 新增 `NormalizeDateTests`（4 例） |

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 206 tests - OK
```

覆盖：ASCII 不变、en-dash/minus 归一、`20260911`→`2026-09-11`、空格与零宽字符剔除。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 206 tests — OK**（轮前 202 + 本轮 4） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思

- 这是"测试驱动发现并修复真实死代码"的一例：R18 仅写测试时即定位到该缺陷，R19 修复并加回归。
- 修改为**行为兼容增强**（ASCII 输入结果不变），风险低。
- 属正确性修复，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **复现热浪效应**（多人户/多日/多种子，token-gated）——R16 仅 n=1；
2. `population_runner.py`（peer-nudge / policy-schedule）恢复或 guide 校正；
3. 用 `analyze_event_response.py` 对现有 `heatwave_probe2` vs `ctrl_probe` 跑一次事件日模式转移。
