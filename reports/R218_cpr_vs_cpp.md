# R218 — CPR（尖峰返利）vs CPP（尖峰税）：**奖≈罚，框架不影响**

- **轮次**：Round 218
- **日期**：2026-09-12
- **验证层级**：**L1**（296 单测全绿，+3）+ **L2 真调**（world_838587 h002；共享 s4-only 时间线；n=15；~30 calls）
- **结论**：✅ **两者等效**：`cpr`（奖）相对 baseline **峰 −13.7% / 谷 +27.9%**（p≤0.001），
  与 `cpp`（罚，峰 −13.2%/谷 +25.6%）相当；**CPR vs CPP 直接对比无差异（峰 +0.3% n.s.）** →
  **奖励 vs 惩罚框架不改变行为**（具体窗口+金额才是关键）。

## 1. 目的

Faruqui & Sergici 2010：CPP（尖峰**罚**）与 CPR（尖峰**奖**）。新增 `cpr` 检验**奖/罚框架**差异。

## 2. 改动
- `src/engine/policy.py`：新增 `render_cpr_policy()`/`render_cpr_soft_policy()`（CPR，窗口 17–20）；
  注册 `cpr`/`cpr_soft`；`parse_tariff("cpr")` 返回"机会成本"型费率（peak_rate=返利，valley=0）→ cost-context 可用。
- `tests/`：+3（cpr 文本/soft/tariff）。**296 绿**。

## 3. 方法（可复现）

```powershell
# 共享 cpp_b_1 的 s1–s3；两臂均 --cost-context
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pcpp_$i" --policy "cpp:0.9" --cost-context --s4-only --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pcpr_$i" --policy "cpr:0.9" --cost-context --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pcpp --treat-prefix pcpr --n 15 --tag cpr --base-tag cpp    # CPR vs CPP
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pctx_c --treat-prefix pcpr --n 15 --tag cpr             # CPR vs baseline
```

## 4. 结果（n=15）

**① CPR vs baseline（奖是否有效）**
| 指标 | baseline | CPR+cost | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 2.885 | 2.489 | **−13.7%** | **−4.15** | **0.0009** |
| **谷期 22–7** | 2.361 | 3.020 | **+27.9%** | **+7.51** | **3e-7** |
| 总电量 | 9.151 | 9.137 | −0.2% | −0.05 | 0.96（n.s.） |

**② CPR vs CPP（奖 vs 罚）**
| 指标 | CPP+cost | CPR+cost | Δ | t | p |
|---|---|---|---|---|---|
| 峰段 | 2.481 | 2.489 | +0.3% | +0.12 | 0.91（n.s.） |
| 谷期 | 3.017 | 3.020 | +0.1% | +0.02 | 0.98（n.s.） |
| 总电量 | 9.270 | 9.137 | −1.4% | −0.63 | 0.54（n.s.） |

## 5. 解读
1. **CPR 有效**（峰 −13.7%/谷 +27.9%）→ 与 CPP 同量级；
2. **奖 = 罚**（直接对比 n.s.）→ **框架（gain vs loss）不影响**，只要**窗口+具体金额**给定；
3. **对文献**：Faruqui 的 CPP/CPR 都能削峰；本平台**两者等效**——与 R041（损失框架不稳定）区别在于**此处有具体金额**，框架被"具体化"抹平；
4. **政策含义**：设计时可选更低政治阻力的"返利版"（CPR），效果与征税相当。

## 6. 论文更新
- `paper/README.md` / `99_discussion.md`：补 **CPR ≈ CPP（R218）**。

## 7. token
- 约 **30 次调用**。
