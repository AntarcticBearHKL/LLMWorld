# R204 — CPP + 成本上下文：**峰 −12.2% / 谷 +23.2%**（cost-context 推广到尖峰电价）

- **轮次**：Round 204
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002；baseline×15 vs CPP+cost×15；共享 s4-only 时间线；~15 calls）
- **结论**：✅ **CPP 也生效**：CPP(1.2 AUD) + 成本表 → **峰 −12.2%（t=−3.45, p=0.004）、谷 +23.2%（t=+5.31, p=1.3e-4）**
  → 而 **CPP 纯文本**（R161）**峰 null** → **cost-context 修正可推广到多种价格政策**。

## 1. 方法（可复现）

```powershell
# 共享 cpp_b_1 的 s1–s3
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pcp_b_$i" --policy "cpp:1.2" --cost-context --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pctx_c --treat-prefix pcp_b --n 15 --tag cpp
```

## 2. 结果（n=15）

| 指标 | baseline | CPP+cost | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 2.885 | 2.532 | **−12.2%** | **−3.45** | **0.004** |
| **谷期 22–7** | 2.361 | 2.909 | **+23.2%** | **+5.31** | **1.3e-4** |
| 总电量 | 9.151 | 9.392 | +2.6% | +1.06 | 0.31（n.s.） |
| Dishwasher | 0.459 | 0.733 | +59.7% | +5.29 | 1.4e-4 |

## 3. 对照（同户 W1 h002）

| 干预 | 峰段 | 判定 |
|---|---|---|
| CPP 纯文本（R161） | −2.7% n.s. | ⚪ null |
| **CPP + cost-context（本轮）** | **−12.2%（p=0.004）** | ✅ 移峰 |
| TOU + cost（R201） | −13.2%（p=0.0018） | ✅ 移峰 |

## 4. 解读
1. **cost-context 通用**：把"价格文本"变"可执行金额+授权"后，TOU 与 CPP 均显著移峰；
2. **纯移峰**（峰↓谷↑、总量不变）；
3. **机制一致**：与 R200/R201 同——**信息具体化 + 授权动作**是价格生效的充分条件。

## 5. 论文更新
- `paper/README.md` CPP 行：补"**+cost-context 后峰 −12.2%/谷 +23.2%（R204）**"。

## 6. token
- 约 **15 次调用**。
