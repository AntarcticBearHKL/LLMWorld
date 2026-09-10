# R064 — cold_snap 扩样：采暖启用 0/5 vs 3/5（p≈0.083，仍未显著）

- **轮次**：Round 64
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0003 M1/M2，both arms；~16 calls）
- **结论**：⚠️ **方向一致但未达显著**：baseline 采暖 **0/5** vs cold_snap **3/5**（Fisher 单侧 p≈0.083）

---

## 1. 目标

R062/R063 的 cold_snap 采暖启用为 2/3（未显著）。本轮在 `world_172148 house_0003`（含采暖设备，
5 人）增样 Member 1/2，扩大样本。

## 2. 设计（可复现）

```powershell
python run.py --mode simulate --world world_172148 --house house_0003 --member 0 --days 1 --env h3m1_ctl --workers 1
python run.py --mode simulate --world world_172148 --house house_0003 --member 0 --days 1 --env h3m1_cold --event-template "2026-09-11|cold_snap" --workers 1
python run.py --mode simulate --world world_172148 --house house_0003 --member 1 --days 1 --env h3m2_ctl --workers 1
python run.py --mode simulate --world world_172148 --house house_0003 --member 1 --days 1 --env h3m2_cold --event-template "2026-09-11|cold_snap" --workers 1
```

采暖 = `SpaceHeater + AirConditioner` 分项 kWh（>0 记为启用）。

## 3. 结果（累计样本）

| 世界/住户/成员 | baseline 采暖 | cold_snap 采暖 | 启用 |
|---|---|---|---|
| w838 h002M1 | 0.000 | 10.200 | ✓ |
| w172 h002M1 | 0.000 | 0.000 | ✗ |
| w172 h002M2 | 0.000 | 12.000 | ✓ |
| w172 h003M1 | 0.000 | 9.000 | ✓ |
| w172 h003M2 | 0.000 | 0.000 | ✗ |

**汇总**：baseline **0/5**；cold_snap **3/5**。
**Fisher 精确检验（0/5 vs 3/5）：单侧 p ≈ 0.083 → 未达 0.05（边缘）。**

## 4. 解读

- **方向一致**：baseline 采暖恒 0；cold_snap 启用率 **3/5（60%）**——**低于热浪的 9/10（90%）**；
- **边缘显著**（p≈0.083）：更大的样本可能达到显著，但当前不足；
- **异质性**：3/5 启用、2/5 未启用；效应量大（9–12 kWh）但概率性；
- 与热浪对比明确：**同为环境事件，热浪的采暖/制冷响应远比 cold_snap 稳健**（可能与"冷→多穿衣服"等
  替代行为、或模型对制冷 vs 采暖的先验差异有关）。

## 5. token 消耗（估算）

- 本轮 4 个 run × (4 步 × 1 成员 × 1 天) ≈ **16 次调用**。

## 6. 论文更新

- `paper/experiments/event_cold_snap.md`：更新为 0/5 vs 3/5（p≈0.083）；
- `paper/README.md`：状态更新。

## 7. 结论

cold_snap 是**方向一致、效应大、但启用概率较低**的事件信号（3/5，p≈0.083）；
与热浪（9/10，p≈0.0004）形成鲜明对比，是"**不同事件、不同稳健性**"的实证例证。
