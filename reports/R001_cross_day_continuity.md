# R001 — 跨日延续状态（day-boundary carry-over）锁定与提交

- **轮次**：Round 1（永续协议首轮）
- **日期**：2026-09-11
- **验证层级**：L0 + L1（纯本地 / 离线单测，**0 token**）
- **结论**：✅ 通过（30/30 单测绿，compileall 干净）

---

## 1. 目标（现状 → 期望）

**现状**：`--mode simulate --days N` 逐日独立生成每位成员的 s1 宏观计划。日与日之间不传递状态，
因此成员可能在第 N 天 24:00 结束时仍处于 `Out`，第 N+1 天 00:00 却直接出现在家里睡觉
（"瞬移回家"），破坏多日行为连续性。

**期望**：把第 N 天末状态持久化，并在第 N+1 天生成时把"上一日结束时人在哪、在做什么"
以自然语言注入 s1 prompt，并对不可避免的边界做**确定性**修正（用一段 `Out / Commuting home`
补上 00:00–00:45），保证多日活动链连续、无瞬移、无时间空洞。

**性质**：健壮性 / 行为真实度修复，属于 goal.md §5 允许范围（正确性 bug、健壮性），
不新增研究方向、不改变"干预只以自然语言注入"的研究语义。

## 2. 依据（先读后做）

- **研究上下文**：`FIT5216/研究计划.md` §2.3 / §4.2 —— 生成式 agent 依赖 memory–reflection–planning
  的连续性；本修复对应"跨日记忆/状态延续"这一最小工程实现。
- **文献**：Park et al. (2023) *Generative Agents*（agent 需连续记忆流才能产生连贯的长时程行为）；
  Xia et al. (2026) *Empirical Grounding*（行为真实性依赖与真实作息的锚定，逐日断裂会污染
  多日聚合负荷统计）。均为 `RefPaper/README.md` 已收录/研究计划已引用的范围内文献。
- **相关 analyze**：`src/analyze/analyze_weekday.py`、`analyze_behavior_patterns.py`（跨日模式分析；
  连续性缺失会直接污染这些脚本的"工作日/周末"与"行为转移"结果）。
- **代码**：`run.py:run_simulate`、`src/steps/simulate/s1_macro_plan.py`、新增 `src/steps/simulate/day_state.py`、
  `src/prompts/simulate_step1_macro_plan.md`。

## 3. 改动（本轮原子目标：把已在工作树中未提交的连续性子特性补齐并锁定）

工作树此前已含该特性但**未提交**（`?? day_state.py` + `M s1_macro_plan.py` 等）。本轮不改写实现语义，
只做三件事：**审阅 + 离线锁定 + 入库**。

| 文件 | 改动 |
|---|---|
| `src/steps/simulate/day_state.py`（新增） | 末段状态摘要 `end_state`、跨日文本 `carry_over_text`、边界重建 `reconcile_boundary`、`save/load_day_state` |
| `src/steps/simulate/s1_macro_plan.py` | `run_step(..., prev_state=None)`；注入 `carry_over_context`；写盘后保存当日末状态 |
| `run.py` | 多日循环把上一日 `day_state` 读入并对每位成员传入 `prev_state`；打印 `[Continuity]` |
| `src/prompts/simulate_step1_macro_plan.md` | 新增 `{carry_over_context}` 占位符 + 一句"不得从工作地瞬移回家"的约束 |

**边界规则**（`reconcile_boundary`）：仅当上一日以 `Out` 结束、且新一日首段为居家时触发；
用一段 00:00–00:45 的 `Out / Commuting home from work` 覆盖/切分首段，其余段原样透传，
保证 00:00–24:00 无空洞、无重叠；其余情况返回原列表对象（no-op）。

## 4. 测试（严格按 goal.md §4 阶梯，只做 L0/L1）

```powershell
# L0 静态
.venv\Scripts\python.exe -m compileall -q src run.py          # exit=0

# L1 离线单测（mock 掉一切 API；仅纯逻辑 + 本地 prompt 渲染）
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

新增 `tests/test_cross_day_continuity.py`，30 个用例覆盖：

- `_parse_range` / `_is_out` / `_fmt` 的边界与非法输入；
- `end_state` 空/正常/居家结束；
- `carry_over_text` 无状态为空、有状态含成员/地点/活动/"commuting home"；
- `reconcile_boundary`：无前日、前日非 Out、首段已 Out、非法时间 → **对象不变（no-op）**；
  首段切分、超短首段替换、前段留空补洞；**重建后 00:00–24:00 连续无洞**；**不修改输入**；
- `save/load_day_state` 往返、`None` 跳过、缺失/损坏返回 `None`、多文件时 member=None 返回 `None`；
- **Prompt 接线**：`simulate_step1_macro_plan` 渲染后必须含哨兵文本、且不含字面占位符
  `{carry_over_context}`（防止模板漏接导致特性静默失效）。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 30 tests — OK** |

**是否符合预期**：是。特性链路（prompt 注入 + 边界重建 + 状态持久化 + 多日驱动）全部被 L1 锁定。

## 6. token 消耗

- 本轮 LLM 调用次数：**0**；token：**0**（L0/L1）。
- 未触发任何 `--mode world/simulate` 真调，符合"能低就不高"。

## 7. 反思

- **发现**：`git status` 首测显示 2 项、复测显示 11 项，属首次读取的瞬时异常——**教训：提交前必须复测 `git status --porcelain`**。
- 工作树里还有**另一组未提交特性**（Feature B：充电池模型 `BATTERY_KWH/DEFAULT_SOC/charge_deficit_kwh`
  + `load_model` 电池上限/`exclude_families` + `s3_household_build` 的 Big Five/energy_awareness 人格落地与冗余房间去除）。
  本轮**刻意不提交**，留待后续各轮分别离线验证后单独入库，避免"一把梭"把未验证代码混入历史。
- 该特性**属于基础设施/健壮性，不产生可与文献对照的"有效果"结论 → 不进入 `paper/`**，仅入 `reports/`（符合 §6 分流）。

## 8. 可复现命令

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
# 真调验证（待后续轮次、按 L2 预算执行）：
# .venv\Scripts\python.exe run.py --mode simulate --world <world> --days 2 --house house_0001 --member 0
```

## 9. 下一步（候选，留待 Round 2 再定）

1. Feature B1：充电池模型（catalog/base/ev/ebike/phone/load_model）离线单测 → 提交；
2. Feature B2：人格 Big Five/energy_awareness 落地（s3_household_build）离线单测 → 提交；
3. 文档漂移修复：`intervention_experiment_guide.md` 引用的 `population_runner.py` / `engine/news*.py` / `compare_worlds.py` 缺失。
