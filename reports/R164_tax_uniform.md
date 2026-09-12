# R164 — 统一电力税（Gunkel 2023）：**null**（不降总量，反而 +5.6% n.s.）

- **轮次**：Round 164
- **日期**：2026-09-12
- **验证层级**：**L1**（278 单测全绿，+2）+ **L2 真调**（world_838587 h002 M1；baseline×15 + `tax_uniform`×15；~120 calls）
- **结论**：⚪ **null**：统一税使总电量 **+5.6%（t=+1.00, n.s.）**、峰段 **+10.7%（n.s.）** —— **未减少用电**。

---

## 1. 目标（补未用参考论文）

`goal.md` §3.2 / 未用参考：**Gunkel et al. 2023** *Uniform Taxation of Electricity*（对**全部**用电统一征税、
含自产光伏，按户规模重分配成本）。其在行为层面的可测含义：**统一税（税基=总用电）应促使家庭降低总用电**。
实现 `--policy tax_uniform` 检验之（此前该论文**零实验**）。

## 2. 改动（最小）

- `src/engine/policy.py`：新增 `render_uniform_tax_policy()`（含"reduce total"指令）与
  `render_uniform_tax_policy_soft()`（仅事实）；注册 `tax_uniform` / `tax_uniform_soft`（`[:<rate>]`，默认 0.10 AUD/kWh）。
- `tests/test_core_logic.py`：+2 测试（默认/自定义费率；soft 无 reduce 指令）。**278 绿**。
- 回滚：`git checkout src/engine/policy.py tests/test_core_logic.py`。

## 3. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "tax_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "tax_t_$i" --policy tax_uniform --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix tax_b --treat-prefix tax_t --n 15 --tag tax_uniform
```

## 4. 结果（n=15，配对 t，df=14）

| 指标 | baseline | tax_uniform | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 7.866 | 8.305 | **+5.6%** | +1.00 | 0.33（n.s.） |
| 峰段 16–21 | 3.311 | 3.666 | +10.7% | +1.22 | 0.24（n.s.） |
| 谷期 22–7 | 2.121 | 1.833 | −13.6% | −0.70 | 0.50（n.s.） |
| 峰值功率 | 3693 | 3973 | +7.6% | +0.62 | 0.55（n.s.） |
| Kettle | 0.357 | 0.690 | **+93.3%** | **+2.09** | 0.055 |
| InductionCooker | 2.423 | 2.645 | +9.2% | +1.13 | 0.28 |

## 5. 解读

1. **统一税 = null**：总电量、峰段、谷期**均无显著下降**（甚至名义上上升）→ **税收型通用信号不改变用电行为**
   （与 `price_hike` 撤回、通用晚峰税反升 R157、CPP 峰值 null 一致）。
2. **与 Gunkel 机制的对齐失败（行为侧）**：Gunkel 是**经济学/优化**论文（税负重分配、光伏自消纳激励），
   平台**无账单核算/无光伏成本内生**，故其"成本再分配→行为"通道**不可观测**；本实验只测到"**税收措辞无行为效应**"。
   → Gunkel 更适合作为**政策设计背景引用**，而非可跑的**行为**实验（记入限制）。
3. **机制一致性**：再次印证 headline —— **通用价格/税信号 ≠ 设备+窗口靶向**；唯有 `ac_tax`（设备+窗口）削峰。
4. **命名提示**：`tax_uniform` 的边际价值低于 `cpp`；建议后续**不再重复**"通用税"变体。

## 6. Validity

- same-era 配对、n=15；单住户、单世界、单日。
- prompt-bias 对照 `tax_uniform_soft` 已实现（本轮未跑，因主臂已 null，按 goal.md §0.3 省 token）。

## 7. token

- 约 **120 次调用**（baseline×15 + tax×15）。
