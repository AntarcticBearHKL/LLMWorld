# R050 — 分析工具在真实产物上的复核（RQ3 工具链，0 token）

- **轮次**：Round 50
- **日期**：2026-09-11
- **验证层级**：L0（读取已有分析产物；**0 token**）
- **结论**：✅ 工具链可跑通；⚠️ 现有世界 `world_838587` 的 awareness 分组**退化**（R8 修复前生成）

---

## 1. 目标

R6/R13/R18 已为分析层纯函数写了 L1，但**整条分析工具链在真实产物上**是否可用、输出是否有意义，
尚未核对。本轮读取 `world_838587` 既有 `analysis/` 产物（0 token）复核。

## 2. 观察结果

| 产物 | 关键内容 | 判读 |
|---|---|---|
| `groups_awareness.json` | labels 两户均 `"Medium"`；`groups=[{Medium,2,14.258}]` | **退化为单组** |
| `policy_tradeoffs.json` | 仅 baseline；`peak_to_mean=4.64` | 无政策场景（未跑政策臂） |
| `population_baseline.json` | 2 户，总 29.69 kWh，均值 14.84；`by_awareness` 全 Medium；`big_five_corr` 全 null | 汇总正确；相关性因单组/聚合为 null |
| `behavior_load_baseline_latest.json` | 2 户全 consistent，0 anomaly；house_0001 raw 16.207 vs behavior 13.717；house_0002 13.482 vs 11.992 | **验证 R2 的 `exclude_families` 生效** |

## 3. 结论

- **工具链可用**：`analyze_groups` / `analyze_policy_tradeoffs` / `analyze_population` /
  `analyze_behavior_load` 均能在真实世界产物上产出结构化结果。
- **两个已验证事实**（来自真实数据）：
  1. `exclude_families` 行为可归因负荷正确（raw > behavior，差额≈恒定/充电类负载），佐证 R2；
  2. awareness 分组在当前世界**退化**——因为 `world_838587` 生成于 **R8 修复之前**（`Energy level` 全 Moderate → 全 Medium）。
- **含义**：要做 **RQ3 群体异质性实验**，必须用**修复后的代码重新生成世界**（awareness 构念化生效），
  现有 `world_838587` 不适用于按 awareness 分组。

## 4. token 消耗

- **0**（仅读取既有 JSON）。

## 5. 下一步（候选）

1. **重新生成一个小世界**（`--mode world --count 3~5`，token 中等）以启用 awareness 分组，
   再做 RQ3 分组实验——这是 RQ3 的前置条件；
2. 或接受当前"描述性异质性"（R048/R049 已观察到个体差异），不做严格分组。
3. 其余实验中需要 EV 的（subsidy/ev_delay）同样需要"生成含 EV 的世界"。
