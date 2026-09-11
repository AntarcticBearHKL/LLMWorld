# R091 — goal.md 重写 + 文档漂移清理 + 论文提级 + output 上传

- **轮次**：Round 91
- **日期**：2026-09-11
- **验证层级**：L0（**0 token**）
- **结论**：✅ 完成用户本轮指示（A1/A2/A3 + goal 更新）

---

## 1. 用户指示

> ① output 需要被上传；② 文档漂移清理；③ A3 论文提级；④ B 全做；⑤ C 可开始；⑥ 跳过 RQ4/RQ1；
> ⑦ 把当前进度和后续计划写进 `goal.md`。

## 2. 改动

| 文件 | 改动 |
|---|---|
| `D:\研究项目\goal.md` | **重写为 v2**：保留永续闭环/硬限制/红线；**新增 §2 当前进度**（91 轮、两个跨 3 世界强显著结论、方法学、能力清单）与 **§3 后续 Backlog**（A/B/C，跳过 RQ4/RQ1）；**§9 更新为“output 需要上传”**（覆盖旧“不入库”） |
| `D:\研究项目\intervention_experiment_guide.md` | **漂移清理**：`population_runner.py`→`run.py`、`engine/news_templates.py`→`engine/news.py`、命令与 `compare_worlds.py` 路径更新；顶部补“能力已全恢复 + 最新结论 + validity”说明 |
| `paper/experiments/event_heatwave.md` | 状态 → **定稿（跨 3 世界 0/9 vs 11/12, 双侧 p≈0.00003）** |
| `paper/experiments/event_lockdown.md` | 状态 → **定稿（13/13→1/13, p≈0.000003；日间 +122%）** |
| `paper/99_discussion.md` | RQ2 顶部新增 **Summary**（两个强显著 + 一个可判幅度） |
| `output/**`（新增 ~1189 文件 / 18.6 MB） | **入库并上传**（世界、模拟、分析产物、events.json） |

## 3. 结果

- `goal.md` 现同时承载**协议**与**当前进度/计划**，后续轮次按 §3 Backlog 执行。
- 指南与实现/结论一致（漂移清零）。
- 论文两个强结论提级为“定稿”。
- output 产物入库上传（不再忽略）。

## 4. 后续（写入 goal.md §3）

- **B（实验，token）**：B1 寒潮扩样（推过双侧 0.05）；B2 占位实验（night_setback/peak_demand/in_home_display/policy_tradeoffs）；B3 更多大效应二值事件。
- **C（campaign，token）**：C1 大规模多种子平均（N≈3–11/臂，`aggregate_runs.py`）；C2 EV prompt 重设计（解 EV 峰移天花板）。
- **不做**：RQ4、RQ1。

## 5. token

- **0**（本轮全为文档与 git）。
