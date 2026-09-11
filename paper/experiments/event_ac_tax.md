# Experiment: Air-conditioner peak tax (`ac_tax`)

> 状态：**定稿（有效果；跨 3 世界复现）**：热浪背景下 ac_tax 使 **AC 启用 15/15 → 7/15**（Fisher 双侧 **p≈0.0022**，漂移免疫），
> 峰段 **−22.5%（t=−2.36）**、AC kWh **−53.8%**（world_838587, n=15）；三世界峰段 **−22.5% / −24.6% / −20.6%**
> （合并 Stouffer Z≈−5.14, **p≈1.4×10⁻⁷**；world_172148 n=9、world_143345 n=15）。数值来自 R118/R120/R122/R125。

## 1. Research Question

对应 **RQ2**。对**晚峰空调用电**征收（自然语言告知的）10% 税，是否促使家庭在峰段减少空调，从而削峰？
与 `heatwave`（开启 AC）构成**条件-抑制**对：热浪制造需求，ac_tax 抑制其峰段使用。

## 2. Hypothesis & Expected Effect

- **预期**：晚峰空调被征税 → 家庭在峰段降低/关闭 AC → 峰段负荷下降；
- **文献基准**：Faruqui & Sergici 2010（价格型干预削峰 3~6%，尖峰定价更强）；ac_tax 为**靶向**价格信号，预期强于通用 TOU；
- **合理区间**：峰段 −5~20%；若远高于此，先查 prompt 是否过强。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（含 `bedroom_1_airconditioner`）；`Member 1`；1 天（2026-09-11）。
- **Intervention / Command**：
  ```powershell
  # 对照（仅热浪）
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env "hw_$i" --event-template "2026-09-11|heatwave" --workers 1
  # 处理（热浪 + 空调峰税）
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env "ha_$i" --event-template "2026-09-11|heatwave" --event-template "2026-09-11|ac_tax" --workers 1
  ```
- **设计**：**同批次交错**（`hw_i` 紧邻 `ha_i`，i=1..15）以规避跨时段漂移（R104 红线）。
- **Analysis**：`load_model.build_load_profile` 取 AC kWh、峰段(16–21) kWh、总电量。

## 4. Metrics

AC 启用（二值，AC kWh>0）、AC kWh、峰段 kWh、总电量 kWh，各取配对 mean/std 与配对 t。

## 5. Results（n=15，same-era 交错）

| 指标 | heatwave | heatwave+ac_tax | Δ | 配对 mean ± std | t(df=14) |
|---|---|---|---|---|---|
| **AC 启用（二值）** | **15/15** | **7/15** | — | — | **Fisher 双侧 p≈0.0022** |
| AC kWh | 5.627 ± 2.135 | 2.600 ± 3.407 | **−53.8%** | −3.027 ± 3.868 | −3.03（p≈0.009） |
| 峰段(16–21) kWh | 4.164 ± 1.307 | 3.225 ± 0.660 | **−22.5%** | −0.939 ± 1.540 | **−2.36（p≈0.033）** |
| 总电量 kWh | 14.268 ± 3.507 | 10.774 ± 4.230 | −24.5% | −3.494 ± 4.720 | −2.87（p≈0.012） |

## 6. Comparison with Literature

- **方向与文献一致**（价格型干预削峰），且 **ac_tax 靶向 AC** 的幅度（峰段 −22.5%）**强于通用 TOU**——
  与"靶向/尖峰定价更强"（Faruqui & Sergici 2010）一致；
- 但幅度高于纯 TOU 基准（3~6%），提示 LLM 代理**较强遵从**（亦见 R040）。

## 7. Validity Check

- **二值信号漂移免疫**（AC on/off），15/15 → 7/15，**p≈0.0022**（最强证据）；
- **same-era 交错**：`hw_i`/`ha_i` 紧邻；**漂移检验**峰段–次序斜率 **−0.021 kWh/run**，远小于效应 −0.94；
- **n=15 功效**：峰段效应随 n=3→9→15 收缩（−37.3%→−36.3%→−22.5%）但**保持显著** → 真实效应特征
  （对比 TOU 塌缩为 null，R114）；
- 限制：单成员、1 天、单世界；条件于热浪背景（无热浪则 AC 本就不开）。

## 8. Conclusion

- **有效果（定稿）**：热浪背景下 `ac_tax` **显著降低空调使用与峰段负荷**——
  AC 启用 15/15→7/15（p≈0.0022）、峰段 −22.5%、AC −53.8%、总电量 −24.5%（n=15）；
- **四个大效应事件**之一（热浪/封锁/寒潮/ac_tax），且**首个通过 n≥15 连续功效检验**的事件；
- **可复现命令**：见第 3 节。

## 9. Cross-world replication (R120)

Replicated on `world_172148` house_0002 Member 1 (AC = `living_room_airconditioner`), n=9, same-era interleaved:

| 世界 | n | 峰段 Δ | AC Δ | AC-on | 峰段 t |
|---|---|---|---|---|---|
| world_838587 (R118) | 15 | **−22.5%** | −53.8% | 15/15→7/15 | −2.36 |
| **world_172148 (R120)** | 9 | **−24.6%** | −67.0% | 9/9→3/9 | −2.56 |

Peak effect **nearly identical across worlds (−22.5% vs −24.6%)**; AC-on significant in both
(Fisher p≈0.0022 and ≈0.009). `ac_tax` is thus a **2-world-replicated** effective event.

### Third world (R122)

Replicated on `world_143345` house_0002 Member 1 (3 ACs), n=9:

| 世界 | n | 峰段 Δ | AC Δ | AC-on | 峰段 t |
|---|---|---|---|---|---|
| world_838587 (R118) | 15 | **−22.5%** | −53.8% | 15/15→7/15 | −2.36 |
| world_172148 (R120) | 9 | **−24.6%** | −67.0% | 9/9→3/9 | −2.56 |
| **world_143345 (R122+R125)** | 15 | **−20.6%** | −23.7% | 9/9→9/9 | **−3.99** |

**Peak effect negative in all three worlds** (−22.5% / −24.6% / −20.6%, mean ≈ −22.5%;
Stouffer combined Z ≈ −5.14, p ≈ 1.4×10⁻⁷). The form is
heterogeneous: W1/W2 turn AC *off* (binary significant), W3 only *reduces* AC (binary unchanged) —
consistent with "event effects condition on baseline appliance configuration" (R082/R083). `ac_tax` is
thus a **3-world-replicated** effective event, on par with heatwave/lockdown/cold-snap.
