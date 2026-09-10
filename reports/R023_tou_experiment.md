# R023 — TOU 分时电价效应实验（RQ2 旗舰干预）

- **轮次**：Round 23
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（`--policy tou` vs baseline，house_0002，2 天）
- **结论**：⚠️ **方向正确、幅度超基准**（峰值 −18~−26% vs 文献 −3~6%）→ 疑似 **prompt 偏置**

---

## 1. 目标

验证旗舰政策干预 TOU 的行为传导：住宅在 16–21 峰段负荷是否下降、22–07 谷段是否抬升。
对照基准：Faruqui & Sergici (2010)——**纯 TOU 平均削峰 3~6%**（guide §2.1/§8）。

## 2. 设计（可复现）

- world `world_838587`；house `house_0002`（单人，含 WashingMachine/Dishwasher/ClothesDryer/WaterHeater 等柔性设备）；
  member `Member 1`；`--days 2`（2026-09-11/12）；`--workers 1`；
- control：`--env tou_ctl`（无政策）
- TOU：`--env tou_run --policy tou`（政策文本经 `engine/policy.render_tou_policy` 注入 s4；输出带 `_tou` 后缀）
- 离线 `load_model.build_load_profile` 按峰段(16–21)/谷段(22–07)/肩段计算 kWh。

## 3. 结果

| 日期 | 臂 | 总 kWh | 峰段 kWh | 谷段 kWh | 肩段 kWh | 峰 W | 峰时 |
|---|---|---|---|---|---|---|---|
| 09-11 | control | 8.193 | 4.892 | 0.804 | 2.497 | 3320.1 | 7 |
| 09-11 | TOU | 10.275 | **4.020** | **2.491** | 3.764 | 5519.1 | 7 |
| 09-12 | control | 11.828 | 2.239 | 0.777 | 8.812 | 5519.1 | 8 |
| 09-12 | TOU | 11.950 | **1.666** | 0.780 | 9.504 | 3520.1 | 8 |

**相对变化（TOU vs control）**：

| 日期 | 峰段 % | 谷段 % | 总电量 % |
|---|---|---|---|
| 09-11 | **−17.83%** | +209.83%（0.804→2.491） | +25.41% |
| 09-12 | **−25.59%** | +0.39% | +1.03% |

## 4. 与文献比较（Validity Check）

- **方向正确**：峰段负荷下降、谷段抬升（load shifting），与 TOU 预期一致。
- **幅度超区间**：纯 TOU 基准为 3~6%（Faruqui & Sergici 2010），本实验 −18%~−26%，
  **远超上限**。按 guide §8 的检查顺序：**先怀疑 prompt 写太强**——当前 TOU 文本含明确指令
  （"shift flexible appliances ... into the valley"、"avoid running high-power appliances during peak"），
  LLM 居民可能**过度遵从**，而非涌现。
- **09-11 谷段 +210%**：基数很小（0.80→2.49 kWh），相对值放大，不宜解读为强度。
- **总电量**：09-12 基本不变（+1%）符合"以峰移为主、非总量削减"；09-11 +25% 属日间差异/随机性。

## 5. 结论

- TOU 干预**可传导**且方向正确，但**幅度不合乎纯 TOU 基准**，证据不足以声称"真涌现的 3~6% 削峰"；
- **建议**：软化 TOU 文本（去掉指令式措辞，仅陈述费率），重做对照；或改用显式"价格弹性"评估。
- 已写入 `paper/experiments/tou.md`（含 validity 标注）。

## 6. token 消耗（估算）

- 2 臂 × (4 步 × 2 天) ≈ **16 次调用**。

## 7. 产物

- `reports/R023_tou_experiment.md`（本文件）；
- `paper/experiments/tou.md`（初步 + validity）；
- `paper/README.md` 状态更新。

## 8. 下一步

1. **软化 TOU 文本**（去指令）重做，检验削峰是否回落到 3~6%（同时是 prompt-bias 消融实验）；
2. 多人户/多日提高稳健性；
3. `population_runner.py` 恢复或正式废弃。
