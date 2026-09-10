# R027 — 恢复 `--policy-schedule`（公告→生效→移除 / 习惯黏性，guide §7）

- **轮次**：Round 27
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 218/218 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（drift）**：`intervention_experiment_guide.md` §7 列出
`--policy-schedule "2026-04-25,2026-04-28,tou"`（公告-生效-移除全生命周期、习惯黏性实验），
但该能力在重构后缺失（原属 `population_runner.py`）。`run.py` 只能全程施加单一 `--policy`。

**期望**：在 `run.py` 中恢复**按日期区间的政策时间线**：指定 `start,end,policy` 条目，
逐日在对应窗口内激活政策，窗口外回到 baseline；支持开区间（`end` 留空）。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §7（Policy schedule：公告-生效-移除，习惯黏性）。
- `engine/policy.py`（现有 `parse_policy_arg`）。
- 研究计划 §4.3 Phase Two（政策的时间传导）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/policy.py` | 新增 `parse_policy_schedule(specs)`（`start,end,policy`，`end` 可空=开区间，条目内不允许逗号费率参数）与 `active_policy_spec(schedule, date)`（区间内激活、最后一个匹配优先） |
| `run.py` | 新增 `--policy-schedule`（可重复）；`run_simulate(..., policy_schedule=None)`；逐日按 `active_policy_spec` 计算当日 `policy_text/tag` 并传给 s4（窗口外为 baseline），打印 `[Policy] <date>: <spec>` |
| `tests/test_core_logic.py` | 新增 `PolicyScheduleTests`（6 例） |

**用法**：
```powershell
python run.py --mode simulate --world <w> --days 5 --house house_0002 `
  --policy-schedule "2026-09-11,2026-09-12,tou" --policy-schedule "2026-09-13,,tou_soft"
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 218 tests - OK
```

覆盖：条目解析、开区间、空输入、畸形（缺字段）抛错、窗口内/边界/开区间激活、窗口间空档返回 None。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 218 tests — OK**（轮前 212 + 本轮 6） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（未真调）。

## 7. 反思与限制

- 时间线条目**只支持简单政策名**（`tou`/`tou_soft`），带费率参数的 `tou:<...>` 含逗号会与条目分隔冲突；
  如需费率，可后续用分号或 JSON 形式扩展（本轮不做，避免过度设计）。
- 与 `--policy` 并存：若提供 schedule 则以 schedule 为准（逐日覆盖）；否则沿用全局 `--policy`。
- 该能力为 RQ2 的"公告-生效-移除"实验铺路；属基础设施，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步

1. **政策时间线真调**（token-gated）：用 schedule 观察"移除后是否回弹"（习惯黏性）；
2. **多人户**平均以降低方差（TOU 结论待复现）；
3. `peer-nudge`（邻居均值注入）评估：需要日内跨户负荷，设计较复杂，暂缓或单列研究。
