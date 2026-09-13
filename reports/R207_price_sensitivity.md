# R207 — 价格敏感度剂量-反应：高敏感户移峰显著更强（峰 −7.0% / 谷 +14.6%）

- **轮次**：Round 207（P2 余项：price_sensitivity）
- **日期**：2026-09-12
- **验证层级**：**L1**（285 单测全绿，+1）+ **L2 真调**（world_838587 h002；低敏感 vs 高敏感，**两臂均 TOU+cost**；共享 s4-only；~30 calls）
- **结论**：✅ **异质性剂量-反应**：高价格敏感度户相对低敏感户 **峰 −7.0%（t=−2.80, p=0.014）、谷 +14.6%（t=+2.82, p=0.014）**
  → 同一价格政策下**响应随住户价格敏感度单调增强**。

## 1. 目的

补 P2 余项：给住户/成员加 **price_sensitivity**（成本意识），检验**异质性价格响应**（RQ3；Costa & Kahn 2010 的"同政策异构响应"、Wang 2021 的弹性异质）。

## 2. 改动
- `src/engine/tariff.py`：新增 `sensitivity_note(level)`（high/low 偏好句）；
- s4：`price_sensitivity` 参数 → 前置到 `{cost_context}`；
- `run.py --price-sensitivity {low,high}`；`tests/test_tariff.py` +1。**285 绿**。

## 3. 方法（可复现）

```powershell
# 共享时间线；两臂均 TOU+cost，仅敏感度不同
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pslo_$i" --policy "tou:0.9,0.18" --cost-context --price-sensitivity low  --s4-only --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pshi_$i" --policy "tou:0.9,0.18" --cost-context --price-sensitivity high --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pslo --treat-prefix pshi --n 15 --tag tou --base-tag tou
```

## 4. 结果（n=15，低敏感 → 高敏感）

| 指标 | 低敏感 | 高敏感 | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 2.669 | 2.481 | **−7.0%** | **−2.80** | **0.014** |
| **谷期 22–7** | 2.636 | 3.020 | **+14.6%** | **+2.82** | **0.014** |
| 总电量 | 9.251 | 9.141 | −1.2% | −0.52 | 0.61（n.s.） |
| Dishwasher | 0.596 | 0.788 | +32.2% | +2.82 | 0.014 |

## 5. 解读
1. **敏感度剂量-反应**：高成本意识户移峰显著更强 → 平台可做**住户异质性的价格响应**分析；
2. **机制一致**：成本表 + 敏感度措辞共同决定移峰强度；
3. **对齐文献**：Costa & Kahn（同政策异构响应）/ Wang（弹性异质）——本平台现可复现"同价格、不同响应"。

## 6. 论文更新
- `paper/99_discussion.md`：补"价格敏感度异质（R207）：高敏感户移峰更强"。

## 7. token
- 约 **30 次调用**。
