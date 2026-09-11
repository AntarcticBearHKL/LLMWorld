# R133 — `solar_incentive`（未来取向信息型）：**null（n=15）**——10 模板覆盖完成

- **轮次**：Round 133
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 h002M1；**交错** baseline×15 + solar_incentive×15；~120 calls）
- **结论**：⚪ **null**：峰段 −13.2%（t=−1.95, **p≈0.07, n.s.**）、总电量 +2.3%（n.s.）

---

## 1. 目标

`solar_incentive`（"屋顶光伏补贴公告"）是**唯一未测**的 news 模板。其预期**无即时负荷效应**（面向未来安装）。
测之以**完成 10 模板覆盖**并验证**信息型边界**。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 --env "sb_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env "si_$i" --event-template "2026-09-11|solar_incentive" --workers 1
}
```

## 3. 结果

| 指标 | N | baseline | +solar_incentive | Δ | paired t |
|---|---|---|---|---|---|
| 峰段(16–21) kWh | 9 | 4.087 ± 0.878 | 3.397 ± 0.347 | **−16.9%** | **−2.60（p≈0.031）** |
| 峰段(16–21) kWh | **15** | 3.796 ± 0.952 | 3.294 ± 0.476 | **−13.2%** | **−1.95（p≈0.07, n.s.）** |
| 总电量 kWh | 15 | 8.637 ± 1.308 | 8.832 ± 1.637 | +2.3% | +0.37（n.s.） |

- AC 两臂皆 0（无热浪）；**漂移检验**峰段–次序斜率 −0.025（同对相邻贡献 ≈−0.025，远小于 −0.50）。

## 4. 解读

- **n=9 的"−16.9%（p≈0.031）"扩样后塌缩为 −13.2%（p≈0.07, n.s.）**——**又一次 n=9 不可靠**（同 TOU，R114）；
- **null**：面向**未来安装**的补贴公告**不应**改变当日负荷，观测的 −13% 峰段（边缘、不显著）更可能为**噪声/随机**；
- **完成 10 模板覆盖**（见下表）。

## 5. 十个事件模板全测（汇总）

| 模板 | 类型 | 结果 |
|---|---|---|
| heatwave / cold_snap / lockdown | 结构 | ✅ 有效（3 世界） |
| ac_tax | 靶向价格 | ✅ 有效（峰段 −20~−25%，3 世界） |
| rebate | 通用价格 | ⚪ 降耗不削峰 |
| energy_crisis / storm / solar_incentive | 信息型 | ⚪ null |
| blackout_risk / price_hike | 连续削峰 | ❌ 撤回（漂移伪影） |

## 6. 论文更新

- README 清单加 `solar_incentive`（null）；**事件模板覆盖 10/10 完成**。

## 7. token 消耗（估算）

- 30 个 run × 4 步 ≈ **120 次调用**。

## 8. 结论

`solar_incentive` = **null**（n=15：峰段 −13.2% n.s.）。**10 模板覆盖完成**；
信息型/未来取向事件在 LLM 代理上**不改变当日负荷**，与 `energy_crisis`/`storm` 一致。
