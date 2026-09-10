# R070 — 合并检查点 v7（R1–R69；三个显著事件结论）

- **轮次**：Round 70（检查点；**0 token**）
- **日期**：2026-09-11
- **用途**：定义当前"可发表结论集"与状态，替代 R066。

---

## 1. 仓库与测试

- **提交**：R1–R69，全部 push 到 `origin/main`（最新 `f4f6750`）。
- **测试**：`tests/` **267/267 全绿**；`compileall` 干净；源码树干净（仅 `output/` 未跟踪）。
- **能力**：guide 全部干预 + news/community（含天气联动）+ `--policy-schedule` + `--peer-nudge` +
  采样控制 + `compare_worlds.py` + `aggregate_runs.py`；漂移清零。世界：`world_838587`、`world_172148`。

## 2. 三个统计显著的事件结论（核心证据集）

| 事件 | 机制 | 证据（跨 2 世界） | 显著性 |
|---|---|---|---|
| **热浪 heatwave** | 高温 → 空调启用 | baseline AC **0/7** vs heatwave **9/10** | Fisher 单侧 **p ≈ 0.0004** |
| **寒潮 cold_snap** | 低温 → 采暖启用 | baseline 采暖 **0/8** vs cold_snap **4/8** | Fisher 单侧 **p ≈ 0.038** |
| **封锁 lockdown** | 居家 → 外出归零 | baseline Out>0 **7/7** vs lockdown **0/7** | Fisher 单侧 **p ≈ 0.0003** |

- 均为**大效应/准二值**信号：设备 off→on（热/冷）、外出 有→无（封锁）；
- **稳健性排序**：lockdown（完美分离）≳ heatwave（90%）> cold_snap（50%）；
- **个体异质性**普遍存在（热浪 1/10、寒潮 4/8 未响应）。

## 3. 方法学结论（本工作的重要产出）

1. **噪声地板**：同配置 3 次总电量 7.37/8.19/9.80 kWh → mean 8.45, **std 1.01（CV≈12%）**，极差 **+33%**（R057）。
2. **单次/单臂不可信**：nudge 5/5 全负→大样本 3/7 增耗（R048→R054）；TOU 方向翻转（R026）；
   政策时间线回弹被对照证伪（R045→R046）。
3. **功效分析**：文献尺度效应（~3%）需 ~124 run/臂（不可行）；仅大效应（≥10–20%）可判（R058）。
4. **定位**：平台适合**定性/方向、异质性、大效应二值响应**；绝对幅度对齐需大规模平均。

## 4. 不支持/不可定论

TOU 幅度（采样敏感）；nudge 方向（大样本反例）；RQ3 分组差异（方差压倒）；
nudge_loss 损失厌恶（相反）；幅度性事件效应（噪声淹没）。

## 5. 论文状态

- `00_intro` / `01_method` / `99_discussion`（Threats-to-validity：过度遵从、框架不稳定、噪声地板）。
- `experiments/`：**heatwave / cold_snap / lockdown 显著**；`tou`/`nudge`/`nudge_loss`/`group_heterogeneity`/
  `peer_nudge` 初步或否定；`subsidy`/`peak_demand`/`ev_delay`/`night_setback`/`in_home_display`/
  `policy_tradeoffs` 占位。

## 6. 下一步（可复现入口）

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v      # 267 全绿
# 事件（低成本、可显著）：
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 --event-template "2026-09-11|heatwave"
# 幅度平均（预算巨大）：
python src/analyze/aggregate_runs.py --world <w> --house <h> --date <d> --envs e1 e2 e3
```

**判定**：核心实证目标（事件驱动行为 + 方法学）已达成；大规模幅度 campaign 未启动（R058 判定不可行）。
