# R029 — `--policy-schedule` 逐日接线的集成测试（mock 步骤，0 token）

- **轮次**：Round 29
- **日期**：2026-09-11
- **验证层级**：L1 集成（**4 个 simulate 步骤被 mock，0 API**）
- **结论**：✅ 通过（累计 221/221 单测绿）

---

## 1. 目标（现状 → 期望）

**现状**：R027 新增的 `--policy-schedule` 只有纯函数（解析/激活）单测，
`run_simulate` 的**逐日接线**（窗口内激活、窗口外回 baseline、打印 `[Policy]`）未被验证。

**期望**：mock 掉 `s1/s2/s3/s4` 步骤与成员枚举，直接验证每日传给 s4 的
`policy_text/policy_tag` 是否符合时间线。

## 2. 依据

- R027（`engine/policy.parse_policy_schedule/active_policy_spec`）。
- goal.md §4 L1（mock `SubAgent`/链路做集成测试）。
- 参照 R017 的 `s1.run_step` 集成测试模式。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_policy_schedule_integration.py`（新增） | 3 个集成用例；mock `run.get_member_names` 与 `run.s{1,2,3,4}_*.run_step`，调用 `run.run_simulate(..., days=2, policy_schedule=...)` 并检查 `s4` 的调用参数 |

用例：
1. **窗口内激活**：`"2026-09-11,2026-09-11,tou"` → 第 1 天 `policy_tag="tou"`、文本含 "time-of-use"；
   第 2 天 `policy_tag=None`、`policy_text=""`；
2. **开区间**：`"2026-09-11,,tou_soft"` → 两天均为 `tou_soft`；
3. **全局 `--policy`**：无 schedule 时两天均 `tou`（回归保护）。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 221 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 221 tests — OK**（轮前 218 + 本轮 3） |

**是否符合预期**：是。R027 的逐日接线已被端到端锁定。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（步骤被 mock）。

## 7. 反思

- 该测试同时保护了 R027 引入的"逐日政策覆盖全局 `--policy`"语义，避免未来重构回退。
- 属测试基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **`peer-nudge`**（guide §6.1）：把上一日社区均值注入 s4（需跨层读取，注意分层）；
2. **多人户实验**（token-gated）以降低 TOU/热浪的方差；
3. 政策时间线真调（习惯黏性，≈20 次调用）。
