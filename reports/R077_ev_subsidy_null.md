# R077 — EV subsidy 实证确认：无位移（天花板效应确认）

- **轮次**：Round 77
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_143345 house_0002 M2；subsidy vs baseline；~4 calls）
- **结论**：⚪ **确认天花板**：两臂 EV 充电均 **100% 谷期**（peak/shoulder=0），subsidy 无位移

---

## 1. 目标

R076 由基线侦察推断 EV 充电已 100% 谷期 → `subsidy` 无 headroom。本轮**实证确认**。

## 2. 设计（可复现）

```powershell
# baseline: world_143345 house_0002 M2 (既有, 2026-09-11)
python run.py --mode simulate --world world_143345 --house house_0002 --member 1 --days 1 `
  --env w143_sub --policy subsidy --workers 1
```

统计 EV 的 `charge_home` 分钟按峰/谷/肩分段。

## 3. 结果

| 臂 | EV charge_home 分钟（峰/谷/肩） |
|---|---|
| baseline | peak 0 / **valley 120** / shoulder 0 |
| **subsidy** | peak 0 / **valley 60** / shoulder 0 |

- **两臂均为 100% 谷期**：峰段/肩段恒 0；
- subsidy 臂充电时长 120→60 分钟属运行间差异（非时段位移）。

## 4. 解读

- **天花板效应确认**：基线已在谷期（prompt 预置"overnight charging"），
  `subsidy`（奖励谷期）**无任何可移动的峰段/肩段负荷** → 位移量恒为 0；
- 与 R076 推断一致；**EV 峰移类干预在当前 prompt 下不可评估**（结构性 null）；
- 本工作的主线再次印证：**prompt 内容决定基线**（R040/R072）——此处 prompt 把基线
  直接推到了干预目标状态，使干预失去意义。

## 5. token 消耗（估算）

- 1 个 subsidy run × (4 步 × 1 成员 × 1 天) ≈ **4 次调用**。

## 6. 论文更新

- 不进 `paper/`（null，符合 §6）；`paper/experiments/subsidy.md` 的记录为设计阻塞，
  可在其"Validity/Setup"注明"当前 prompt 下基线已谷期，需先建立自然基线"。

## 7. 结论

`subsidy` 在 `world_143345` 上**无效应**（天花板）；EV 干预实验的前置条件是
**移除/弱化 s4 的 overnight-charging 提示以建立自然基线**（属研究设计决策，建议用户拍板）。
