# R044 — 论文实验结构补全（占位条目）

- **轮次**：Round 44
- **日期**：2026-09-11
- **验证层级**：L0（**0 token**）
- **结论**：✅ 完成（每个实验清单行现都有对应文件）

---

## 1. 目标

goal.md §7 要求 `paper/experiments/` 中每个实验一个文件；"尚未产生效果时，文件可只保留第 1–4 节（占位），
第 5 节写'待验证'"。此前清单中多个行（subsidy/peak_demand/ev_delay/night_setback/in_home_display/
group_heterogeneity/policy_tradeoffs/peer_nudge）**无对应文件**。本轮补齐。

## 2. 改动

| 文件 | 内容 |
|---|---|
| `paper/experiments/subsidy.md` | RQ2；谷期补贴；基准 Alexeenko & Bitar 2023（30~60% 峰移）；需 EV |
| `paper/experiments/peak_demand.md` | RQ2；需量电费；基准 Escarrega 2025（−10~20%） |
| `paper/experiments/ev_delay.md` | RQ2；EV 延迟激励；性格异质性；需 EV |
| `paper/experiments/night_setback.md` | RQ2；夜间回温；基准 Cabezas-Riviere 2025（采暖 −5~10%） |
| `paper/experiments/in_home_display.md` | RQ2；实时反馈；基准 Monacchi 2015 / Faruqui 2010（3~10% / 10~30%） |
| `paper/experiments/group_heterogeneity.md` | RQ3；分组分化；基准 Costa & Kahn 2010（2~4% vs ~0） |
| `paper/experiments/policy_tradeoffs.md` | RQ2/RQ3；多目标权衡；基准 CoRenew 2026 |
| `paper/experiments/peer_nudge.md` | RQ2；真实邻居均值；**含 R037 初步结果**（+11.6%/−6.6%，不一致） |
| `paper/README.md` | 上述行的状态 → `占位(待跑)`（subsidy/ev_delay 标注"需 EV"） |

## 3. 结果

- `paper/experiments/` 现覆盖清单全部条目；每项含 `1 Research Question / 2 Hypothesis & Expected
  Effect / 3 Experimental Setup / 4 Metrics`，第 5 节 `待验证`（peer_nudge 已填初步）。
- 与 goal.md §7 模板一致。

## 4. 测试 / token

- 无代码改动；既有 **262/262** 单测保持全绿。
- token：**0**。

## 5. 下一步（候选）

1. **多人户实验**（首要）：把 preliminary 结论升格（见 `reports/R042_consolidation_v2.md`）；
2. 需要 EV 的实验（subsidy/ev_delay）先解决"世界无 EV"的数据前提；
3. `--policy-schedule` 真调（习惯黏性）。
