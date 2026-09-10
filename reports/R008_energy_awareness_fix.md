# R008 — 修复 energy_awareness 分组退化（构念化推导）

- **轮次**：Round 8
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 修复生效（累计 156/156 单测绿，本轮新增 8 项）

---

## 1. 目标（现状 → 期望）

**现状（R7 发现）**：真实运行中 5 位成员的 `energy_awareness` **全部为 "Medium"**。
根因诊断（读取 `persona_rows.json`）：人格行里的 `Energy level` 列取值**几乎恒为 "Moderate"**，
而 `_level_to_awareness("moderate")` 恰映射到 "Medium"——导致
`analyze_groups.py --label-source awareness`（RQ3 异质性，Costa & Kahn 2010）
退化为**单组**，无法展示"同一政策、不同群体分化响应"。

**期望**：把 `energy_awareness` 作为**构念**（对能源的态度 + 尽责性），而非单一的"健康精力"单元格，
恢复群体区分度，同时保持**确定性**与**可分析性**。

## 2. 依据（先读后做）

- `intervention_experiment_guide.md` §3.4：分组实验明确以
  "**energy awareness / high conscientiousness** 的家庭对 nudge 响应更强"为依据。
- `研究计划.md` §2.7 Costa & Kahn (2010)：同一政策在不同价值取向群体响应分化（2–4% vs ~0）。
- 可行字段（persona 库实存且**有区分度**）：`Attitude: Renewable energy` / `Attitude: Climate action`
  （Opposed/Skeptical/Neutral/Positive/Enthusiast）、`BFI-2 Conscientiousness`（Very low…Very high）、
  `Energy level` / `BFI-2 Energy Level`。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/steps/world/s3_household_build.py` | 新增 `ATTITUDE_ENERGY_SCORES`、阈值常量、`_score_attitude`、`_row_energy_awareness`；`_apply_personality` 改用 `_row_energy_awareness`（替代仅取 `Energy level`） |
| `tests/test_personality_rooms.py` | 新增 `RowEnergyAwarenessTests`（8 例） |

**构念公式**（确定性）：`composite = mean(可用分量)`，分量依次为
① 能源态度（优先 `Attitude: Renewable energy`，缺失用 `Attitude: Climate action`）
② `BFI-2 Conscientiousness` ③ `Energy level`（缺失用 `BFI-2 Energy Level`）。
分档：`<0.4 → Low`，`<0.65 → Medium`，否则 `High`；无任何分量返回 `None`（回退 portrait）。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 156 tests - OK
```

新增用例：高分组合→High、低分组合→Low、仅 Energy level Moderate→Medium、回退 BFI-2 Energy Level、
**可再生能源态度优先于气候态度**、无分量→None、**尽责性在 Energy level 恒定时提供方差**、态度分映射。

## 5. 真实数据验证（0 token，复用 world_838587 persona 行）

| 房 | 旧标签 | 新标签 |
|---|---|---|
| house_0001 | Medium ×4 | **Low, Medium, Low, Medium** |
| house_0002 | Medium ×1 | Low |

**退化已解除**。旧标签的均匀性正是 `Energy level=Moderate` 造成的。

## 6. 结论与限制

- 修复把 awareness 还原为研究文档定义的构念，恢复分组区分度；**未新增研究方向**。
- 限制：本小样本只出现 Low/Medium，无 High（因 `Energy level` 恒 0.5 拉低均值）；
  更大世界或调整阈值可进一步拉开分布——列为后续观察点，不阻塞。
- 纯逻辑变更，token 0；属分组口径修正，**尚无与文献对照的"有效果"结论 → 仅入 `reports/`**。

## 7. 下一步（候选）

1. 在更大世界（≤5 户）复算 awareness 分布，确认 Low/Medium/High 三档均有样本；
2. 触发 R1 "Out→通勤"重写分支的小样本真调；
3. 文档漂移修复（`population_runner.py`/`engine/news*.py`/`compare_worlds.py`）。
