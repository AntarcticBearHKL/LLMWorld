# R211 — B-x1 替代效应跨世界（world_172148 h001 全 5 成员）：**null**（炊具未动）

- **轮次**：Round 211（B-x1）
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h001 **全 5 成员**；baseline×5 vs 炊具峰税×5；共享 s4-only；~70 calls）
- **结论**：⚪ **null**：炊具峰税使 **InductionCooker +0.0%（逐字节不变）**、微波炉/烤箱 +0.0%、
  总峰 −2.4%（t=−1.54, n.s.）→ **该户未见替代效应**（与 R144/R149 的"炊具有响应→替代"不同）。

## 1. 目的（B-x1）

R155 曾因**只跑 M1**（该户烹饪不在 M1 峰段）而不 informative。本轮**全 5 成员**复检：靶向炊具 →
是否出现"炊具↓、烤箱/微波炉↑、总峰不变"的替代。

## 2. 方法（可复现）

```powershell
# 全成员种子（s1–s3），复制到两臂；共享时间线
$EV = "2026-09-11|Induction-cooker peak tax|A 10 percent tax applies to induction-cooker electricity use during the evening peak (5pm to 8pm) today; delaying cooking until after 8pm avoids the tax."
python run.py --mode simulate --world world_172148 --house house_0001 --date 2026-09-11 --env "sub_c_$i" --s4-only --workers 1
python run.py --mode simulate --world world_172148 --house house_0001 --date 2026-09-11 --env "sub_t_$i" --event $EV --s4-only --workers 1   # 复现前先清空 events.json 以防臂 c 污染
python src/analyze/compare_cpp.py --world world_172148 --house house_0001 --date 2026-09-11 --base-prefix sub_c --treat-prefix sub_t --n 5 --tag baseline
```

## 3. 结果（n=5，全成员）

| 指标 | baseline | 炊具税 | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 16.170 | 15.949 | −1.4% | −1.06 | 0.35（n.s.） |
| 峰段 16–21 | 5.119 | 4.997 | −2.4% | −1.54 | 0.20（n.s.） |
| **InductionCooker** | 2.523 | 2.523 | **+0.0%** | n/a | 不变 |
| Microwave | 0.048 | 0.048 | +0.0% | n/a | 不变 |
| Oven | 0.048 | 0.048 | +0.0% | n/a | 不变 |

## 4. 解读
1. **炊具逐字节不变** → 该户对炊具税**无响应**（既未削、也未替代）；总峰 −2.4% n.s.；
2. **与 R144/R149 对照**：那里是**自定义请求**触发替代（炊具 −99.7% → 烤箱/微波炉 +）；此处**炊具税未触发任何改变** →
   替代效应**未被复现**（跨世界/跨事件型）；
3. **可能原因**：该户烹饪本就不在峰段；n=5（screen）；炊具税文本未改变其决策；
4. **B-x1 结论**：**未复现替代**（null）；替代效应仍**仅见于 R144/R149**，外推性存疑。

## 5. 论文更新
- `paper/99_discussion.md`：补"B-x1 全成员未复现替代（R211，null）"。

## 6. token
- 约 **70 次调用**（种子 20 + 两臂 5×5×2）。
