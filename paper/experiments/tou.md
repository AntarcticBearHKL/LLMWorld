# Experiment: Time-of-use pricing (TOU)

> 状态：**初步；方向正确但幅度超基准 → 疑似 prompt 偏置，待软化文本后重做**。数值来自 R023。

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

- 政策文本**是否过强**：很可能是本轮超幅的主因；需做"去指令版 TOU"消融对照。
- 是否涌现：方向可，但幅度可疑 → **暂不认定为可信的 3~6% 削峰**。
- 混杂：n=1、2 天、`temperature=1.0`。

## 8. Conclusion

- **初步**：TOU 干预在仿真中产生明显峰移（峰段 −18~−26%），但与纯 TOU 文献区间不符，
  证据指向 **prompt 偏置**；须软化文本后复测方能与基准比较。
- **可复现命令**：见第 3 节。
- **下一步**：去指令版 TOU 消融 + 多人户/多日复现。
