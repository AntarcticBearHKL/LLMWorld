# Experiment: Energy-saving rebate (`rebate`)

> 状态：**partial（峰段 null）**：热浪背景下 `rebate` 显著降 **AC −40.8%、总电量 −21.2%**（n=15），
> 但**峰段 −6.0%（t=−0.88, n.s.）**。与 `ac_tax`（峰段 −22.5%，R118）对照，确立**靶向性边界**。数值来自 R119。

## 1. Research Question

对应 **RQ2**。**通用**峰段返利（"降低峰时用电可得返利"）是否削峰？与 `ac_tax`（靶向 AC+晚峰）对照，
检验削峰效果是否取决于**文本是否同时锚定时段与设备**。

## 2. Hypothesis & Expected Effect

- **预期（guide §2.x / Faruqui & Sergici 2010）**：峰段激励使家庭移峰 → 峰段下降；
- **对照假设**：通用措辞（仅"峰时"）可能弱于**设备×时段双锚定**（`ac_tax`）。

## 3. Experimental Setup

- **World**：`world_838587`，`house_0002` `Member 1`；1 天（2026-09-11）。
- **Intervention / Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env "hb_$i" --event-template "2026-09-11|heatwave" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
    --env "hr_$i" --event-template "2026-09-11|heatwave" --event-template "2026-09-11|rebate" --workers 1
  ```
- **设计**：同批次交错（`hb_i`/`hr_i`，i=1..15）。

## 4. Metrics

AC 启用（二值）、AC kWh、峰段(16–21) kWh、总电量，配对 mean/std/t。

## 5. Results（n=15）

| 指标 | heatwave | heatwave+rebate | Δ | 配对 mean ± std | t(df=14) |
|---|---|---|---|---|---|
| AC kWh | 6.400 ± 2.123 | 3.787 ± 3.403 | **−40.8%** | −2.613 ± 4.048 | −2.50（p≈0.026） |
| **峰段(16–21) kWh** | 3.666 ± 0.724 | 3.445 ± 0.574 | **−6.0%** | −0.221 ± 0.976 | **−0.88（n.s.）** |
| 总电量 kWh | 15.034 ± 2.738 | 11.852 ± 3.595 | **−21.2%** | −3.182 ± 4.238 | −2.91（p≈0.012） |

AC 启用 15/15 → 10/15（Fisher 双侧 p≈0.042）。

## 6. Comparison with Literature

- **峰段效应 null**（−6.0%，n.s.）：与纯 TOU 基准（3~6%）同量级、**不显著**；
- **降 AC/总电量显著**：返利使代理整体少开空调，但**未靶向峰段**。

## 7. Validity Check

- 二值（AC on/off）漂移免疫；same-era 交错；**漂移检验斜率 +0.003 kWh/run**（无漂移）；
- n=15 足功效；峰段效应 ~0（配对 mean −0.221 vs std 0.976）。

## 8. Conclusion

- **峰段 null（partial）**：通用 `rebate` **不显著削峰**，但显著降 AC/总电量；
- **靶向性边界**：只有**同时锚定"晚峰 + 设备"**的 `ac_tax` 才显著削峰（−22.5%）；
  通用措辞仅使代理**整体减少用电**而不移峰。与"措辞/靶向主导"主线一致。
