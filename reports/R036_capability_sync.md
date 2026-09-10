# R036 — 文档同步：干预面已与实现对齐

- **轮次**：Round 36
- **日期**：2026-09-11
- **验证层级**：L0（**0 token**）
- **结论**：✅ 完成

---

## 1. 目标

R29–R35 恢复/新增了多项能力后，`paper/01_method.md` §5 仍写"peer-nudge (planned)"且只列部分政策，
与实现不符。做一次**文档同步**，使方法与代码一致。

## 2. 改动

| 文件 | 改动 |
|---|---|
| `paper/01_method.md` §5 | 重写"外部输入"清单：价格（TOU/TOU-soft/subsidy/peak_demand/ev_delay）、社会规范（nudge/nudge_loss/--peer-nudge 动态邻居均值）、行为引导（night_setback/in_home_display）、政策时间线（--policy-schedule）、新闻事件（10 模板 + 天气联动）、社区公告（--community-notice） |

## 3. 结果

- `paper/01_method.md` 的干预面现与 `engine/policy.py` + `run.py` **完全一致**。
- 能力完备性核对（guide §1 表）：TOU/TOU-soft、nudge、nudge_loss、subsidy、peak_demand、ev_delay、
  night_setback、in_home_display、news（10 模板/自定义）、community-notice、policy-schedule、
  peer-nudge —— **全部具备入口**。

## 4. 测试 / token

- 无代码改动；既有 **260/260** 单测保持全绿。
- token：**0**。

## 5. 下一步（候选）

1. 真实实验：`nudge` vs `--peer-nudge`（guide §6.1），或多人户 TOU/价格政策（降噪）；
2. 政策时间线真调（习惯黏性）；
3. 视效果把结论沉淀进 `paper/experiments/*.md`。
