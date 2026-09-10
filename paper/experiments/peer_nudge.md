# Experiment: Neighbour comparison (`peer-nudge`)

> 状态：**初步（不一致）**：R037 的动态邻居均值结果自相矛盾（+11.6% / −6.6%）；固定文本对照见
> `nudge.md`（−6~−10%，措辞驱动）。样本 n=1，勿作最终结论。

## 1. Research Question

对应 **RQ2**。用**真实邻居均值**（随社区滚动）比较，是否优于固定文本规范？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §6.1）**：真实邻居比较略优于固定文本；高耗家庭响应更强。
- **文献基准**：Ayres 2013（−1~3%，高耗家庭最强）；Opower 后续研究（动态比较略优）。

## 3. Experimental Setup

- World：`world_838587`，house `house_0002`；Days：2；
- Command：`python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env peer_run --peer-nudge --workers 1`
  （对照 `nudge_run` / `tou_ctl`）。
- Analysis：`load_model.build_load_profile` 总电量。

## 4. Metrics

总电量变化 %、与固定 `nudge` 的差异。

## 5. Results（初步）

| 日期 | peer 总 kWh | vs baseline | nudge vs baseline |
|---|---|---|---|
| 09-11 | 9.141 | +11.57% | −10.29% |
| 09-12 | 11.044 | −6.63% | −5.76% |

（baseline：tou_ctl。首日无上一日 → 无 peer 文本。）

## 6. Comparison with Literature

- peer **未显示**优于固定文本；两日方向矛盾（+11.6% / −6.6%）。

## 7. Validity Check

- n=1、2 天；peer 首日缺均值；方差主导。需多人户复测。

## 8. Conclusion

- **初步/不一致**：动态邻居比较在单成员下不稳定；固定 `nudge` 反而更一致（但疑措辞驱动，见 nudge.md）。
- **下一步**：多人户 `nudge` vs `peer-nudge` 对照。
