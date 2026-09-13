# R200 — 成本上下文改造：**平台首次出现显著价格移峰**（峰 −7.2% / 谷 +16.6%）

- **轮次**：Round 200（**价格分析能力专项 P1+P2 首次成功**）
- **日期**：2026-09-12
- **验证层级**：**L1**（284 单测全绿，+6）+ **L2 真调**（共享时间线 `--s4-only`；n=15/臂；~30 calls）
- **结论**：✅ **有效果**：给"柔性负荷成本表 + 明确授权移峰"后，**峰段 −7.2%（t=−2.84, p=0.013）、
  谷期 +16.6%（t=+3.15, p=0.007）**，总量 −0.2% n.s. → **典型的"移峰"（peak↓ valley↑）**，
  是**平台迄今唯一显著的价格响应**。

---

## 1. 目标

解决"政策/价格-行为全 null"（前次分析）：核心缺口是 **① 无成本数字、② 价格未具体到设备/动作**。
本轮实现并检验 **成本上下文（cost context）**：

- 新增 `src/engine/tariff.py`：由 tariff（峰/谷费率+窗）+ 住户柔性设备 → **每台设备"现在 vs 谷段"的金额表**；
- `policy.parse_tariff()` 输出结构化费率；`run.py --cost-context` 开关；s4 prompt 增 `{cost_context}` 占位 + 决策原则 12。

## 2. 关键迭代（诊断→修正）

| 版本 | 成本表措辞 | 峰段 Δ | 谷期 Δ | 判定 |
|---|---|---|---|---|
| v1 | "schedule at the cheapest feasible time" | −0.1% n.s. | +1.4% n.s. | ⚪ 无效果 |
| **v2** | **"MAY move it to an off-peak segment earlier/later the same day（明确授权移峰）"** | **−7.2%（p=0.013）** | **+16.6%（p=0.007）** | ✅ **有效果** |

- **诊断**：v1 时 18:00 负荷、热水器（2.25 kWh）在两臂**逐字节相同** → agent **不会重排"活动绑定"的柔性负荷**；
- **修正**：成本表**显式授权**把柔性设备移到谷段（活动不变、仅改时间）→ agent 才执行。

## 3. 方法（可复现；共享时间线降噪）

```powershell
# 种子：一次完整 baseline 运行（得到 s1–s3 固定时间线）
# 复制 s1/s2/s3/day_state 到 15 个 arm A 与 15 个 arm B env
# arm A：TOU 文本（无成本表）；arm B：TOU + 成本表
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pctx_a_$i" --policy "tou:0.9,0.18" --s4-only --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pctx_b_$i" --policy "tou:0.9,0.18" --cost-context --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pctx_a --treat-prefix pctx_b --n 15 --tag tou --base-tag tou
```
- **共享同一 s1–s3 时间线** → 消除计划层噪声，只测 s4 决策（政策只注入 s4）。

## 4. 结果（n=15，配对 t）

| 指标 | A（TOU 文本） | B（TOU + 成本表） | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 2.701 | 2.505 | **−7.2%** | **−2.84** | **0.013** |
| **谷期 22–7** | 2.544 | 2.966 | **+16.6%** | **+3.15** | **0.007** |
| 总电量 | 8.975 | 8.956 | −0.2% | −0.10 | 0.92（n.s.） |
| Dishwasher | 0.550 | 0.760 | +38.2% | +3.15 | 0.007（移至谷段） |

注入的成本表示例（`--cost-context`）：
```
Flexible-appliance costs under today's tariff (peak 16:00-21:00 @0.90; off-peak 22:00-07:00 @0.18):
- bedroom_1_airconditioner: 1.80 AUD now (peak) vs 0.36 AUD off-peak — save 1.44 per hour
- kitchen_dishwasher: 0.99 AUD now (peak) vs 0.20 AUD off-peak — save 0.79 per cycle
- bathroom_waterheater: 2.70 AUD now (peak) vs 0.54 AUD off-peak — save 2.16 per hour
```

## 5. 解读（为何这次有效）

1. **成本数字 + 明确授权**把"价格"变成 agent**可执行的取舍**（现在贵 X、谷段省 Y、允许改时间）；
2. **纯移峰**：峰↓、谷↑、总量不变 → 与 `tou` 单臂（R114 null）**质变**，与 Faruqui 纯 TOU（−3~6%）方向一致、幅度（−7.2%）合理；
3. **机制**：不是"价格文本"生效，而是**信息具体化 + 授权动作**——印证前次分析（agent 是"指令/情境响应者"，非经济优化器；给了可执行指令即可响应）；
4. **共享时间线**（s4-only）显著降噪 → 低价差下的移峰才被检出。

## 6. 论文更新
- `paper/99_discussion.md`：新增"**成本上下文使 TOU 移峰可检出（R200）**：峰 −7.2%/谷 +16.6%（p≤0.013）"；
- `paper/README.md`：TOU 行补注"加成本表后移峰显著（R200）"。

## 7. token
- 约 **30 次调用**（s4-only 1 call/run × 30）——**极省**。
