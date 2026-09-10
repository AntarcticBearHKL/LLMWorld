# R011 — news 注入端到端真调冒烟（L2，最小样本）

- **轮次**：Round 11
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（1 户 × 1 成员 × 1 天；复用已生成世界，避免世界生成 token）
- **结论**：✅ 通过（news 注入 s1 与 s4 prompt 均确认；`events.json` 正确落盘；流程 exit 0）

---

## 1. 目标

R9/R10 恢复了 news 引擎并接线，但**从未真调**。本轮做**最小**端到端冒烟，确认：
`--event-template` → `events.json` → 逐日 `world_news` → s1/s4 prompt 占位符 → 模型真实接收。

## 2. 命令（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0001 --member 0 --days 1 `
  --env news_smoke --event-template "2026-09-11|heatwave"
```

- `--env news_smoke`：输出到独立目录，**不覆盖**原有 baseline 产物；
- 复用 `world_838587`：不触发世界生成；
- `--member 0`：仅 1 位成员。

## 3. 结果（证据）

| 检查 | 证据 |
|---|---|
| `events.json` 落盘 | `output/worlds/world_838587/events.json` 含 heatwave 事件（date/title/content） |
| **s1 prompt 注入** | `.../news_smoke/2026-09-11/house_0001/log/00001_s1_macro_plan.md:189` = `- (2026-09-11) Heatwave warning: A severe heatwave is forecast, ... 38C ...` |
| **s4 prompt 注入** | `.../log/00001_s4_appliance_decision.md:492-493` = `Recent news and events in your area:` + 同上 |
| 流程完整 | 产出 `day_state_Member 1.json`、`s1/s2/s3/s4_*`，`run exit=0` |
| 决策修复 | `[Repair] segments=18 ops kept=15/15 repaired=0 dropped=0 valid=True` |
| 跨日状态 | `day_state_Member 1.json` 写入（R1 机理被真实触发） |

## 4. token 消耗（估算）

- 真实 LLM 调用：**4 次**（s1 宏观计划 → s2 协调 → s3 丰富 → s4 家电决策），单成员单日。
- 日志未记录逐轮 token 计数（`ChatLogger` 仅存 prompt/response），故无法精确读数；
  按同规模历史运行，属**最低成本档**。未做任何 L3 大范围验证。

## 5. 结论与限制

- **能力成立**：事件确实以**自然语言**进入 s1/s4（符合"告知 agent、效果涌现"红线）。
- **本轮不是效果实验**：单成员、单日、无对照。要判断"热浪 → 空调负荷上升"是否与
  Xia et al. (2026) 方向一致，需要**反事实对照**（Fidone et al. 2025：同日有/无事件的平行世界），
  且应由 `analyze_event_response.py` 度量——列为后续 L2/L3 实验，不在此冒烟中冒充结论。
- 本轮**未改动源码**（仅新增本报告）→ 无代码提交，符合"每步有 report"。

## 6. 下一步（候选）

1. **事件效果对照实验**：同日 `--event-template heatwave` vs 无事件（两个 env），
   `analyze_event_response.py` 比较负荷/行为转移（需控制随机种子，token 受控）；
2. **触发 R1 重写分支**：构造/寻找 day1 以 `Out` 结束的成员，验证 day2 首段补通勤；
3. `compare_worlds.py` / `population_runner.py` 缺失的恢复或文档校正。
