# R007 — 真实运行 world_838587（2 天）产物离线验证（L2 证据，0 额外 token）

- **轮次**：Round 7
- **日期**：2026-09-11
- **验证层级**：L2 证据复用（读取已有真实运行产物；**新增 LLM 调用 0，token 0**）
- **结论**：B2 ✅ / R2 ✅ / R1 部分 ✅（no-op 路径）；并发现一个**分组退化**问题

---

## 1. 背景与目标

一个外部进程此前跑完 `run.py --mode simulate --world world_838587 --days 2`
（2026-09-11 与 2026-09-12，`house_0001` 4 人、`house_0002` 1 人）。
其产物是可复用的**真实链路证据**。目标：在不额外烧 token 的前提下，核对 R1/R2 与本轮 B2 是否在真调中生效。

## 2. 方法（只读，可复现）

用仓库自身代码对真实产物做**离线重算**（不是重跑 LLM）：

- `household.json` → 读 `personality.energy_awareness` / `big_five`（B2）；
- `day_state_*.json`（两日）+ `s1_macro_*.json`（次日首段）→ 连续性（R1）；
- `load_model.build_load_profile(household, decisions)` 对真实 `s4_decisions_*` 重算
  → 充电池上限（R2）与 `exclude_families` 行为口径。

## 3. 结果

### 3.1 B2 人格落地 ✅
`house_0001` 4 人与 `house_0002` 1 人**全部**具备 `energy_awareness` 与完整 5 维 `big_five`，
取值有区分（如 conscientiousness 0.1/0.25/0.9，agreeableness 0.1/0.25/0.8）。字段确实落盘并被读取。

### 3.2 R2 充电池上限 ✅
真实运行中存在的充电设备均为 Phone（无 EV/E-bike），实测：

| 设备 | 电量缺口 kWh | 重算充电 kWh |
|---|---|---|
| member_1_phone | 0.014 | 0.010 |
| member_2_phone | 0.014 | **0.014**（触顶） |
| member_3_phone | 0.014 | 0.0083 |
| member_4_phone | 0.014 | **0.014**（触顶） |

全部 ≤ 缺口；两个恰好落在上限（说明跨界精确缩放生效），其余由 LLM 自律少充。**无越限**。

### 3.3 R1 跨日连续性 ⚠️（仅验证 no-op 路径）
4 位成员的 day1 末状态**均为居家睡眠**（`ends_out=false`，位于各自 Bedroom）。
因此 `reconcile_boundary` 正确地**不改写**，day2 首段为居家睡眠，与 day1 末状态自然衔接。
**遗憾**：本次运行没有成员以 `Out` 结束，**"Out→补通勤"重写分支未在真实数据中触发**
（该分支已由 R1 的 30 项离线单测覆盖）。

### 3.4 行为可归因负荷口径 ✅
`house_0001` day1：`raw_total=17.543 kWh` vs `behavior_total=15.053 kWh`（剔除
EV/E-bike/冰箱/冷柜/路由器后降约 14%），符合"剔除恒定/纯充电负载"的预期方向。

## 4. 发现：`energy_awareness` 分组退化（重要）

本次 5 位成员**全部为 "Medium"**。若该现象普遍，`analyze_groups.py --label-source awareness`
（RQ3 异质性，Costa & Kahn 2010 的"同政策分组分化"）将退化为**单组**，无法展示分化。

可能原因：persona 行 `Energy level` 列取值集中/缺失，回退到 `_portrait_energy_awareness` 亦多为 Medium。
列为**下一轮候选优化点**（在已有研究范围内：分组口径正确性）。

## 5. 结论与限制

- B2 与 R2 在真实链路中**确认生效**；R1 no-op 路径确认，重写路径仅单测覆盖。
- 本轮**未新增任何 LLM 调用**，token 0。
- 属验证证据（未产生"与文献基准对照的有效果结论"）→ **仅入 `reports/`**。

## 6. 下一步（候选）

1. **R8：energy_awareness 分布诊断与修正**——统计 `persona_rows.json` 的 `Energy level` 分布；
   若 `ENERGY_LEVEL_AWARENESS` 映射过窄或列缺失，改为按 BFI/portrait 分位数分档，恢复分组区分度；
2. 触发 R1 重写分支的真实小样本验证（构造 ended-out 的 day1 后看 day2 首段）；
3. 文档漂移修复。
