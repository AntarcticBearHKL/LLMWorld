# R219 — peak_demand + 具体需求电费成本：**仍 null**（未起死回生）

- **轮次**：Round 219
- **日期**：2026-09-12
- **验证层级**：**L1**（297 单测全绿，+1）+ **L2 真调**（world_838587 h002；baseline vs peak_demand+cost；共享 s4-only；n=15；~15 calls）
- **结论**：⚪ **null**：给 `peak_demand` 加上**具体需求电费金额表**后，峰 **−2.6%（t=−0.95, n.s.）**、
  总 −2.2% n.s.、峰值功率 −5.5% n.s. → **需求电费即使金额化也不削峰**（与 TOU/CPP 不同）。

## 1. 目的

R172 的 `peak_demand` null 是"**抽象描述**"（"最高 60 分钟按 12 AUD/kW"）。检验：**加具体金额**后是否同 TOU/CPP 一样"起死回生"。

## 2. 改动
- `src/engine/tariff.py`：新增 **demand 模式** `_render_demand_context()`——按每台柔性设备额定 kW 给出"若触发峰段将增加的需求电费"；
  `render_cost_context` 分派 demand 模式。
- `policy.parse_tariff("peak_demand")` → `{"mode":"demand","rate":12.0}`。
- `tests`：+1（demand 上下文）。**297 绿**。

## 3. 方法（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "pdem_$i" --policy peak_demand --cost-context --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix pctx_c --treat-prefix pdem --n 15 --tag peak_demand
```
注入示例：`- living_room_airconditioner: 2.0 kW → up to 24.00 AUD added to the demand charge if it sets the peak hour`

## 4. 结果（n=15）

| 指标 | baseline | peak_demand+cost | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 9.151 | 8.948 | −2.2% | −0.77 | 0.45（n.s.） |
| 峰段 16–21 | 2.885 | 2.810 | −2.6% | −0.95 | 0.36（n.s.） |
| 谷期 22–7 | 2.361 | 2.364 | +0.1% | +2.09 | 0.056 |
| 峰值功率 | 4839 | 4573 | −5.5% | −0.69 | 0.50（n.s.） |

## 5. 解读
1. **金额化也无效**：与 TOU（−13.2%）/CPP（−12.2%）"起死回生"不同，**需求电费仍 null**；
2. **机制差异**：`peak_demand` 收费基于**全天最高的 60 分钟**（一个**全局耦合**约束），而 TOU/CPP 是**时段价格**（可直接"移出窗口"）；
   agent 能执行"避开某窗口"，但**不擅长"错开设备同时启动以压低全天最大值"**这种**全局优化**；
3. **对文献**：Escarrega 2025 的需量管理为原型工具（实时反馈辅助），本平台**缺乏该耦合认知** → 与 R172 一致；
4. **结论**：**价格可分析 ≠ 所有价格工具都可分析**——**时段型有效、需量型无效**。

## 6. 论文更新
- `paper/README.md` peak_demand 行 / `99_discussion`：补"金额化仍 null（R219）；时段型有效、需量型无效"。

## 7. token
- 约 **15 次调用**。
