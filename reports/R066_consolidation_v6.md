# R066 — 合并检查点 v6（R1–R65；两个显著结论 + 方法学）

- **轮次**：Round 66（检查点；**0 token**）
- **日期**：2026-09-11
- **用途**：定义当前状态与"可发表结论"，替代 R047/R058 的旧状态。

---

## 1. 仓库与测试

- **提交**：R1–R65，全部 push 到 `origin/main`（最新 `3ac6595`）。
- **测试**：`tests/` **267/267 全绿**（全离线、mock `SubAgent`）；`compileall` 干净。
- **能力**：guide 全部干预 + news/community + `--policy-schedule` + `--peer-nudge` + 采样控制 +
  `compare_worlds.py` + `aggregate_runs.py`；漂移清零。新世界 `world_172148`（awareness 非退化）。

## 2. 两个统计显著结论（核心）

| 结论 | 证据 | 显著性 |
|---|---|---|
| **热浪 → 空调启用** | baseline **0/7** vs heatwave **9/10**（跨 2 世界） | Fisher 单侧 **p ≈ 0.0004** |
| **寒潮 → 采暖启用** | baseline **0/8** vs cold_snap **4/8**（跨 2 世界） | Fisher 单侧 **p ≈ 0.038** |

- 二者均为**大效应二值**信号（设备 off→on）；**热浪更稳健（90%）** 于 **寒潮（50%）**；
- 有个体异质性（热浪 1/10、寒潮 4/8 未启用）。

## 3. 方法学结论（本工作的重要产出）

1. **运行间噪声地板**：同配置 3 次总电量 7.37/8.19/9.80 kWh → mean 8.45, **std 1.01（CV≈12%）**，极差 **+33%**（R057）。
2. **单次/单臂不可信**：nudge 小样本 5/5 全负 → 大样本 3/7 增耗（R048→R054）；
   TOU 方向随采样翻转（R026）；政策时间线"回弹"被对照证伪（R045→R046）。
3. **功效分析**：检测文献尺度效应（~3%）需 **~124 run/臂**（不可行）；**只有大效应（≥10–20%）可判**（R058）。
4. **由此定位**：本平台适合**定性/方向、异质性、以及大效应二值响应**；**绝对幅度对齐**需大规模平均。

## 4. 不支持/不可定论的结论

- TOU 幅度（采样敏感）；nudge 方向（大样本反例）；RQ3 分组差异（方差压倒）；
  nudge_loss 损失厌恶（相反方向 +6%）；幅度性事件效应（被噪声淹没）。

## 5. 论文状态

- `00_intro` / `01_method` / `99_discussion`（含 Threats-to-validity：过度遵从、框架不稳定、噪声地板）。
- `experiments/`：**heatwave** 与 **cold_snap** 为显著；`tou`/`nudge`/`nudge_loss`/`group_heterogeneity`/
  `peer_nudge` 为初步或否定；`subsidy`/`peak_demand`/`ev_delay`/`night_setback`/`in_home_display`/
  `policy_tradeoffs` 为占位。

## 6. 下一步（唯一关键路径）

1. **大效应二值/事件**方向可继续扩样（低成本、可显著）——已有两个，可再加（如 storm/blackout_risk）；
2. **幅度性结论**需按 §3 的 N 做多种子平均（预算巨大，暂缓）；
3. 需要 EV 的实验（subsidy/ev_delay）需先生成含 EV 的世界。

## 7. 复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v          # 267 全绿
python src/analyze/aggregate_runs.py --world world_838587 --house house_0002 --date 2026-09-11 --envs tou_ctl sched_ctl world_838587
```
