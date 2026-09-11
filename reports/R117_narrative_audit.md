# R117 — 叙事章节一致性审计（00_intro / 01_method）

- **轮次**：Round 117
- **日期**：2026-09-11
- **验证层级**：L0（**0 token**）
- **结论**：✅ 两章与修正后结论**一致**；补 method §7 的 validity controls

---

## 1. 目标

R110 审计了 README/experiments；本轮审计 **`00_intro.md`** 与 **`01_method.md`** 是否与
R104–R116 修正后的结论一致（是否有过时的"削峰/多结论"表述）。

## 2. 审计结果

| 文件 | 检查项 | 结论 |
|---|---|---|
| `00_intro.md` | Contributions #3 是否仍宣称 3 个有效事件 | ✅ 一致（热浪/封锁/寒潮，均与修正后集吻合） |
| `00_intro.md` | 是否残留 blackout_risk/price_hike 削峰表述 | ✅ 无残留 |
| `01_method.md` | §5 干预入口（policy/news）是否与代码一致 | ✅ 一致 |
| `01_method.md` | §7 是否含漂移/小样本红线 | ⬅️ **补入** |

## 3. 改动

- `01_method.md` §7 增补 **Validity controls (R104–R116)**：
  (i) 连续指标须 same-era 对照或用二值信号；
  (ii) 连续幅度 **n<15 不可信**（TOU 3→9→15）；
  (iii) 噪声地板 CV≈12%，仅大效应可判。

## 4. token 消耗
- **0**。

## 5. 结论
`paper/` 的**叙事章（intro/method）与实验章（experiments/discussion）现方法学一致**。
