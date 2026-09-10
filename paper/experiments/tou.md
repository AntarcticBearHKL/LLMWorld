# Experiment: Time-of-use pricing (TOU)

> 状态：**初步；方向正确，但幅度不可定论**（R024 去指令消融显示单成员方差主导）。数值来自 R023/R024。

## 1. Research Question

对应 **RQ2**（外部输入的行为传导）；研究计划政策干预阶段。核心问题：把 TOU 费率**以自然语言**
告知居民后，峰段负荷是否下降、谷段是否抬升？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §2.1）**：峰段(16–21)负荷 −5~15%、谷段抬升、总量大致不变；
  弹性主要来自**峰移**而非总量削减。
- **文献基准（Faruqui & Sergici 2010）**：**纯 TOU 平均削峰 3~6%**（叠加恒温器/智能家电可达 10~30%）。
- **合理区间**：峰值 −3~6%；若远高于此，先查 prompt 是否写得太强。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（单人，含 WashingMachine/Dishwasher/ClothesDryer/WaterHeater）。
- **Dates / Days**：2026-09-11 / 09-12（2 天）。
- **Intervention / Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env tou_ctl --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env tou_run --policy tou --workers 1
  ```
- **Model / Params**：DeepSeek，`temperature=1.0`，thinking on；`--workers 1`。
- **Analysis**：`load_model.build_load_profile` 按峰/谷/肩段计算 kWh（峰 16–21，谷 22–07）。

## 4. Metrics

峰段 kWh 变化 %、谷段 kWh 变化 %、总电量变化 %、峰值 W 与峰时。

## 5. Results（初步）

| 日期 | 臂 | 总 kWh | 峰段 kWh | 谷段 kWh | 峰 W |
|---|---|---|---|---|---|
| 09-11 | control | 8.193 | 4.892 | 0.804 | 3320.1 |
| 09-11 | TOU | 10.275 | **4.020** | **2.491** | 5519.1 |
| 09-12 | control | 11.828 | 2.239 | 0.777 | 5519.1 |
| 09-12 | TOU | 11.950 | **1.666** | 0.780 | 3520.1 |

- 峰段：**−17.83% / −25.59%**；谷段：+209.83%（0.80→2.49）/ +0.39%；总量：+25.41% / +1.03%。

## 6. Comparison with Literature

- **方向一致**（峰降/谷升），但**幅度 −18~−26% 远超纯 TOU 的 3~6%**。
- 按 guide §8：应先检查 prompt 是否过强 → **当前 TOU 文本含明确指令**（shift…into the valley；
  avoid running high-power appliances during peak），LLM 可能**过度遵从**。

## 7. Validity Check

- 政策文本**是否过强**：R024 加入去指令版 `tou_soft` 消融后**未支持**该假设：
  `tou_soft` 09-11 峰段 −39.8%、09-12 峰段 **+79.6%**（且总量 −32%），自相矛盾
  → **运行间方差主导**，无法把效应归因于政策文本强度。
- 是否涌现：方向（峰降谷升）在硬 TOU 两日一致，但幅度**不可定论**。
- 混杂：n=1 成员、2 天、`temperature=1.0`。**须扩大样本**（多人户/多种子）或降温度。

## 8. Conclusion

- **初步且不可定论**：硬 TOU 峰段 −18~−26%（超纯 TOU 基准），但 R024 的去指令版 `tou_soft`
  未能复现"软化→幅度回落"，反而出现 −39.8% 与 +79.6% 的**自相矛盾**结果 → **运行间方差主导**，
  既不能确认 prompt 偏置，也不能确认真实削峰幅度。
- **可复现命令**：见第 3 节（消融：`--policy tou_soft`）。
- **下一步**：多人户（≥3 成员/户 × ≥2 户）或降温度，以把信号从噪声中分离。
