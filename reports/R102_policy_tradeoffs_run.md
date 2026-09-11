# R102 — `policy_tradeoffs` 实跑（工具可用；TOU 结果混杂）

- **轮次**：Round 102
- **日期**：2026-09-11
- **验证层级**：**L2 真调**（world_838587 全户 1 天 TOU；~20 calls）+ L0 分析
- **结论**：✅ 工具跑通；⚠️ TOU 权衡**混杂/不可定论**（峰值 −9.9% 但峰段 +18.9%、平台 +28.6%）

---

## 1. 目标（B2 收尾）

跑 `policy_tradeoffs`（RQ3 多目标权衡：削峰 vs 负担 vs 平台率），并验证 `analyze_policy_tradeoffs.py`。

## 2. 方法

```powershell
# 将 TOU 注入 world_838587 本体（与 baseline 同目录，policy tag = tou）
python run.py --mode simulate --world world_838587 --days 1 --env world_838587 --policy tou --workers 4
python src/analyze/analyze_policy_tradeoffs.py world_838587
```

## 3. 结果（% vs baseline；越负越好）

| Policy | Total | Peak hrs | Peak | Plateau | P/M |
|---|---|---|---|---|---|
| baseline | — | — | — | — | 4.64 |
| **tou** | **−13.4%** | **+18.9%** | **−9.9%** | **+28.6%** | 4.83 |

- 输出：`output/simulation/world_838587/analysis/policy_tradeoffs.json`；
- 警告：2026-09-12 无 tou 决策（仅跑了 09-11）。

## 4. 解读

- **工具可用**：分析器正常产出权衡矩阵并落盘；
- **TOU 结果混杂**：最大峰值 −9.9%（削峰方向对），但**峰段总电量 +18.9%、平台率 +28.6%**（负担/平台恶化）
  —— 与 R023/R026 的"TOU 采样敏感、方向不稳"一致；
- **不可作为有效结论**；属工具验证 + 初步（混杂）结果。

## 5. token 消耗（估算）

- TOU 注入 5 成员 × 4 步 ≈ **20 次调用**；分析 0 token。

## 6. 论文更新

- `paper/experiments/policy_tradeoffs.md`：第 5 节填初步（混杂）；状态“初步(工具可用,结果混杂)”。

## 7. 结论

B2 占位实验**全部覆盖**（peak_demand/in_home_display/night_setback/policy_tradeoffs）。
`policy_tradeoffs` 工具可用，但 TOU 权衡混杂 → 与"软/价格干预不可判"主线一致。
