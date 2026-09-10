# R017 — s1 连续性重写路径的端到端集成测试（mock LLM，0 token）

- **轮次**：Round 17
- **日期**：2026-09-11
- **验证层级**：L1 集成（**SubAgent 被 mock，0 API**）
- **结论**：✅ 通过（累计 197/197 单测绿）

---

## 1. 目标（现状 → 期望）

**现状（自 R1 起的功能缺口）**：`reconcile_boundary` 已有 30 项纯函数单测，
`{carry_over_context}` 占位符也有渲染测试；但**整条链路**
（`load Home → 注入 carry-over prompt → 重写日界 → 落盘 s1_macro + day_state`）
从未被端到端验证——R7 真实运行里也没有成员以 `Out` 结束，重写分支未被触发。

**期望**：用 mock 的 `SubAgent.single_call` + 临时 world，锁定该集成路径的行为。

## 2. 依据（先读后做）

- goal.md §4 L1："为纯逻辑写/跑测试并 mock 掉 `SubAgent`，禁止真调 API"。
- R1（`day_state`/`reconcile_boundary`）与 R7（真实运行仅覆盖 no-op 路径）的遗留。
- 代码：`src/steps/simulate/s1_macro_plan.py:run_step`、`engine/prompt.py`。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_continuity_integration.py`（新增） | 3 个集成用例；`gw.WORLDS_DIR`/`gw.SIMULATION_DIR` 重定向到临时目录，`SubAgent.single_call` 返回固定计划 |

用例：

1. `ends_out=True` → prompt 含注入句 `"The previous day ended at 24:00"`；落盘
   `s1_macro` 首段被改写为 `00:00-00:45 / Out / Commuting home from work`；
   且 `day_state` 记录当日末状态（`ends_out=False`）；
2. 无前日 → prompt 不含注入句、计划首段保持 `00:00-08:00`；
3. 前日为居家 → 同 2。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 197 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 197 tests — OK**（轮前 194 + 本轮 3） |

**是否符合预期**：是。重写分支现已被**集成层**锁定（此前仅纯函数层）。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（`SubAgent` 被 mock）。

## 7. 反思

- 首次运行暴露一个**测试自身的断言缺陷**：静态 prompt 里本就含短语 "previous day ended"，
  导致"未注入"断言误报；改用注入句的唯一前缀 `"The previous day ended at 24:00"` 后修复
  ——提醒：断言哨兵必须与模板静态文本可区分。
- 属测试基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **复现热浪效应**（R16 仅 n=1）：≥3 人户 × ≥2 天，或多日期，确认方向稳健（token-gated）；
2. 用 `analyze_event_response.py` 对事件日做模式转移度量；
3. `population_runner.py`（peer-nudge / policy-schedule）恢复或 guide 校正。
