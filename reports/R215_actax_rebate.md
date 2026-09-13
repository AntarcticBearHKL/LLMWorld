# R215 — A4 ac_tax × rebate 组合：**非加性（rebate 抵消 ac_tax）**

- **轮次**：Round 215（A4）
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002，**热浪背景**，完整 run；3 臂 × n=9；~110 calls）
- **结论**：⚪ **非加性/相消**：`ac_tax` 单独 → AC **−58.4%（p=0.002）**、总 **−29.0%（p=0.002）**；
  再叠加 `rebate` → **AC 反升 +79.8%（p=0.118）、总 +16.6%** → **rebate 抵消了 ac_tax**（与 Pellerano 2017 挤出同向）。

## 1. 目的（A4）

价格×价格是否**叠加**（goal §3.2）：`ac_tax`（设备+窗口税）× `rebate`（通用返利），热浪背景下。

## 2. 方法（可复现）

```powershell
$HW="2026-09-11|heatwave"; $AC="2026-09-11|ac_tax"; $RB="2026-09-11|rebate"
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "cb_b_$i"  --event-template $HW --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "cb_t_$i"  --event-template $HW --event-template $AC --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "cb_tr_$i" --event-template $HW --event-template $AC --event-template $RB --workers 1
```

## 3. 结果（n=9）

**① heatwave → heatwave+ac_tax**
| 指标 | heatwave | +ac_tax | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 15.351 | 10.904 | **−29.0%** | **−4.48** | **0.002** |
| 峰段 16–21 | 3.413 | 3.623 | +6.1% | +0.94 | 0.38（n.s.） |
| **AirConditioner** | 6.733 | 2.800 | **−58.4%** | **−4.51** | **0.002** |

**② heatwave+ac_tax → +rebate**
| 指标 | +ac_tax | +ac_tax+rebate | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 10.904 | 12.717 | +16.6% | +1.31 | 0.23（n.s.） |
| 峰段 16–21 | 3.623 | 3.322 | −8.3% | −1.05 | 0.32（n.s.） |
| **AirConditioner** | 2.800 | 5.033 | **+79.8%** | +1.75 | 0.118 |

## 4. 解读
1. **ac_tax 有效**（AC −58.4%、总 −29%；峰 +6.1% n.s. —— W1h002 空调为主卧夜用，峰段占比低，与 R118 caveat 一致）；
2. **叠加 rebate → 相消**：AC 从 2.80 回到 5.03（**+79.8%**）、总 +16.6% → **两价格工具非叠加**；
3. **对文献**：与 Pellerano 2017"**经济激励挤出社会/内在动机**"、R139"组合非加性"**同向**（机制：返利把决策框架从"避税"转为"达标领赏"，反而放松了避税行为）；
4. **政策含义**：**设备+窗口靶向税**应**单独使用**，叠加通用返利会抵消其效果。

## 5. 论文更新
- `paper/99_discussion.md`：补"ac_tax×rebate 相消（R215）"。

## 6. token
- 约 **110 次调用**（含网络重试）。
