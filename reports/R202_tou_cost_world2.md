# R202 — TOU+cost 跨世界复现（W2）：**峰 −5.0% / 谷 +8.2%**（均显著）

- **轮次**：Round 202
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002；baseline×15 vs TOU+cost×15；共享 s4-only 时间线；~30 calls）
- **结论**：✅ **跨世界复现**：**峰 −5.0%（t=−2.89, p=0.012）、谷 +8.2%（t=+3.10, p=0.008）**，总量 +0.2% n.s.
  → 价格移峰**跨 2 世界成立**（W1 −13.2%/+25.6%）。

## 1. 方法（可复现）

```powershell
# 复制 hol2_b_1（world_172148 h002 baseline）的 s1–s3 到各 arm env；共享时间线
python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "pctx2_c_$i" --s4-only --workers 1
python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --date 2026-09-11 --env "pctx2_b_$i" --policy "tou:0.9,0.18" --cost-context --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix pctx2_c --treat-prefix pctx2_b --n 15 --tag tou
```

## 2. 结果（n=15）

| 指标 | baseline | TOU+cost | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 2.872 | 2.727 | **−5.0%** | **−2.89** | **0.012** |
| **谷期 22–7** | 2.538 | 2.748 | **+8.2%** | **+3.10** | **0.008** |
| 总电量 | 10.656 | 10.681 | +0.2% | +0.13 | 0.90（n.s.） |

## 3. 两世界对照

| 世界 | 峰段 Δ | 谷期 Δ |
|---|---|---|
| W1 `838587` h002（R201） | **−13.2%**（p=0.0018） | **+25.6%**（p=2.3e-5） |
| W2 `172148` h002（本轮） | **−5.0%**（p=0.012） | **+8.2%**（p=0.008） |

## 4. 解读
1. **两世界均显著移峰**（峰↓谷↑、总量不变）→ cost-context 的效果**跨世界稳健**（幅度世界相关）；
2. **机制一致**：柔性设备（洗碗机等）移至谷段；
3. 与 W1 幅度差（−13% vs −5%）→ 与各户柔性负荷占比/基线作息有关（同 stay-home 剂量逻辑）；
4. **待第 3 世界**（world_143345）达 cross-3-world。

## 5. 论文更新
- `paper/README.md` TOU 行：补"跨 2 世界（W1 −13.2%/W2 −5.0%）"。

## 6. token
- 约 **30 次调用**。
