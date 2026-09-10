# R041 — 损失框架 `nudge_loss` 对照：与预期相反（反而增耗）

- **轮次**：Round 41
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（house_0002，2 天；nudge_loss 新跑，baseline/nudge 复用）
- **结论**：⚠️ **与 guide 预期相反**：`nudge_loss` 两日总电量**上升** +5.7% / +6.1%，
  而 `nudge` 下降 −10.3% / −5.8%（预期 nudge_loss 应比 nudge 更强）

---

## 1. 目标

guide §3.2 / Ghesla et al. (2019)：**损失框架**（不省电则失去补贴）应比增益/规范框架多省 ~5%。
本轮用 `--policy nudge_loss` 与 `--policy nudge` 在同一住户/日期上对照。

## 2. 设计（可复现）

- world `world_838587`；house `house_0002`；member `Member 1`；`--days 2`；`--workers 1`；
- baseline：`tou_ctl`；nudge：R037 的 `nudge_run`；
- **新跑**：`--env nudge_loss_run --policy nudge_loss`
  文本："Households that do not reduce their electricity use will be flagged as high-usage and lose the 30 AUD energy-saving rebate."

## 3. 结果

| 日期 | 臂 | 总 kWh | vs baseline |
|---|---|---|---|
| 09-11 | baseline | 8.193 | — |
| 09-11 | nudge | 7.350 | **−10.29%** |
| 09-11 | nudge_loss | 8.659 | **+5.69%** |
| 09-12 | baseline | 11.828 | — |
| 09-12 | nudge | 11.147 | **−5.76%** |
| 09-12 | nudge_loss | 12.554 | **+6.14%** |

**派生**：nudge 均值 −8.0%；nudge_loss 均值 **+5.9%**（相差 ≈14 个百分点，方向相反）。

## 4. 解读（保守）

- **未复现损失厌恶**：guide 预期 nudge_loss 应"比 nudge 多省 ~5%"，实测却**增耗**。
- 可能原因（未定论）：(a) n=1/2 天随机性；(b) LLM 对"失去补贴/被标记"的措辞产生**逆反/焦虑性**或
  不同解读；(c) 框架效应在 LLM 代理上不稳定。
- **限制**：单成员、样本极小；**不能**据此断言损失框架无效，但可作**反例**记录，提示：
  LLM 代理的框架效应对**措辞**高度敏感（与 R040 同源：措辞驱动 > 信息驱动）。

## 5. 论文更新

- `paper/experiments/nudge_loss.md`（初步 + 反例）；
- `paper/README.md` 状态更新；
- 在 `paper/99_discussion.md` Threats-to-validity 备注：框架效应在 LLM 代理上不稳定/可能反向。

## 6. token 消耗（估算）

- 本轮 1 臂 × (4 步 × 2 天) ≈ **8 次调用**。

## 7. 下一步（候选）

1. **多人户**重复 nudge / nudge_loss / nudge_soft（确认是否稳定）；
2. 政策时间线真调（习惯黏性）；
3. 若多人户仍复现"措辞主导"，可作为**方法学贡献**独立成节。
