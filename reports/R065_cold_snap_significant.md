# R065 — cold_snap 达标显著：采暖启用 0/8 vs 4/8（p≈0.038）

- **轮次**：Round 65
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0003 M3/M4/M5，both arms；~24 calls）
- **结论**：✅ **达到显著**：baseline 采暖 **0/8** vs cold_snap **4/8**，Fisher 单侧 **p ≈ 0.038**

---

## 1. 目标

R064 的 cold_snap 采暖启用为 3/5（p≈0.083，边缘）。本轮补齐 house_0003 的 M3/M4/M5（both arms），
扩大样本以判定显著性。

## 2. 设计（可复现）

```powershell
foreach ($i in 2,3,4) {   # Member 3/4/5
  python run.py --mode simulate --world world_172148 --house house_0003 --member $i --days 1 --env "h3m$i`_ctl" --workers 1
  python run.py --mode simulate --world world_172148 --house house_0003 --member $i --days 1 --env "h3m$i`_cold" --event-template "2026-09-11|cold_snap" --workers 1
}
```

采暖 = `SpaceHeater + AirConditioner` 分项 kWh（>0 记为启用）。

## 3. 结果（累计，2 世界）

| 世界/住户/成员 | baseline 采暖 | cold_snap 采暖 | 启用 |
|---|---|---|---|
| w838 h002M1 | 0.000 | 10.200 | ✓ |
| w172 h002M1 | 0.000 | 0.000 | ✗ |
| w172 h002M2 | 0.000 | 12.000 | ✓ |
| w172 h003M1 | 0.000 | 9.000 | ✓ |
| w172 h003M2 | 0.000 | 0.000 | ✗ |
| w172 h003M3 | 0.000 | 0.000 | ✗ |
| w172 h003M4 | 0.000 | 12.000 | ✓ |
| w172 h003M5 | 0.000 | 0.000 | ✗ |

**汇总**：baseline **0/8**；cold_snap **4/8**。
**Fisher 精确检验：单侧 p ≈ 0.0385 → 显著（p<0.05）。**

## 4. 解读

- **cold_snap 采暖启用达显著**：baseline 8 个样本全 0，cold_snap 8 个中 4 个启用；
- **启用率 50%**：明显低于热浪（90%），说明**不同事件的响应稳健性不同**（冷天或有替代行为）；
- 效应量大（启用时 9–12 kWh）；
- 现为**第二个 p<0.05 的结论**（仅次于热浪 p≈0.0004；强于本项其余所有幅度性结论）。

## 5. token 消耗（估算）

- 本轮 6 个 run × (4 步 × 1 成员 × 1 天) ≈ **24 次调用**。

## 6. 论文更新

- `paper/experiments/event_cold_snap.md`：更新为 **0/8 vs 4/8（p≈0.038，显著）**；
- `paper/99_discussion.md` RQ2：cold_snap 升级为显著；
- `paper/README.md`：状态更新。

## 7. 结论

**环境事件 → 设备启用**（热浪→制冷 9/10；寒潮→采暖 4/8）**均为显著的大效应信号**，
共同支撑"平台擅长定性/大效应结论"的定位（R058）。
