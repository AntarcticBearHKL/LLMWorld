# R220 — 价格 × 社会框架：**nudge / nudge_loss 叠加到具体价格上均无效应**

- **轮次**：Round 220
- **日期**：2026-09-12
- **验证层级**：**L1**（297 单测全绿）+ **L2 真调**（world_838587 h002；3 臂共享 s4-only；n=15；~45 calls）
- **结论**：⚪ **社会/心理框架被具体价格"抹平"**：在 `tou+cost` 上叠加
  **`nudge`（社会规范）→ 峰 +1.4% n.s.**；**`nudge_loss`（损失框架）→ 峰 +4.7% n.s.** → **均无显著变化**。

## 1. 目的

- **Pellerano 2017**：社会规范 vs 货币激励（挤出？）。
- **Ghesla 2019**：损失框架是否更强（对照 R041 的反例——但那次**无具体金额**）。

## 2. 改动（含 bugfix）
- 修复 `policy.parse_tariff()`：组合政策串（如 `tou:0.9,0.18,nudge`）此前会因把 `nudge` 当费率而**抛异常**；
  现只解析**前导数值** token。**297 绿**。

## 3. 方法（可复现）

```powershell
# 共享 cpp_b_1 的 s1–s3；三臂均 --cost-context
python run.py ... --env "pnp_$i" --policy "tou:0.9,0.18"             --cost-context --s4-only
python run.py ... --env "pnn_$i" --policy "tou:0.9,0.18,nudge"        --cost-context --s4-only
python run.py ... --env "pnl_$i" --policy "tou:0.9,0.18,nudge_loss"   --cost-context --s4-only
# 以价格臂为基准
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pnp --treat-prefix pnn --n 15 --tag "tou+nudge" --base-tag tou
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pnp --treat-prefix pnl --n 15 --tag "tou+nudge_loss" --base-tag tou
```

## 4. 结果（n=15；基准=价格臂）

**① +社会规范 `nudge`**
| 指标 | 价格 | 价格+nudge | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 9.119 | 9.032 | −1.0% | −0.37 | 0.72（n.s.） |
| 峰段 | 2.509 | 2.544 | +1.4% | +0.43 | 0.67（n.s.） |
| 谷期 | 2.965 | 3.021 | +1.9% | +0.58 | 0.57（n.s.） |

**② +损失框架 `nudge_loss`**
| 指标 | 价格 | 价格+nudge_loss | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 9.119 | 9.036 | −0.9% | −0.37 | 0.72（n.s.） |
| 峰段 | 2.509 | 2.626 | +4.7% | +1.59 | 0.13（n.s.） |
| 谷期 | 2.965 | 2.691 | −9.2% | −1.78 | 0.10（n.s.） |

## 5. 解读
1. **两者均**不显著**改变**具体价格的效果 → **社会/心理框架被"具体化价格"抹平**；
2. **对 Pellerano**：**未见叠加**（更接近"无效"而非"挤出"）；具体价格是主导信号；
3. **对 Ghesla**：损失框架**不再产生差异**（对照 R041 的反例——那里无具体金额，故框架主导；此处金额主导）；
4. **统一结论**（R215/R218/R220）：**只要给定窗口+具体金额，框架（奖/罚、gain/loss、社会规范）都不改变行为**。

## 6. 论文更新
- `paper/99_discussion.md`：补"R220 框架被具体价格抹平"。

## 7. token
- 约 **45 次调用**（+ 修复后重跑的 30）。
