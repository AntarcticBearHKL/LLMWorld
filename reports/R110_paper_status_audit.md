# R110 — 论文状态一致性审计与修复（README ↔ 实验文件）

- **轮次**：Round 110
- **日期**：2026-09-11
- **验证层级**：L0（**0 token**）
- **结论**：✅ 修复 5 处状态不一致（README 3 行 + 实验文件 2 处状态头）

---

## 1. 目标

对 `paper/README.md` 实验清单与 `paper/experiments/*.md` 实际状态做**交叉审计**，修正漂移。

## 2. 发现的不一致（审计）

| 文件 | 问题 | 应为 |
|---|---|---|
| `experiments/peak_demand.md` | 状态头仍写"占位（待验证）"，但第 5–8 节**已填** R092 null | **null（N=3 交错）** |
| `experiments/group_heterogeneity.md` | 状态头仍写"占位（待验证）"，但第 5 节**已填** R053/R054 | **不可定论（方差压倒）** |
| `README.md` peak_demand | "占位(待跑)"（已跑 R092） | null(N=3交错) |
| `README.md` night_setback | "占位(待跑)"（已跑 R099） | null(单例) |
| `README.md` policy_tradeoffs | "占位(待跑)"（已跑 R102） | 工具可用/TOU混杂 |

## 3. 修复

- `peak_demand.md` / `group_heterogeneity.md`：更新**状态头**（正文已正确）；
- `README.md`：更新 peak_demand / night_setback / policy_tradeoffs 三行状态；
- **保留** `ev_delay` / `subsidy` 为"占位（待验证）"（确需 EV，未跑；README 一致）。

## 4. 复核
- 全库 grep：仅剩 `ev_delay`/`subsidy` 两处"占位"，均为**真·待跑**，正确。

## 5. token 消耗
- **0**（纯审计/编辑）。

## 6. 结论
README 清单现与 17 个实验文件状态**逐行一致**。
