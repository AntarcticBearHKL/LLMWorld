# R021 — 论文初稿骨架（intro / method / discussion）

- **轮次**：Round 21
- **日期**：2026-09-11
- **验证层级**：L0（**0 token**）
- **结论**：✅ 完成（`paper/` 章节骨架建立）

---

## 1. 目标

goal.md §7 要求 `paper/` 具备章节结构（`00_intro.md`、`01_method.md`、`99_discussion.md`）。
此前只有 `README.md` 与 `experiments/`；本轮补齐这三章**草稿**骨架，把已有实现与初步结果归位。

## 2. 依据

- `paper/README.md`（实验清单与模板，R001 建立）。
- `FIT5216/研究计划.md` §4.1（RQ1–RQ4）、§4.2（架构）、§2.7（实证基准）。
- 当前代码现状（`run.py`、`src/steps/*`、`src/engine/*`、`src/analyze/*`）与 R001–R020 成果。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `paper/00_intro.md`（新增） | 定位、RQ1–RQ4、贡献草稿、指向研究计划 |
| `paper/01_method.md`（新增） | 系统总览（world/simulate 两模式 s1–s4）、领域模型（28 家电/4 基类/电池上限）、行为→负荷管线（含跨日延续）、异质性参数、自然语言干预面、分析工具、成本纪律 |
| `paper/99_discussion.md`（新增） | 按 RQ1–RQ4 汇总已实现/已验证/待办；记录**热浪初步结果（2 窗口复现）**与限制；下一步 |
| `paper/README.md` | 章节状态 `待写` → `草稿` |

## 4. 测试

本轮为文档，无代码测试。既有测试仍全绿（上一轮 206/206）。

## 5. 结果

- `paper/` 现为：`README.md`（清单）+ `00_intro.md` + `01_method.md` + `99_discussion.md` +
  `experiments/event_heatwave.md`（初步有效果）。
- 与 goal.md §7 建议结构一致。

## 6. token 消耗

- LLM 调用：**0**（写作文档，未真调）。

## 7. 反思

- 草稿刻意保持**保守**：仅把**已有证据**（尤其 2 窗口复现的热浪）写入 discussion，
  其余标注 pending，避免过度声称。
- 属论文初稿进度；尚无新的实验结论，故 `99_discussion` 主要汇总而非新增发现。

## 8. 下一步（候选）

1. **多人户/多种子热浪复现**（token-gated），升格 event_heatwave 结论；
2. 定价（TOU/subsidy）效果实验对照基准；
3. `population_runner.py`（peer-nudge / policy-schedule）恢复或正式废弃。
