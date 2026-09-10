# Experiment: Off-peak charging subsidy (`subsidy`)

> 状态：**占位（待验证）**。第 1–4 节就绪；第 5 节待跑后填。

## 1. Research Question

对应 **RQ2**。谷期充电补贴是否把 EV 充电从晚峰移到深夜谷期（"鸭子曲线"变平）？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §2.2）**：EV 充电由晚峰移向深夜，晚峰下降、谷段隆起。
- **文献基准**：Alexeenko & Bitar 2023（协同充电可降 EV 相关峰值）；Thorvaldsen et al. 2021
  （柔性充电相对"到即充"可削 EV 峰 **30~60%**）。
- **前提**：需要含 EV 的世界（生成不预设 EV，可用事件/配置注入）。

## 3. Experimental Setup（计划）

- World：≤5 户（需含 EV）；Days：≤3；
- Command：`python run.py --mode simulate --world <w> --house <h> --member 0 --days 2 --policy subsidy --workers 1`
  （`--policy "subsidy:0.25"` 可调费率）。
- Analysis：谷/峰段 kWh（同 compare_tou 窗口）+ `load_model`。

## 4. Metrics

晚峰段下降 %、谷段抬升 %、EV 充电时段分布、总电量变化 %。

## 5. Results

**待验证**（当前 world 无 EV）。

## 6. Comparison with Literature

待填（对照 30~60% 峰移区间）。

## 7. Validity Check

待填。

## 8. Conclusion

- **阻塞（advisory）**：`world_143345` 的基线 EV 充电已 **100% 落在谷期**（prompt 预置 "prefer
  overnight charging"），故 `subsidy`/峰移类干预**无 headroom**（R076/R077：subsidy 臂与基线同为
  100% 谷期）。
- **前置条件**：需先**移除/弱化 s4 的 overnight-charging 提示**以建立"自然/到即充"基线，
  EV 峰移实验方能评估（研究设计决策）。

