# Experiment: Time-of-use pricing (TOU)

> 状态：**不可定论**：方向对采样/推理模式敏感——推理模式峰段 −18~−26%，低方差无思考模式峰段 **+8~+30%**（方向翻转）。数值来自 R023/R024/R026。

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
- **低方差检查（R026）**：`--no-thinking --temperature 0.2` 两臂同采样下，TOU 峰段
  **+30.1% / +7.6%**（方向**翻转**），与推理模式的 −18%/−26% 相反 → 效应对推理模式高度敏感。
- 是否涌现：**不成立**（方向随设置改变）。
- 混杂：n=1 成员、2 天；即便低温，工作日/周末日程差异仍大。**须多人户平均**（≥3 成员/户 × ≥2 户）。

## 8. Conclusion

- **不可定论**：硬 TOU 推理模式峰段 −18~−26%（超纯 TOU 基准 −3~6%）；去指令消融（R024）
  与低方差无思考复测（R026）分别给出自相矛盾（−39.8%/+79.6%）与**方向翻转**（+30.1%/+7.6%）的结果
  → TOU 响应**对设置高度敏感**，**不能**作为论文结论。
- **可复现命令**：见第 3 节（消融：`--policy tou_soft`；低方差：`--no-thinking --temperature 0.2`）。
- **下一步**：多人户平均（≥3 成员/户 × ≥2 户）并固定星期；或优先复现更稳健的热浪（二进制信号）。

## 9. Habit-stickiness probe (R045 → falsified by control, R046)

Within the policy arm alone (`--policy-schedule "2026-09-11,2026-09-12,tou"`), the peak-window
"rebounded" after removal (policy days ≈2.72 kWh → removed days ≈3.55 kWh, R045). **A parallel
no-policy control (R046) overturns this**: the policy arm's peak was lower than control on *all four*
days, including the removed days (Δpeak: policy days ≈−1.54, removed days ≈−2.16). The apparent
rebound was a within-arm artifact, not a policy effect.
**Conclusion**: single-run-per-arm DiD is not trustworthy; the habit-stickiness question requires
multi-seed / multi-household averaging.
