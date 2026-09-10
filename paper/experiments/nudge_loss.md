# Experiment: Loss-framed nudge (`nudge_loss`)

> 状态：**初步反例**：损失框架 `nudge_loss` 使总电量**上升** +5.7%/+6.1%，与 guide 预期（比 nudge 多省 ~5%）
> **方向相反**。数值来自 R041；n=1、2 天，勿作最终结论。

## 1. Research Question

对应 **RQ2**。损失框架（"不省电将失去补贴/被标记"）是否比规范/增益框架带来**更强**的节能？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §3.2）**：`nudge_loss` 比 `nudge` 多省约 **5 个百分点**（损失厌恶）。
- **文献基准**：Ghesla et al. (2019)（损失框架显著更省）；Kahneman & Tversky 损失厌恶理论。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（单人）；Dates：2026-09-11/12（2 天）。
- **Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env nudge_loss_run --policy nudge_loss --workers 1
  # 对照：--policy nudge (R037), baseline: --env tou_ctl
  ```
- **Model / Params**：DeepSeek，thinking on；`--workers 1`。
- **Analysis**：`load_model.build_load_profile` 总电量。

## 4. Metrics

总电量变化 %（vs baseline；并与 `nudge` 对比）。

## 5. Results（初步）

| 日期 | 臂 | 总 kWh | vs baseline |
|---|---|---|---|
| 09-11 | baseline | 8.193 | — |
| 09-11 | nudge | 7.350 | −10.29% |
| 09-11 | **nudge_loss** | 8.659 | **+5.69%** |
| 09-12 | baseline | 11.828 | — |
| 09-12 | nudge | 11.147 | −5.76% |
| 09-12 | **nudge_loss** | 12.554 | **+6.14%** |

## 6. Comparison with Literature

- **与文献相反**：预期 nudge_loss 更强节能，实测**增耗** ~6%，与 nudge 相差 ~14 个百分点。

## 7. Validity Check

- 文本为损失框架（"lose the 30 AUD rebate"），无行为指令；方向异常。
- 可能解释：n=1/2 天随机性；措辞引发不同解读/逆反；框架效应在 LLM 代理上不稳定。
- 与 R040 一致的主线：**措辞驱动 > 信息驱动**（LLM 对文本措辞高度敏感）。

## 8. Conclusion

- **初步反例**：本平台单成员设置下**未复现损失厌恶**，`nudge_loss` 反而增耗；
  需多人户复现以确认是方法学现象还是噪声。
- **可复现命令**：见第 3 节。
