# R053 — RQ3 微实验（新世界 house_0002：Low vs Medium 对 nudge 的响应）

- **轮次**：Round 53
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002，2 成员；nudge vs baseline，1 天）
- **结论**：⚠️ **描述性**：Medium 成员降幅（−17.4%）大于 Low（−10.1%），方向与假设一致，但每组 n=1

---

## 1. 目标

R052 生成了 awareness 不再退化的新世界。本轮做**首个 RQ3 分组微实验**：
house_0002 的 Low / Medium 两个成员在 `nudge` 下的响应是否分化（Costa & Kahn 2010）。

## 2. 设计（可复现）

```powershell
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 --env nw_ctl --workers 1
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 --env nw_nudge --policy nudge --workers 1
```

- house_0002 类型：Young Professional Couple；成员：Member 1（**Low**）、Member 2（**Medium**）；
- 日期 2026-09-11；离线 `load_model` 计算各成员总电量。

## 3. 结果

| 成员 | awareness | baseline kWh | nudge kWh | 变化 |
|---|---|---|---|---|
| Member 1 | Low | 8.959 | 8.054 | **−10.10%** |
| Member 2 | Medium | 9.589 | 7.920 | **−17.41%** |

## 4. 解读（保守）

- **方向与假设一致**：Medium（较高意识）对 nudge 的降幅**大于** Low；
- **但每组 n=1**，无法与运行噪声分离 → **纯描述性**，非统计结论；
- 与既有发现一致：nudge 效应由规范性措辞驱动（R040），且幅度超基准（过度遵从）。

## 5. token 消耗（估算）

- 2 臂 × (4 步 × 2 成员 × 1 天) ≈ **16 次调用**。

## 6. 论文更新

- `paper/experiments/group_heterogeneity.md`：第 5 节填入本初步观察（注明 n=1/组）。

## 7. 下一步（候选）

1. 在 house_0001（3 Low + 2 Medium）与 house_0003（3 Low + 2 Medium）上重做，扩大每组样本（token 较高）；
2. 若方向在更大样本上稳定，再作为 RQ3 结果。
