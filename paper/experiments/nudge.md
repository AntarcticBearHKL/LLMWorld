# Experiment: Social-norm nudge

> 状态：**初步**：固定 nudge（含规范性措辞）降总电量 −6~−10%（超 −1~3% 基准）；
> R040 去指令消融显示**去掉规范性措辞后效应几乎消失**（−1% / +6%）→ 支持 **prompt 过度遵从**。
> 动态 peer-nudge 不一致。数值来自 R037/R040；n=1，勿作最终结论。

## 1. Research Question

对应 **RQ2**（非价格行为干预的行为传导）。核心问题：把"邻居平均用电"以自然语言告知居民，
是否降低其总用电？

## 2. Hypothesis & Expected Effect

- **预期（intervention_experiment_guide.md §3.1）**：总电量下降 1~3%；**高耗家庭响应更强**。
- **文献基准**：Allcott 2011（Opower 约 −2%）；Ayres 2013（−1~3%，高耗家庭最强）。
- **合理区间**：−1~3%；远高于此需查 prompt 偏置。

## 3. Experimental Setup

- **World**：`world_838587`，house `house_0002`（单人）。
- **Dates / Days**：2026-09-11 / 09-12（2 天）。
- **Intervention / Command**：
  ```powershell
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env nudge_run --policy nudge --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 2 --env peer_run --peer-nudge --workers 1
  # baseline: --env tou_ctl (no policy)
  ```
- **Model / Params**：DeepSeek，thinking on，`temperature` 未覆盖；`--workers 1`。
- **Analysis**：`load_model.build_load_profile` 总电量/峰值。

## 4. Metrics

总电量变化 %、峰值 W。

## 5. Results（初步）

| 日期 | 臂 | 总 kWh | 峰值 W | vs baseline |
|---|---|---|---|---|
| 09-11 | baseline | 8.193 | 3320.1 | — |
| 09-11 | nudge | 7.350 | 3320.1 | **−10.29%** |
| 09-11 | peer | 9.141 | 3520.1 | +11.57% |
| 09-12 | baseline | 11.828 | 5519.1 | — |
| 09-12 | nudge | 11.147 | 3520.1 | **−5.76%** |
| 09-12 | peer | 11.044 | 3520.1 | −6.63% |

**Ablation — de-instructionalized `nudge_soft` (R040)**

| 日期 | 臂 | 总 kWh | vs baseline |
|---|---|---|---|
| 09-11 | nudge（规范性） | 7.350 | −10.29% |
| 09-11 | nudge_soft（仅事实） | 8.114 | −0.96% |
| 09-12 | nudge | 11.147 | −5.76% |
| 09-12 | nudge_soft | 12.567 | +6.25% |

去掉规范性措辞后，总电量变化由 −6~−10% 降至 ≈0 → 效应由**规范性措辞**驱动（过度遵从）。

## 6. Comparison with Literature

- 方向一致（总电量下降），但**幅度 −6~−10% 超出 −1~3% 基准** → 与 R023 TOU 同样的"过度遵从"疑点。
- peer-nudge（真实邻居均值）**未显示**优于固定文本的稳定性（反而两日矛盾）。

## 7. Validity Check

- 政策文本是否过强：`nudge` 文本含"Most households ... keep their usage near or below this level"，
  属规范性引导，可能被 LLM 过度执行 → 需软化对照。
- 混杂：n=1、2 天、`temperature` 未覆盖；peer 首日无上一日均值。

## 8. Conclusion

- **初步**：固定社会规范 nudge（含规范性措辞）一致降低总用电（−6~−10%），方向正确但幅度超基准；
  R040 去指令消融（`nudge_soft`）使效应消失（≈0）→ 效应由**规范性措辞**驱动，支持 **prompt 过度遵从**。
- **可复现命令**：见第 3 节（含 `--policy nudge_soft` 消融）。
- **下一步**：多人户平均；`nudge` vs `nudge_loss`（损失框架，guide §3.2）。
