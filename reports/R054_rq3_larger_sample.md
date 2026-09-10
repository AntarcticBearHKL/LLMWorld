# R054 — RQ3 扩大样本：分组方向名义成立但**方差压倒**，nudge 效应不稳健

- **轮次**：Round 54
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148；house_0001 5 人 + house_0002 2 人；nudge vs baseline，1 天）
- **结论**：⚠️ **不能得出分组结论**：Low/Medium 均值方向名义一致（+3.4% vs −18.0%），
  但**组内离散度（±25~45pp）远大于组间差**；且 **7 人中 3 人对 nudge 反而增耗**

---

## 1. 目标

R053 在 house_0002（每组 n=1）看到"Medium 降幅 > Low"。本轮在 house_0001（3 Low + 2 Medium）扩大样本，
检验分组方向是否稳健。

## 2. 设计（可复现）

```powershell
# house_0001（5 人）
python run.py --mode simulate --world world_172148 --house house_0001 --days 1 --env nw_h1_ctl --workers 4
python run.py --mode simulate --world world_172148 --house house_0001 --days 1 --env nw_h1_nudge --policy nudge --workers 4
# house_0002（2 人，R053 复用）
```

## 3. 结果（world_172148，2026-09-11）

| 住户 | 成员 | awareness | baseline kWh | nudge kWh | 变化 |
|---|---|---|---|---|---|
| house_0001 | Member 1 | Low | 7.062 | 5.278 | **−25.26%** |
| house_0001 | Member 2 | Medium | 5.471 | 5.938 | **+8.55%** |
| house_0001 | Member 3 | Low | 5.643 | 7.867 | **+39.42%** |
| house_0001 | Member 4 | Medium | 7.632 | 4.188 | **−45.13%** |
| house_0001 | Member 5 | Low | 5.737 | 6.293 | **+9.69%** |
| house_0002 | Member 1 | Low | 8.959 | 8.054 | −10.10% |
| house_0002 | Member 2 | Medium | 9.589 | 7.920 | −17.41% |

**分组**：
- **Low**（n=4）：均值 **+3.44%**，值 [−25.26, +39.42, +9.69, −10.10]（范围 ≈65pp）
- **Medium**（n=3）：均值 **−18.00%**，值 [+8.55, −45.13, −17.41]（范围 ≈54pp）

## 4. 解读（关键修正）

- **组间方向名义一致**（Medium 更负），但**组内离散度远超组间差**（±25~45pp vs 均值差 ~21pp），
  n=3/4 → **不具统计意义**，不能作为 RQ3 结论。
- **nudge 效应不稳健**：7 人中 **3 人反而增耗**（+8.6%、+39.4%、+9.7%）——与 R048 的
  "house_0001 M1/M2/M3 全负"**不一致**（不同世界/成员）。说明此前"5/5 全负"是**小样本巧合**。
- 与主线一致：**单次/单成员结果不可信**（R047），效应量被运行方差淹没。

## 5. token 消耗（估算）

- 本轮 2 臂 × (4 步 × 5 成员 × 1 天) ≈ **40 次调用**。

## 6. 论文更新

- `paper/experiments/nudge.md`：**下调**结论为"方向不稳定、个体可增耗，方差主导"。
- `paper/experiments/group_heterogeneity.md`：第 5 节补充分组方差压倒的说明，撤回"Medium>Low"倾向。
- `paper/README.md`：nudge / group 状态更新。

## 7. 结论

R054 是一次**重要的阴性/修正结果**：在扩大样本后，nudge 的个体响应正负混杂、分组差异被方差淹没。
**唯一稳健的仍是二进制/定性信号**（热浪→AC on/off）；所有**幅度**结论须待大规模平均实验。
