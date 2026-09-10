# R062 — cold_snap 事件：采暖设备启用（第二个大效应信号）

- **轮次**：Round 62
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 house_0002；cold_snap vs baseline；~4 calls）
- **结论**：✅ **大效应**：baseline 采暖 0，cold_snap 启用 **SpaceHeater 3.0 + AC 7.2 kWh**，总电量 **+158%**

---

## 1. 目标

R058 指出只有二值/大效应可判。热浪（R059–R061）已证。本轮测试**另一环境事件** `cold_snap`
（guide §5.1：cold_snap → 采暖上升），是否为类似的大效应信号。

## 2. 设计（可复现）

```powershell
# baseline 复用 tou_ctl（同户/成员/日，无政策无事件）
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
  --env cold_run --event-template "2026-09-11|cold_snap" --workers 1
```

- 天气联动：`cold_snap` → ColdSnap / 温度 −10（R015 机制）；
- 离线 `load_model` 计算采暖类分项。

## 3. 结果（2026-09-11）

| 臂 | 总 kWh | SpaceHeater | AirConditioner | Fan | Dehumidifier |
|---|---|---|---|---|---|
| baseline | 8.193 | 0.0 | 0.0 | 0.0 | 0.0 |
| **cold_snap** | **21.140** | **3.000** | **7.200** | 0.0 | 0.0 |

- 总电量 **+158%**（8.193 → 21.140）；
- **采暖设备由全 0 变为启用**：SpaceHeater 3.0 kWh、AC 7.2 kWh（模型用 AC 制热）。

## 4. 解读

- **第二个大效应环境事件**：与热浪对称（热→制冷启用；冷→采暖启用），方向符合 guide §5.1；
- **信号强**（baseline 全 0，事件后大幅上升），属 R058 认定的"可判"类型；
- **限制**：**n=1**（单户单日），须如热浪那样**跨成员/跨世界复现**方可升格。

## 5. token 消耗（估算）

- 1 个 cold_snap run × (4 步 × 1 成员 × 1 天) ≈ **4 次调用**。

## 6. 论文更新

- 新增 `paper/experiments/event_cold_snap.md`（初步）；
- `paper/99_discussion.md` RQ2：新增 cold_snap 初步条；
- `paper/README.md`：新增清单行。

## 7. 下一步

1. 按热浪同法为 cold_snap 扩展样本（跨成员/世界）以升格；
2. 或继续寻找其它大效应二值信号。
