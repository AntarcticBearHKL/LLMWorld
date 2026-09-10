# R015 — 事件↔天气联动（修复 R014 发现的不一致）

- **轮次**：Round 15
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 194/194 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（R014 发现）**：`heatwave` 事件文本称"38C"，但 s4 prompt 的结构化天气字段来自
`weather.get_weather()` 桩函数（春季/温和/20C），**两者冲突**；agent 依据天气字段判定不热，
因此空调全程 `idle`，观测不到热浪效应。

**期望**：预设环境类事件（heatwave/cold_snap）**同时**调整传给 s4 的天气/温度，
使"新闻文本"与"环境字段"一致，消除该可信度缺陷（RQ2/Q3）。

## 2. 依据（先读后做）

- R014 归因（事件-环境不一致是首要可信度问题）。
- `intervention_experiment_guide.md` §5.1（heatwave→AC 激增 / cold_snap→采暖上升）。
- Xia et al. (2026)：disruption 下行为真实性依赖**环境与信号一致**。
- 研究语义红线：仍只通过**文本 + 环境上下文**告知，不硬编码行为。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/news.py` | `parse_event_template_spec` 在事件里记录 `template` 名；新增 `EVENT_WEATHER_EFFECTS`（heatwave→Heatwave/+12、cold_snap→ColdSnap/−10）与 `weather_override_for(active_events)`（合并取最后天气、温度增量求和） |
| `src/engine/weather.py` | `get_weather(date=None, override=None)`：在默认值上应用 `override` 的天气与温度增量 |
| `src/steps/simulate/s4_appliance_decision.py` | `run_step(..., weather_override=None)`；`w = weather.get_weather(date, override=weather_override)` |
| `run.py` | 逐日 `weather_effect = news.weather_override_for(active_events)` 并传给 s4 |
| `tests/test_news.py` | 新增 `WeatherLinkTests`（8 例） |

**行为**：仅**预设**环境事件触发天气联动；自定义事件（无 `template`）不影响天气。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 194 tests - OK
```

覆盖：模板事件带 `template`、自定义事件无 `template`、heatwave/cold_snap 覆盖值、
空/自定义无覆盖、多事件增量合并（Heatwave+12 与 ColdSnap−10 → ColdSnap/+2）、
`get_weather` 应用覆盖、无覆盖等于默认。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 194 tests — OK**（轮前 186 + 本轮 8） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（仅静态/单元验证）。

## 7. 反思与限制

- 该改动**直接影响研究有效性**（避免"事件文本与环境自相矛盾"）；已保留"仅文本注入"红线，
  天气是环境状态而非行为规则。
- **尚未重跑** R014 的 A/B 探针；联动是否真的恢复"热浪→空调上升"需后续 L2（token-gated）确认。
- 依据的是**桩** weather 函数；未来接入真实天气 API 时，应把 override 叠加在真实值上（签名已兼容）。

## 8. 下一步（候选）

1. **R16 重跑探针**：同 R014 设计（或改多人户），确认 weather 联动后空调负荷是否随热浪上升；
2. 触发 R1 "Out→通勤"重写分支的真实样本；
3. `population_runner.py`（peer-nudge/policy-schedule）恢复或 guide 校正。
