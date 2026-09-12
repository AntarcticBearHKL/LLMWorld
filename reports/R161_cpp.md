# R161 — 尖峰电价 CPP：**降总量 −14.4% 但不削晚峰**（节能≠削峰；与 R157 "税反升" 相反）

- **轮次**：Round 161
- **日期**：2026-09-12
- **验证层级**：**L1**（276 单测全绿，+4 CPP 测试）+ **L2 真调**
  （world_838587 h002 M1；baseline×15 + `cpp`×15 + `cpp_soft`×15；**~180 calls**）
- **结论**：✅ **总量 −14.4%（t=−3.17, p=0.007）**；⚪ **峰段 −2.7%（t=−0.34, p=0.74, n.s.）** →
  **CPP 节能但不削峰**；对照 `cpp_soft`（仅事实）总量 −10.9%（p=0.034）→ 效应主要来自"高价事实"。

---

## 1. 目标

补齐 guide §2.1 / Faruqui & Sergici (2010) 的**尖峰电价 (CPP)**能力缺口（此前只有 TOU）：
把"17:00–20:00 高价 critical peak"作为**自然语言政策**注入，检验**是否削峰**（文献基准：CPP 削峰 **13–20%**，
远强于纯 TOU 的 3–6%），并加 **prompt-bias 对照**（`cpp_soft`：只给价格事实、不含"shift/avoid"指令）。

## 2. 改动（最小）

- `src/engine/policy.py`：新增 `render_cpp_policy()`（含 shift 指令）与 `render_cpp_soft_policy()`（仅事实）；
  注册 `cpp`/`cpp_soft`（`cpp[:<peak_rate>]`，默认 0.90 AUD/kWh，窗口 17:00–20:00）。**只改注入文本，不动计算逻辑。**
- `tests/test_core_logic.py`：+4 测试（默认/自定义费率/soft 无指令/组合）。
- `src/analyze/compare_cpp.py`：配对比较脚本（复用 `dataset.iter_house_days`）。
- 回滚：`git checkout src/engine/policy.py tests/test_core_logic.py`（纯增量，无风险）。

## 3. 方法（可复现）

```powershell
# same-era 交错，n=15 每臂；显式 --date
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "cpp_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "cpp_c_$i" --policy cpp --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "cpp_s_$i" --policy cpp_soft --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix cpp_b --treat-prefix cpp_c --n 15 --tag cpp
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix cpp_b --treat-prefix cpp_s --n 15 --tag cpp_soft
```

## 4. 结果（n=15，配对 t，df=14）

| 指标 | baseline | cpp | Δ | t | p |
|---|---|---|---|---|---|
| **总电量** | 8.766 | 7.505 | **−14.4%** | **−3.17** | **0.007** |
| **峰段 16–21** | 3.581 | 3.485 | **−2.7%** | −0.34 | 0.74（n.s.） |
| 峰值功率 (max W) | 4333.1 | 3606.6 | −16.8% | −1.69 | 0.11（n.s.） |
| InductionCooker | 2.645 | 2.234 | −15.5% | −2.03 | 0.062 |
| Kettle | 0.757 | 0.402 | −46.9% | −1.92 | 0.075 |
| WaterHeater | 1.750 | 1.500 | −14.3% | −1.10 | 0.29 |
| AirConditioner | 0.160 | 0.000 | −100% | −1.00 | 0.33 |

**对照 `cpp_soft`（仅价格事实，无 shift 指令）**：

| 指标 | baseline | cpp_soft | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.766 | 7.809 | **−10.9%** | −2.35 | **0.034** |
| 峰段 16–21 | 3.581 | 3.327 | −7.1% | −1.50 | 0.156（n.s.） |
| InductionCooker | 2.645 | 2.589 | −2.1% | −0.26 | n.s. |

## 5. 解读

1. **CPP 节能但不削峰**：总电量显著 −14.4%，峰段 **−2.7% n.s.** → 再次确认 headline **"节能 ≠ 削峰"**。
2. **与文献不对齐（峰）**：Faruqui & Sergici (2010) 报 CPP 削峰 **13–20%**；本平台 CPP **峰段 null**。
   → 记录为 **null（峰指标）**；与 R157（通用晚峰税不削峰）方向一致。
3. **与 R157 反升相反**：R157 自定义通用晚峰税 = 峰 **+18.9%**、总 **+15.5%**；本轮 CPP（`--policy` 路径）
   = 总 **−14.4%**、峰 −2.7%。差异提示 **注入路径（custom event vs policy）/ 措辞（tax vs critical peak pricing）
   是混淆变量** —— 支持 R157/R158 的结论。
4. **prompt-bias 控制**：`cpp_soft`（无指令）仍降总 −10.9%（p=0.034）→ **主效应来自"高价事实"本身**，
   指令额外贡献约 3.5pp（−14.4% vs −10.9%）；**两臂均不削峰** → 削峰结论稳健。
5. **机制**：CPP 靠削减烹饪/热水壶/热水器用量降总量（炊具 −15.5% p≈0.06、壶 −46.9%），
   但**烹饪主导的晚峰抵抗削峰**（R151/R144/R156 的替代约束）。

## 6. 文献对比

| 来源 | 预期 | 本研究 |
|---|---|---|
| Faruqui & Sergici 2010 — CPP 削峰 13–20% | 峰显著降 | **峰 null（−2.7%）** ❌ |
| 本研究 headline — 节能≠削峰 | 总量↓、峰不动 | **成立** ✅ |
| R157 — 通用晚峰"税"（custom）反升 | 峰↑ | CPP（policy）峰 −2.7% → **路径/措辞不同** |

## 7. Validity

- **same-era 配对交错**（baseline/cpp 同 i 紧邻），n=15 达红线；
- **prompt-bias 对照**（cpp_soft）；
- 限制：单住户（h002 M1，烹饪主导）、单世界、单日；跨世界未验。**外推需跨住户/世界**。

## 8. 结论

CPP = **"节能型"政策**：显著降总电量（−14.4%，p=0.007）但**不削晚峰**（−2.7%，n.s.）。
与 Faruqui CPP 削峰基准**不对齐**（记 null）；与 R157 通用"税"反升**相反**（注入路径/措辞混淆）。
控制实验（cpp_soft）表明主要为"高价事实"驱动。**新增 `cpp`/`cpp_soft` 政策能力 + 4 测试（276 绿）。**

## 9. token

- 约 **180 次调用**（baseline×15 + cpp×15 + cpp_soft×15，各 ~4 call/run）。
