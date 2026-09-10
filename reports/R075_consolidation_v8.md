# R075 — 合并检查点 v8（终稿状态；R1–R74）

- **轮次**：Round 75（检查点；**0 token**）
- **日期**：2026-09-11
- **用途**：终稿状态（含 R072/R073/R074 更正），替代 R070 v7。

---

## 1. 仓库与测试

- **提交**：R1–R74，全部 push 到 `origin/main`（最新 `37ff265`）。
- **测试**：`tests/` **267/267 全绿**；`compileall` 干净；源码树干净（仅 `output/` 未跟踪）。
- **能力**：guide 全部干预 + news/community（天气联动）+ `--policy-schedule` + `--peer-nudge` +
  采样控制 + `compare_worlds.py` + `aggregate_runs.py`；漂移清零。世界：`world_838587`、`world_172148`。

## 2. 可发表结论集（经精确检验校正）

| 结论 | 证据（跨 2 世界） | 单侧 p | **双侧 p** | 判定 |
|---|---|---|---|---|
| **热浪 → 空调启用** | baseline AC 0/7 vs heatwave 9/10 | 0.00041 | **0.00041** | ✅ 显著 |
| **封锁 → 外出归零** | baseline Out>0 7/7 vs lockdown 0/7 | 0.00029 | **0.00058** | ✅ 显著 |
| 寒潮 → 采暖启用 | baseline 采暖 0/8 vs cold_snap 4/8 | 0.038 | 0.077 | ⚠️ 方向一致，双侧不显著 |
| storm → 行为改变 | 总量 −1.5%、日间/Out 不变 | — | — | ⚪ 无效（null） |

**事件类型边界**：只有**改变行为结构**（设备需求 or 居家/外出时间）的事件产生可判效应
（热浪/寒潮/封锁）；纯信息性预警（storm）无效。

## 3. 方法学结论

1. **噪声地板**：同配置 3 次总电量 7.37/8.19/9.80 kWh → mean 8.45, **std 1.01（CV≈12%）**，极差 +33%（R057）。
2. **单次/单臂不可信**：nudge 小样本 5/5 全负→大样本 3/7 增耗（R048→R054）；TOU 方向翻转（R026）；
   政策时间线回弹被对照证伪（R045→R046）。
3. **功效分析**：文献尺度效应（~3%）需 ~124 run/臂（不可行）；仅大效应（≥10–20%）可判（R058）。
4. **框架/措辞**：nudge 效应由规范性措辞驱动（R040）；损失框架未复现（R041）→ 措辞主导。

## 4. 不支持/不可定论

TOU 幅度；nudge 方向（大样本反例）；RQ3 分组差异（方差压倒）；nudge_loss 损失厌恶（相反）；
寒潮（仅单侧）；幅度性事件效应（噪声淹没）。

## 5. 论文状态

- `00_intro`（两个显著事件）/ `01_method` / `99_discussion`（Threats-to-validity：过度遵从、框架不稳定、
  噪声地板、单次不可信）；文本内部一致。
- `experiments/`：**heatwave / lockdown 显著**；`cold_snap` 单侧；`tou`/`nudge`/`nudge_loss`/
  `group_heterogeneity`/`peer_nudge` 初步或否定；`subsidy`/`peak_demand`/`ev_delay`/`night_setback`/
  `in_home_display`/`policy_tradeoffs` 占位。

## 6. 下一步（唯一关键路径）

1. **大效应二值/事件**可继续扩样（低成本、可显著）；
2. **幅度性结论**需按 R058 的 N 做多种子平均（预算巨大）；
3. 含 EV 的世界以运行 `subsidy`/`ev_delay`。

## 7. 复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v      # 267 全绿
python src/analyze/aggregate_runs.py --world world_838587 --house house_0002 --date 2026-09-11 --envs tou_ctl sched_ctl world_838587
```
