# R071 — 论文一致性修订（对齐三个显著结论）

- **轮次**：Round 71（**0 token**）
- **日期**：2026-09-11
- **结论**：✅ 论文文本与最新证据一致

---

## 1. 目标

R059–R069 产生了**三个统计显著的事件结论**（热浪/寒潮/封锁），但论文部分文本仍写"preliminary
heatwave"、Limitations 仍称 heatwave 为 "single-household (n=1)"、Next steps 仍提"restore
population_runner"——均已过时。本轮做一致性修订。

## 2. 改动

| 文件 | 改动 |
|---|---|
| `paper/00_intro.md` | 贡献 #3 由"preliminary replicated heatwave"改为列出**三个显著事件结果**（热浪 p≈0.0004 / 寒潮 p≈0.038 / 封锁 p≈0.0003，跨 2 世界） |
| `paper/99_discussion.md` | Limitations：删除过时的"heatwave n=1"条目，改为"事件结论为二值/大效应；连续幅度受噪声地板（CV≈12%）限制，文献尺度幅度不作声明" |
| `paper/99_discussion.md` | Next steps：改为（1）扩展显著事件集 + `analyze_event_response`；（2）幅度需大规模平均（高预算）；（3）生成含 EV 的世界 |

## 3. 结果

- 论文（intro/discussion）与实验条目（heatwave/cold_snap/lockdown 的 README 状态）**内部一致**。
- 既有 **267/267** 单测不受影响。

## 4. token

- **0**。

## 5. 当前"可发表结论集"

- **三个显著事件**：热浪→制冷（0/7 vs 9/10, p≈0.0004）、寒潮→采暖（0/8 vs 4/8, p≈0.038）、
  封锁→居家（7/7→0/7, p≈0.0003），均跨 2 世界；
- **方法学**：噪声地板 CV≈12%、单次不可信、功效分析（文献尺度幅度不可行）。
