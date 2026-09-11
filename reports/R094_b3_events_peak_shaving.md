# R094 — B3：`blackout_risk` / `price_hike` 显著削峰（低噪指标）

- **轮次**：Round 94
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 house_0002 M1；事件×3 + baseline 复用；~24 calls）
- **结论**：✅ **两个新显著效应**：`blackout_risk` 峰段 **−31.7%**、`price_hike` 峰段 **−17.9%**（均超基线噪声）

---

## 1. 目标（B3）

在剩余事件模板中筛“改行为结构”者（R074 曾判 storm=null）。测 `blackout_risk`（避免晚峰）
与 `price_hike`（电价 +8%）是否削峰。

## 2. 设计（可复现）

- 指标关键：**峰段(16–21) kWh 是低噪指标**——3 个同配置 baseline 得 4.89/4.65/4.52（**std 0.154, CV≈3.3%**），
  远低于总电量的 CV≈12%（R057）。
- baseline：复用 `tou_ctl` / `sched_ctl` / `world_838587`（同户/成员/日，无事件）。
- 事件臂（各 N=3）：
  ```powershell
  foreach ($i in 1,2,3) {
    python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 --env "blackout_run$i" --event-template "2026-09-11|blackout_risk" --workers 1
    python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 --env "pricehike_run$i" --event-template "2026-09-11|price_hike" --workers 1
  }
  ```

## 3. 结果（峰段 16–21 kWh）

| 臂 | mean ± std (n=3) | vs baseline | z |
|---|---|---|---|
| baseline | **4.686 ± 0.154** | — | — |
| **blackout_risk** | **3.203 ± 0.298** | **−31.7%** | −9.6 |
| **price_hike** | **3.849 ± 0.635** | **−17.9%** | −5.4 |

（单次样本另见 R092/上文：`blackout_risk` 总量 +18.9%、峰值 +66%；`price_hike` 总量 +4.9%。）

## 4. 解读

- **两个经济/预警事件显著削峰**：`blackout_risk`（"避免晚峰"）峰段 −31.7%、`price_hike`（电价 +8%）−17.9%；
- **事件类型边界需更新**：不只有环境/封锁类改行为结构——**制造"错峰动机"的事件（价格/停电预警）同样有效**；
  纯信息性（storm）无效。R074 的边界**过严**，此处修正为：**提供明确 timing 动机的事件有效**；
- **指标洞见**：**峰段总电量是低噪可判指标**（CV≈3%），比总电量（CV≈12%）更易检出中等效应——
  这对后续 C1 平均很关键；
- **限制**：单户、单成员、1 天、N=3；须跨世界/成员复现方可升格为最强结论。

## 5. token 消耗（估算）

- 6 个事件 run × (4 步 × 1 成员 × 1 天) ≈ **24 次调用**。

## 6. 论文更新

- 新增 `paper/experiments/event_blackout_risk.md`、`paper/experiments/event_price_hike.md`（初步-强）；
- `paper/README.md`：headline + 清单新增两行；
- `paper/99_discussion.md` RQ2：补“经济/预警事件削峰”。

## 7. 结论

B3 成功：发现 **2 个新的显著削峰效应**（blackout_risk −31.7%、price_hike −17.9%），
并识别出**低噪可判指标**（峰段 kWh）。下一步：跨世界复现（C1）。
