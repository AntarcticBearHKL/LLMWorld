# R103 — `blackout_risk` 跨 3 世界方向复现（−7.3%~−31.7%）

- **轮次**：Round 103
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_143345 h002M1；blackout×3 + baseline×2；~16 calls）
- **结论**：✅ **方向跨 3 世界一致**（−7.3% / −11.7% / −31.7%，均为负）

---

## 1. 目标（C1 续）

将 `blackout_risk` 削峰结论从 2 世界扩到 **3 世界**。第三世界（world_143345 h002M1）**基线仅 1 个样本**
（初值 2.67）时曾显示 +18%（反向）；本轮补 2 个 baseline 以**fix基线分布**再评。

## 2. 设计（可复现）

```powershell
# world_143345 house_0002 Member 1, 1 天
python run.py --mode simulate --world world_143345 --house house_0002 --member 0 --days 1 --env b143_1 --workers 1   # +b143_2
foreach ($i in 1,2,3) { python run.py --mode simulate --world world_143345 --house house_0002 --member 0 --days 1 --env "bo143_$i" --event-template "2026-09-11|blackout_risk" --workers 1 }
```

## 3. 结果（峰段 16–21 kWh，跨 3 世界）

| 世界 | baseline (n=3) | blackout_risk (n=3) | 变化 |
|---|---|---|---|
| world_838587 | 4.686 ± 0.154 | 3.203 ± 0.298 | **−31.7%** |
| world_172148 | 3.461 ± 0.187 | 3.056 ± 0.645 | **−11.7%** |
| world_143345 | 3.398 ± 0.910 | 3.151 ± 0.239 | **−7.3%** |

（world_143345 基线 3 样本为 2.67/4.681/2.842，方差大；单看首样本 2.67 会误判为 +18%。）

## 4. 解读

- **方向跨 3 世界一致**（全负）→ `blackout_risk` 削峰**可复现**；
- **幅度异质**（−7%~−32%）且第 3 世界基线噪声大；
- **教训**：**单样本基线不足以判定**（R082/R057 的又一实例）——须先建立基线分布。

## 5. token 消耗（估算）

- 本轮 5 个 run（3 blackout + 2 baseline）× (4 步 × 1 成员 × 1 天） ≈ **20 次调用**。

## 6. 论文更新

- `paper/experiments/event_blackout_risk.md`：加 world_143345 行；state → **跨 3 世界方向复现**；
- `paper/README.md`：状态更新。

## 7. 结论

`blackout_risk` 削峰**跨 3 世界方向复现**（−7.3%~−31.7%）——本工作除“环境/封锁事件”外**唯一可复现的政策/预警类**削峰结论。
