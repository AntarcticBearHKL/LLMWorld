# R012 — 接线 community-notice（轻量社会信号，guide §6）

- **轮次**：Round 12
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 182/182 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状**：s1 模板有 `{community_notice}` 占位符，但一直被硬编码为 `""`；
`run.py` 无 `--community-notice`。guide §6.2 的"社区公告"信号无法注入。

**期望**：打通 `--community-notice "date|title|content"` → 逐日 `community_notice` → **s1 prompt** 全链路；
公告同样以**自然语言**告知居民，并写入 `events.json` 供分析脚本消费。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §6.2（社区公告：计划停电维护等，观察公告日前后用电模式变化）。
- 研究语义红线：仅自然语言注入，效果涌现。
- 复用 R9 的 `engine.news.parse_event_spec` / `events_for_date` / `render_world_news`。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `run.py` | `run_simulate(..., notices=None)`；`events + notices` 一并写入 `events.json`；逐日 `day_notice=render(events_for_date(notices,...))` 传入 s1；新增 `--community-notice`（可重复），与 `--event` 同一套解析/校验 |
| `src/steps/simulate/s1_macro_plan.py` | `run_step(..., community_notice="")`；Prompt 传 `community_notice=community_notice` |
| `tests/test_news.py` | 新增 1 项：s1 模板渲染 `{community_notice}` 哨兵 |

**用法**：
```powershell
python run.py --mode simulate --world <world> --days 3 `
  --community-notice "2026-09-12|Planned outage|The community will have a planned 4-hour outage this Saturday"
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 182 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| Prompt 渲染 `{community_notice}`（s1） | 哨兵出现、占位符消失 |
| `unittest discover -s tests` | **Ran 182 tests — OK**（轮前 181 + 本轮 1） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（仅静态/单元验证，未真调）。

## 7. 反思与限制

- 与 news 事件共用解析与持久化，但注入**不同占位符**（news→`world_news` 于 s1/s4；notice→`community_notice` 于 s1），
  保持两类信号可区分。
- **尚未真调验证**；公告注入的端到端确认属后续 L2（与 news 冒烟同法），本轮不烧 token。
- 属能力恢复基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **一个 L2 事件效果实验**（token-gated，需设计）：同日 `heatwave` vs 无事件、2–3 天、单户，
   用 `analyze_event_response.py` 对比（注意 LLM 随机性，解读需谨慎）；
2. 触发 R1 "Out→通勤"重写分支的真实样本；
3. `compare_worlds.py` / `population_runner.py` 恢复或 guide 校正。
