# R009 — 恢复缺失的 news 引擎（自然语言事件注入，guide §5）

- **轮次**：Round 9
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 179/179 单测绿，本轮新增 23 项）

---

## 1. 目标（现状 → 期望）

**现状（drift）**：`intervention_experiment_guide.md` §5 描述了 10 个新闻事件模板与
`--event`/`--event-template` 注入能力，`analyze_event_response.py` 也会读取
`output/worlds/<world>/events.json`；但**当前 `src/` 中没有 `engine/news.py` / `news_templates.py`**
（重构后缺失 = goal.md §1 记录的文档漂移）。`s1`/`s4` 的 `world_news` 占位符目前被硬编码为 `""`（死代码）。

**期望**：重建**纯自然语言**的事件模板与选择/渲染逻辑（不硬编码任何行为），并给出可被分析脚本消费的持久化格式，
为 RQ2/RQ3 的"事件→行为"实验打基础。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §5.1（10 模板：heatwave/cold_snap/storm/price_hike/energy_crisis/
  ac_tax/rebate/blackout_risk/solar_incentive/lockdown）、§5.2（自定义事件）。
- `研究计划.md` §4.3 Phase Three（社会事件：极端天气/假日/封锁）与 RQ2/RQ3。
- 文献：Xia et al. (2026)（disruption 下的行为真实性）、Fidone et al. (2025)（对照世界因果）。
- `src/analyze/analyze_event_response.py`：事件日期来源 `output/worlds/<world>/events.json`。
- goal.md §5 明确允许修复 `engine/news*.py` 缺失。
- **研究语义红线**：事件文本仅"告知居民"，不含指令式行为（避免 prompt 偏置）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/news.py`（新增） | 10 个模板；`parse_event_spec("date\|title\|content")`、`parse_event_template_spec("date\|模板")`、`parse_events`、`events_for_date`（按日期筛选 + 记忆窗口 `NEWS_MEMORY_KEEP`）、`render_world_news`（自然语言块）、`write/load_events_json` |
| `tests/test_news.py`（新增） | 23 个离线用例 |

**格式**：`events.json = {"events":[{"date","title","content"}]}`，与 `analyze_event_response.py` 的读取一致。
**注入点（占位符已就绪，接线留待 R10）**：s1 `world_news`/`community_notice`、s4 `world_news`。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 179 tests - OK
```

覆盖：10 模板存在且含 title/content；`parse_event_spec`（内容含 `|`、空→None、畸形→ValueError）；
`parse_event_template_spec`（大小写不敏感、未知模板→ValueError）；`parse_events` 合并两类来源并跳过空；
`events_for_date`（过滤未来、保留最近 N、`keep=0` 全返回、忽略坏条目）；
`render_world_news`（空→""、含 date/title/content）；`events.json` 往返 / 缺失 / 损坏。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 179 tests — OK**（轮前 156 + 本轮 23） |

**是否符合预期**：是（模板、解析、选择、渲染、持久化全部锁定）。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思与限制

- 本轮只完成**引擎模块 + L1**；**尚未接线**到 `run.py`/`s1`/`s4`，故当前 `world_news` 仍为空——
  这是刻意的原子切分（下一轮 R10 接线并写 report）。
- 未与并发工作流冲突：`engine/news.py`、`tests/test_news.py` 均为新文件；`s1`/`s4`/`run.py` 本轮未改。
- 属能力恢复基础设施；**事件对行为的"有效果"结论需接线后真调才能产生 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **R10 接线**：`run.py` 增加 `--event`（可重复）/`--event-template`，写入 `output/worlds/<world>/events.json`，
   并在逐日循环把 `render_world_news(events_for_date(...))` 传入 s1 与 s4 的 `world_news`；补 L1；
2. 触发 R1 "Out→通勤"重写分支的小样本真调；
3. `compare_worlds.py` / `population_runner.py` 缺失的同类处理。
