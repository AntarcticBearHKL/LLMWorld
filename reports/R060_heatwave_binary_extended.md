# R060 — 扩展热浪二值样本：baseline 0/5 vs heatwave 7/8（Fisher p≈0.0047）

- **轮次**：Round 60
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（新增 house_0001 Member 4 的 baseline/heatwave，各 1 天；~8 calls）
- **结论**：✅ **二值结果更强**：baseline **0/5** vs heatwave **7/8**，Fisher 单侧 **p ≈ 0.0047**

---

## 1. 目标

R059 的二值结果（0/4 vs 6/7, p≈0.015）已达显著。本轮按"可实现的平均 campaign"**扩展二值样本**
（连续幅度的 campaign 已被 R058 判为不可行），为 paper 的最强结论增样。

## 2. 设计（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0001 --member 3 --days 1 --env m4_ctl --workers 1
python run.py --mode simulate --world world_838587 --house house_0001 --member 3 --days 1 --env m4_hw --event-template "2026-09-11|heatwave" --workers 1
```

- 新增 `house_0001 Member 4` 的 baseline 与 heatwave（2026-09-11）；
- 复用 R059 的既有样本；
- **`--member 4`（Member 5）运行失败**：house_0001 仅 4 名成员 → 正确跳过（非 bug）。

## 3. 结果（world_838587，按 `AirConditioner` 分项 >0 记启用）

| 条件 | 成员-日 | AC 启用 |
|---|---|---|
| baseline | h002M1；h001M1/2/3/4 | **0/5** |
| heatwave | h002M1×4（两窗口）；h001M1/2/3/4 | **7/8** |

- 新增 h001M4 heatwave：AC = **0.600 kWh（启用）**；
- **Fisher 单侧 p ≈ 0.0047**（较 R059 的 0.015 更显著）。

## 4. 解读

- **二值结果进一步增强**且方向一致（2 户、多日期/成员）；baseline **5 个样本全不启用**；
- 热浪 8 个样本中 **7 个启用**（唯一未启用者为 h001M3，体现**个体异质性**）；
- 与 R058 功效分析一致：**二值/大效应**在 CV≈12% 噪声下仍可显著，是平台的**可信结论类型**。

## 5. token 消耗（估算）

- 本轮 2 个成功 run × (4 步 × 1 天) ≈ **8 次调用**（另 2 个 m5 run 因成员不存在被跳过）。

## 6. 论文更新

- `paper/experiments/event_heatwave.md`：二值统计更新为 **0/5 vs 7/8, p≈0.0047**；
- `paper/99_discussion.md` RQ2：更新对应数字；
- `paper/README.md`：状态更新。

## 7. 结论

热浪→空调启用是当前**唯一**达到统计显著（且 p<0.01）的结论，已有 2 户 / 8 个 heatwave 成员-日支持。
