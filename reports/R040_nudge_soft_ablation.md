# R040 — 社会规范去指令消融：支持"prompt 过度遵从"假设

- **轮次**：Round 40
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（house_0002，2 天；nudge_soft 新跑，baseline/nudge 复用）
- **结论**：✅ **支持过度遵从假设**：去掉规范性措辞后效应几乎消失（−6~−10% → ≈0）

---

## 1. 目标

R037 发现固定 `nudge` 降总电量 −6~−10%（超 −1~3% 基准）；R039 提出"prompt 过度遵从"解释。
本轮用 R038 的 **`nudge_soft`（仅事实均值、无规范性压力）** 做直接消融检验。

## 2. 设计（可复现）

- world `world_838587`；house `house_0002`；member `Member 1`；`--days 2`；`--workers 1`；
- baseline：复用 `tou_ctl`；nudge：复用 R037 的 `nudge_run`；
- **新跑**：`--env nudge_soft_run --policy nudge_soft`（“Your neighbours use about 18 kWh per day on average.”）
- 对照文本差异：`nudge` 多出规范性短语 "Most households in your area try to keep their usage near or below this level."

## 3. 结果

| 日期 | 臂 | 总 kWh | vs baseline |
|---|---|---|---|
| 09-11 | baseline | 8.193 | — |
| 09-11 | **nudge**（规范性） | 7.350 | **−10.29%** |
| 09-11 | **nudge_soft**（仅事实） | 8.114 | **−0.96%** |
| 09-12 | baseline | 11.828 | — |
| 09-12 | **nudge** | 11.147 | **−5.76%** |
| 09-12 | **nudge_soft** | 12.567 | **+6.25%** |

**派生**：nudge 均值 ≈ **−8.0%**；nudge_soft 均值 ≈ **+2.6%**（无效应/微增）。

## 4. 解读

- **规范性措辞是效应主因**：仅保留"邻居均值"这一事实信息时，总电量几乎不变；
  加上"大多数家庭都尽量不超标"的规范压力后，出现 −6~−10% 的（超额）下降。
- **支持过度遵从**：LLM 对**指令式/规范式**文本的遵从强于对**纯信息**的反应，
  这与 R023（TOU 硬文本 −18~−26%）模式一致，也解释了超基准幅度。
- **限制**：n=1、2 天、随机性；但硬/软两臂差异大（≈10 个百分点），方向清晰。

## 5. 论文更新

- `paper/experiments/nudge.md`：新增消融小节，结论改为"效应由规范性措辞驱动（过度遵从）"。
- `paper/99_discussion.md` Threats-to-validity：补充本消融为过度遵从的**直接证据**。

## 6. token 消耗（估算）

- 本轮 1 臂 × (4 步 × 2 天) ≈ **8 次调用**（baseline/nudge 复用）。

## 7. 下一步（候选）

1. 在**多人户**上重复该消融，确认收敛后的幅度是否落入基准区间；
2. `nudge` vs `nudge_loss`（损失框架，guide §3.2）；
3. 政策时间线真调（习惯黏性）。
