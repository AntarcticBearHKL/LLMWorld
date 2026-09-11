# R098 — `in_home_display`：方向一致（−5.2%）但 N=3 未显著

- **轮次**：Round 98
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002 M1；in_home_display×3；baseline 复用；~12 calls）
- **结论**：⚠️ **不显著**：总量 −5.2%、峰段 −8.4%，均**在噪声内**（点估计落在 guide 3~10% 区间，但 z<1）

---

## 1. 目标（B2 续）

测试 `in_home_display`（实时反馈，guide §4.2 期望 3~10% 节能）在**低噪峰段指标**上的效果。

## 2. 设计（可复现）

```powershell
foreach ($i in 1,2,3) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env "ihd172_$i" --policy in_home_display --workers 1
}
# baseline 复用 nw_ctl + bp172_1 + bp172_2
```

## 3. 结果

| 指标 | baseline (n=3) | in_home_display (n=3) | 变化 | z |
|---|---|---|---|---|
| 总电量 kWh | 9.340 ± 1.388 | 8.850 ± 0.792 | **−5.2%** | ~−0.5 |
| 峰段 kWh | 3.461 ± 0.187 | 3.169 ± 0.475 | **−8.4%** | ~−1.0 |

## 4. 解读

- **方向与 guide 一致**（反馈→节能），点估计 −5.2% 落在文献 3~10% 区间内；
- **但 N=3 下不显著**（变化 < 噪声；treatment 方差大）；
- 与主线一致：软干预在单/小样本下**不可判**；若要结论须更大 N（C1）。

## 5. token 消耗（估算）

- 3 个 run × (4 步 × 1 成员 × 1 天） ≈ **12 次调用**。

## 6. 论文更新

- `paper/experiments/in_home_display.md`：第 5 节填初步（−5.2%，N=3 不显著），状态“初步(不显著)”。

## 7. 结论

`in_home_display` **方向一致但不显著**（N=3）；列入待扩样。至此 B 的**占位实验基本覆盖**：
`peak_demand`=null、`in_home_display`=不显著；`night_setback`（需冬季）与 `policy_tradeoffs`（分析型）待后续。
