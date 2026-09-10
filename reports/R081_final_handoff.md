# R081 — 最终交接（R1–R80）

- **轮次**：Round 81（**0 token**）
- **日期**：2026-09-11
- **用途**：会话最终状态与决策请求；细节见 R075（v8）/R076–R080。

---

## 1. 仓库状态

- **提交**：R1–R80 共 **80** 个 step 提交，全部 push 到 `origin/main`（最新 `40179b7`）。
- **测试**：`tests/` **270/270 全绿**（全离线、mock `SubAgent`）；`compileall` 干净；源码树干净。
- **能力**：guide 全部干预 + news/community（天气联动）+ `--policy-schedule` + `--peer-nudge` +
  `--natural-ev`（opt-in）+ 采样控制 + `compare_worlds.py` + `aggregate_runs.py`；漂移清零。
- **世界**：`world_838587`、`world_172148`、`world_143345`（含 EV）。

## 2. 统计显著结论（核心证据集）

| 结论 | 证据（跨 2 世界） | 双侧 p | 状态 |
|---|---|---|---|
| **热浪 → 空调启用** | baseline AC 0/7 vs heatwave 9/10 | ≈0.0004 | ✅ |
| **封锁 → 外出归零** | baseline Out>0 7/7 vs lockdown 0/7 | ≈0.0006 | ✅ |
| 寒潮 → 采暖启用 | baseline 采暖 0/8 vs cold_snap 4/8 | 0.077 | ⚠️ 仅单侧 0.038 |

## 3. 阴性/不可定论结论

- **TOU 幅度**：方向随采样翻转（R026）；DiD 被对照证伪（R046）。
- **nudge 方向**：小样本 5/5 全负、大样本 3/7 增耗（R048→R054）→ 不稳健；措辞驱动（R040）。
- **nudge_loss**：未复现损失厌恶，反而 +6%（R041）。
- **RQ3 分组差异**：组内方差压倒组间差（R054）。
- **storm 事件**：null（−1.5%<噪声地板，R074）→ **事件类型边界**：仅改变行为结构的事件可判。
- **EV 峰移**：内在天花板（基线及 `--natural-ev` 均 100% 谷期，R076/R077/R080）→ 不可评估。

## 4. 方法学产出

1. **噪声地板**：同配置 3 次总电量 std 1.01 kWh（CV≈12%），极差 +33%（R057）。
2. **单次/单臂不可信**；**功效分析**：文献尺度效应（~3%）需 ~124 run/臂（不可行），仅大效应可判（R058）。
3. **定位**：平台适合**定性/方向、异质性、大效应二值响应**；绝对幅度对齐需大规模平均。

## 5. 论文状态

`00_intro`（两个显著事件）/ `01_method` / `99_discussion`（Threats-to-validity：过度遵从、框架不稳定、
噪声地板、单次不可信、事件类型边界）；`experiments/` 14 个文件（2 显著、1 单侧、若干否定/占位）。

## 6. 需要用户决策 / 建议的下一步

1. **规模**：是否投入大规模多种子平均以升级**幅度**结论（R058 估需 ~3–11 run/臂 for 10–20% 效应；
   文献尺度 ~124 run/臂，不建议）。
2. **EV 实验**：是否**修改 s4 默认 prompt**（当前默认即谷期充电，使 EV 干预失效）——属研究设计。
3. **后续事件**：继续扩样大效应二值事件（低成本、可显著）。

## 7. 复现入口

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v      # 270 全绿
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 --event-template "2026-09-11|heatwave"
python src/analyze/aggregate_runs.py --world world_838587 --house house_0002 --date 2026-09-11 --envs tou_ctl sched_ctl world_838587
```
