# R172 — 需量电费 peak_demand（n=14）：**null**（峰 −7.5% n.s.，总电量 0.0%）

- **轮次**：Round 172
- **日期**：2026-09-12
- **验证层级**：**L2 真调 + L0/L1 熔断**（world_838587 h002 M1；计划 baseline×15 + `peak_demand`×15；**因网络中断实得 n=14**）
- **结论**：⚪ **null**：峰段 **−7.5%（t=−1.11, n.s.）**、总电量 **0.0%（t=0.00）**、谷期 −11.6%（n.s.）
  → 需量电费（Escarrega 2025 基准 峰值 −10~20%）**未达显著**。

---

## 1. 目标

将 `peak_demand`（需量电费）从 **n=3**（paper 现状）扩到 **n=15** 复核（Escarrega et al. 2025：峰值 −10~20%）。

## 2. 网络中断（goal.md §10 熔断）

- 跑至 **pair 12** 时 **DeepSeek DNS 中断**（`W10260 ConnectTimeout`，随后 `deepseek.com`/`github.com` 均**无法解析**）；
- 按 goal.md §10 切 **L0/L1**：**分析已产出的 14 对**并暂停 push（待网络恢复）。
- 代码改动：`compare_cpp.py` 增加**缺失对跳过**（`[skip] pair 12`），使部分数据可分析。

## 3. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pd_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pd_t_$i" --policy peak_demand --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pd_b --treat-prefix pd_t --n 15 --tag peak_demand
```

## 4. 结果（n=14，配对 t；pair 12 因断网缺失）

| 指标 | baseline | peak_demand | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.586 | 8.586 | **+0.0%** | +0.00 | 1.00（n.s.） |
| 峰段 16–21 | 3.850 | 3.560 | **−7.5%** | −1.11 | 0.29（n.s.） |
| 谷期 22–7 | 2.136 | 1.888 | −11.6% | −0.57 | 0.58（n.s.） |
| 峰值功率 | 3802 | 3906 | +2.7% | +0.36 | 0.72（n.s.） |

## 5. 解读

1. **peak_demand = null**：峰段名义 −7.5%（落在 Escarrega 区间 10–20% 的下缘之外），但 **n.s.**；
   总电量**完全不变**（0.0%）→ 若有效果也仅为"错峰"而非"省电"；
2. **与 n=3 null 一致**（R092）：扩样后仍不显著 → 需量电费信号（"错开大功率"）在**烹饪主导单户**上无效；
3. **机制一致性**：通用价格型（无设备靶向）不改变行为（对照 R157/R161/R164）；
4. **功效**：−7.5% 低于平台可分辨下限（R058），即便 n=15 也难判。

## 6. 论文更新

- `paper/README.md`：`peak_demand` 行状态更新为 "**n=14 same-era null**（峰 −7.5% n.s., 总 0.0%）"。

## 7. Validity / 待办

- ⚠️ **n=14**（<15，红线）；pair 12 待网络恢复后补跑；
- 单住户、单世界、单日。

## 8. token

- 约 **116 次调用**（14 对 × 2 臂 × ~4 call）。
