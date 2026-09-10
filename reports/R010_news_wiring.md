# R010 — 接线 news 引擎到 run.py/s1/s4（事件注入可用）

- **轮次**：Round 10
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 181/181 单测绿，本轮新增 2 项；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（R9 遗留）**：`engine/news.py` 已实现，但 `world_news` 占位符仍被硬编码为 `""`，
`run.py` 无 `--event`/`--event-template`，事件无法真正注入 prompt。

**期望**：打通 `CLI → events.json → 逐日 world_news → s1/s4 prompt` 全链路，
使 guide §5 的事件实验可运行，且**只以自然语言**告知 agent（不硬编码行为）。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §5.1/§5.2（10 模板 + 自定义事件）。
- `src/analyze/analyze_event_response.py`：读取 `output/worlds/<world>/events.json` 对齐日期。
- 研究语义红线（goal.md §5）：事件只注入文本，效果必须涌现。
- 上一轮 R009（模板/选择/渲染/持久化）+ R001（s1 prompt 已有 `{world_news}` 占位符）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `run.py` | `from engine import news`；`run_simulate(..., events=None)` 写入 `events.json`；逐日计算 `day_news=render(events_for_date(...))` 并传给 s1/s4；新增 `--event`/`--event-template`（可重复），解析失败打印并返回 1 |
| `src/steps/simulate/s1_macro_plan.py` | `run_step(..., world_news="")`；Prompt 传 `world_news=world_news` |
| `src/steps/simulate/s4_appliance_decision.py` | `run_step(..., world_news="")`；Prompt 传 `world_news=world_news` |
| `tests/test_news.py` | 新增 2 项：s1/s4 模板渲染 `{world_news}` 哨兵 |

**用法**：
```powershell
python run.py --mode simulate --world <world> --days 3 `
  --event-template "2026-09-11|heatwave" `
  --event "2026-09-12|Subsidy cancelled|The off-peak subsidy ends next month"
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 181 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| Prompt 渲染 `{world_news}`（s1/s4） | 哨兵出现、占位符消失 |
| `unittest discover -s tests` | **Ran 181 tests — OK**（轮前 179 + 本轮 2） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（仅静态/单元验证；未真调）。

## 7. 反思与限制

- 全链路已接线，但**尚未做真实 L2 运行**（任何真调都会消耗 token）；事件是否产生与文献方向一致的
  涌现响应，需后续 L2 小范围（单户 × ≤3 天）验证——这属于"必须最终验证"时才做的步骤。
- `s4_only` 模式也接收 `day_news`（因为 day_news 在分支外计算），事件在 policy 对比中一致生效。
- 能力恢复属基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **L2 事件小样本**（token-gated）：1 户 × 2–3 天 `--event-template "...|heatwave"`，
   用 `analyze_event_response.py` 看事件日行为/负荷偏移是否 > 0；
2. 触发 R1 "Out→通勤"重写分支的小样本真调；
3. `compare_worlds.py` / `population_runner.py` 缺失的同类恢复或文档校正。
