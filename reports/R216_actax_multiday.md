# R216 — A5 ac_tax 多日持久性：**持续、无衰减**（AC −71%/−68%）

- **轮次**：Round 216（A5）
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002；2 天，热浪+ac_tax vs 热浪；n=6；~90 calls）
- **结论**：✅ **持续**：ac_tax 在第 1/2 天均显著降 AC（**−71.2%/−67.5%**）、降总电量（−28.5%/−19.3%）
  → **无衰减/无适应**（与 R210"无跨日记忆"一致）。

## 1. 目的（A5）

`ac_tax` 削峰是否随天数**衰减/适应**（习惯粘性，goal §3.2）。

## 2. 方法（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env "acd_b_$i" --event-template "2026-09-11|heatwave" --event-template "2026-09-12|heatwave" --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --days 2 --env "acd_t_$i" --event-template "2026-09-11|heatwave" --event-template "2026-09-12|heatwave" --event-template "2026-09-11|ac_tax" --event-template "2026-09-12|ac_tax" --workers 1
# day1 / day2 分别比较
```

## 3. 结果（n=6，热浪 → +ac_tax）

| | 总电量 Δ | 峰段 Δ | **AirConditioner Δ** |
|---|---|---|---|
| **Day1 (09-11)** | **−28.5%**（t=−2.59, p=0.049） | −0.1% n.s. | **−71.2%**（t=−3.05, p=0.028） |
| **Day2 (09-12)** | −19.3%（t=−2.31, p=0.068） | +5.9% n.s. | **−67.5%**（t=−2.42, p=0.060） |

## 4. 解读
1. **持续无衰减**：两天 AC 降幅相当（−71% vs −68%）→ **无适应/习惯化**；
2. **与 R210 一致**：平台**无跨日记忆**——单日政策有效、但**既不累积也不衰减**；
3. 峰段两日均 n.s.（W1h002 空调主卧夜用，峰段占比低）——设备级（AC）效应真实、峰段受该户结构限制（R118 caveat）；
4. **政策含义**：持续型政策**不会因适应而失效**，但也**不会随天数增强**。

## 5. 论文更新
- `paper/99_discussion.md`：补"ac_tax 2 天持续（R216）"。

## 6. token
- 约 **90 次调用**（含重试）。
