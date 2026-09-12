# R160 — 交接（Handoff）：暂停于 R159，状态已同步 goal.md

- **轮次**：Round 160（交接；**0 token**）
- **日期**：2026-09-12
- **用途**：用户令"先暂停、同步 goal、便于新窗口无缝继续"。本报告为**仓库内**交接记录；
  完整版见仓库外 `D:\研究项目\goal.md`（v3，含 QUICK RESUME + Backlog）。

---

## 1. 仓库状态（新窗口先核对）
- `D:\研究项目\LLMWorld`，分支 `main`，**HEAD `e8fa827`**，**与 `origin/main` 同步**（曾遇网络中断，已恢复）。
- 测试：`tests/` **272 项全绿**（`.venv\Scripts\python.exe -m unittest discover -s tests`）。
- 规模：**155 份 report**（`reports/R001–R160`）；`paper/` = README + 00/01/02/99 + 18 个 `experiments/*.md`。
- 源码树干净；`output/` 已入库。

## 2. 结论摘要

### 四个 headline（跨 3 世界）
热浪→AC（0/9 vs 11/12, p≈3e-5）；封锁→Out 归零（13/13→1/13, p≈3e-6）+ 日间 +220.7%（same-era n=9）；
寒潮→采暖（0/10 vs 6/10, p≈0.011）；**空调峰税 ac_tax→削峰**（AC 15/15→7/15, p≈0.0022；峰 −22.5%/−24.6%/−20.6%，合并 p≈1e-7）。

### 机制
1. **剂量律**：削峰 ∝ 设备峰段负荷 × 行为改变率（三世界剂量-反应）。
2. **可替代性约束**：靶向电磁炉 −99.7% → 烤箱/微波炉替代 → 总峰 −0.2%（R144/R149）。
3. **设备+窗口联合锚定**：`ac_tax` 削峰；通用晚峰税反升 +18.9%、炊具税 null（R156/R157）。
4. **晚峰由烹饪主导**（27–54%，R151）→ 烹饪主导峰段抵抗削峰。
5. **节能 ≠ 削峰**。

### 主要 null / 撤回 / 世界特异
TOU（n=15 null，小样本假象）；storm（n=15 null）；`in_home_display`/`peak_demand`/`night_setback`（same-era null）；
`energy_crisis`/`solar_incentive`（信息型 null）；`blackout_risk`/`price_hike`（**撤回**，漂移伪影）；
通知效应（+11~21%）= **世界特异**（R146 跨世界不复现）。

## 3. 方法学红线（4 条）
1. 连续指标**跨时段漂移** → **same-era**；优先二值/结构（R104/R106）。
2. 连续幅度 **n<15 不可信**（TOU/solar/storm 均 9→15 塌缩，R114）。
3. 机制/结论须**跨世界**检验（R128/R146）。
4. **注入路径混淆**：自定义 `--event` 通用事件在 world_838587 h002 抬升负荷（+11~21%）；preset 不抬升（R157/R159）。
- 噪声地板 CV≈12%（R057）；文献 ~3% 不可行（R058）。

## 4. 待续（Backlog，详见 goal.md §3）
- **B-x1** 替代效应**跨世界**：world_172148 h001 **跑全 5 成员**（此前只跑 M1 → 该户烹饪不在 M1 峰段）。
- **B-x2** 生成 **≥5 天**世界 → N8（工作日/周末）、季节、`analyze_forecast`。
- **B-x3** 澄清 `--event` vs `--event-template` 同内容差异（路径伪影？）。
- **B-x4** 不可替代设备（热水器短时/EV）**高剂量**检验剂量律。
- 不做：RQ4/RQ1（用户指示）。

## 5. 快速命令
```powershell
cd D:\研究项目\LLMWorld
.venv\Scripts\python.exe -m unittest discover -s tests     # 272 OK
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 `
  --date 2026-09-11 --days 1 --env <env> --event-template "2026-09-11|heatwave" --workers 1
```
> **务必显式 `--date`**（会话跨午夜，默认日期会变）。

## 6. token
- **0**（交接）。

## 7. 结论
**暂停于 R159**；状态同步至 `goal.md`(v3) 与本报告；**新窗口可按 QUICK RESUME 无缝继续**。
