# Experiment: EV charging-delay incentive (`ev_delay`)

> 状态：**占位（待验证）**。第 1–4 节就绪；第 5 节待跑后填。

## 1. Research Question

对应 **RQ2**。按延迟时长递减电价的激励下，不同"时间偏好"性格的居民如何权衡价格与便利？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §2.4）**：多数 EV 户选择延迟 2~6 小时、充电集中在 23–7h；
  低尽责性/弱规划的居民可能接受更高价即时充电 → **性格异质性可观测**。
- **文献基准**：Alexeenko & Bitar 2023（多数用户接受延迟换折扣，异质性显著）。

## 3. Experimental Setup（计划）

- World：需含 EV；Days：≤3；
- Command：`--policy ev_delay`（`--policy "ev_delay:0.05"` 可调每小时间隔）。
- Analysis：EV 充电时刻分布 + `analyze_groups.py --label-source awareness`（性格分组）。

## 4. Metrics

延迟时长分布、谷段集中度、性格分组间的选择差异。

## 5. Results

**待验证**（当前 world 无 EV）。

## 6. Comparison with Literature

待填。

## 7. Validity Check

待填。

## 8. Conclusion

- **阻塞（同 subsidy）**：基线 EV 充电已被 prompt 预置到谷期（R076/R077），
  `ev_delay` 的"延迟选择"缺乏可移动窗口；需先建立自然基线（移除 overnight-charging 提示）再评估。

