# R063 — cold_snap 跨户复现：采暖启用 2/3（方向一致但未显著）

- **轮次**：Round 63
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002 cold_snap；baseline 复用 `nw_ctl`；~8 calls）
- **结论**：⚠️ **方向一致但未显著**：baseline 采暖 **0/3** vs cold_snap **2/3**（Fisher 单侧 p=0.20）

---

## 1. 目标

R062 在 world_838587 house_0002（n=1）看到 cold_snap 启用采暖（+158%）。本轮在第二世界增样，
检验 cold_snap 是否如热浪那样稳健。

## 2. 设计（可复现）

```powershell
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 `
  --env nw_cold --event-template "2026-09-11|cold_snap" --workers 1
# baseline 复用 nw_ctl（同户/成员/日，无政策无事件）
```

采暖 = `SpaceHeater` + `AirConditioner` 分项 kWh（>0 记为启用）。

## 3. 结果

| 世界/住户/成员 | baseline 采暖 kWh | cold_snap 采暖 kWh | 启用 |
|---|---|---|---|
| w838 h002M1 | 0.000 | **10.200**（SH 3.0 + AC 7.2） | ✓ |
| w172 h002M1（Low） | 0.000 | **0.000** | ✗ |
| w172 h002M2（Medium） | 0.000 | **12.000**（SH 12.0） | ✓ |

**汇总**：baseline **0/3**；cold_snap **2/3**。
**Fisher 精确检验（0/3 vs 2/3）：单侧 p = 0.20 → 不显著。**

## 4. 解读

- **方向一致**：baseline 采暖恒 0，cold_snap 多数启用（且效应量大：10–12 kWh，总量 +134~158%）；
- **但不如热浪稳健**：热浪 9/10，cold_snap 仅 2/3——**启用概率较低**（w172 M1 未采暖），
  n=3 下未达显著；
- **个体/意识异质性**：未采暖的 w172 M1 为 **Low**，采暖的 M2 为 **Medium**（与 RQ3 方向一致）；
- **与 R058 一致**：cold_snap 属**大效应但非确定性**，需更多样本才能判定。

## 5. token 消耗（估算）

- 1 个 cold_snap run × (4 步 × 2 成员 × 1 天) ≈ **8 次调用**。

## 6. 论文更新

- `paper/experiments/event_cold_snap.md`：第 5 节更新为跨户样本（0/3 vs 2/3），结论降级为"方向一致、未显著、需更多样本"。

## 7. 结论与下一步

cold_snap 是**大效应但异质**的信号（与热浪对比：9/10 vs 2/3），需扩样方能显著。
下一步可继续扩样（更多含采暖设备的住宅），或转向其它大效应信号。
