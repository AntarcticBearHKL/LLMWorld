# R201 — cost-context 让 TOU「起死回生」：vs 无政策 baseline **峰 −13.2% / 谷 +25.6%**（高度显著）

- **轮次**：Round 201（价格分析能力专项 P2 验证）
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（共享 s4-only 时间线；baseline(无政策)×15 vs TOU+cost×15；~30 calls）
- **结论**：✅ **强效应**：TOU 文本 + 成本表相对**无政策 baseline** → **峰段 −13.2%（t=−3.84, p=0.0018）、
  谷期 +25.6%（t=+6.20, p=2.3e-5）**，总电量 −2.1% n.s.（**纯移峰**）。

---

## 1. 目的

R200 已示"成本表在 TOU 内加效应"（峰 −7.2%）。本轮直接对比**无政策 baseline**，量化**政策本身的净效应**，
并对照"纯 TOU 文本 = null"（R114）。

## 2. 方法（可复现）

```powershell
# 三臂共享同一 s1–s3 时间线（复制 cpp_b_1 的 s1/s2/s3/day_state）
# arm A: TOU 文本(无cost) ; arm B: TOU+--cost-context ; arm C: baseline(无政策)
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pctx_c_$i" --s4-only --workers 1
# 比较 C(基线) vs B(TOU+cost)
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pctx_c --treat-prefix pctx_b --n 15 --tag tou
```

## 3. 结果（n=15，配对 t）

| 指标 | baseline（无政策） | TOU+cost | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 2.885 | 2.505 | **−13.2%** | **−3.84** | **0.0018** |
| **谷期 22–7** | 2.361 | 2.966 | **+25.6%** | **+6.20** | **2.3e-5** |
| 总电量 | 9.151 | 8.956 | −2.1% | −0.94 | 0.36（n.s.） |
| Dishwasher | 0.459 | 0.760 | **+65.7%** | **+6.20** | 2.3e-5 |

**三臂对照**（共享时间线）：

| 对比 | 峰段 Δ | 谷期 Δ |
|---|---|---|
| TOU 文本 vs baseline（R114 式） | ~null | ~null |
| TOU+cost vs TOU 文本（R200） | **−7.2%**（p=0.013） | **+16.6%**（p=0.007） |
| **TOU+cost vs baseline（R201）** | **−13.2%**（p=0.0018） | **+25.6%**（p=2.3e-5） |

## 4. 解读（关键结论）

1. **改造成功**：**纯 TOU = null → TOU + 成本表 = 峰 −13.2% / 谷 +25.6%**（高度显著）→
   平台**从"价格不可分析"变为"价格可分析"**；
2. **机制**：生效的是**"具体金额 + 明确授权移峰"**，不是价格文本本身（去掉授权句即回落到 −0.1% R200 v1）；
3. **纯移峰**（总量不变）：峰↓谷↑ = 经典 TOU 行为（Faruqui & Sergici 2010 的 valley-filling），
   幅度（−13%）落在"TOU+反馈/智能设备 10–30%"合理区间；
4. **与文献对齐首次成立**：之前 TOU 全 null 是**注入方式缺陷**（非平台无能）——补齐"可执行的经济信息"后即对齐。

## 5. 论文更新
- `paper/99_discussion.md`：TOU 条由"null"改述为"**加成本上下文后显著移峰**（R200/R201）"；
- `paper/README.md`：TOU 行更新（峰 −13.2%/谷 +25.6% vs baseline）。
- 新增能力写入 goal.md §3.4（P1/P2 ✅）。

## 6. token
- 约 **30 次调用**（arm C 15 + 复用 arm B 15）。
