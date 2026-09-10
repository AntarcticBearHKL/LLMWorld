# R048 — nudge 多成员配对（house_0001 M1/M2/M3）

- **轮次**：Round 48
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（house_0001 三个成员，各 1 天；nudge vs 同成员同日均 baseline）
- **结论**：✅ **方向跨成员稳健**（3/3 均下降 −12.3%~−23.3%），幅度**持续超 −1~3% 基准**（过度遵从）

---

## 1. 目标

R042/R047 指出"单次单成员不可信、需多成员平均"。本轮为 `nudge` 增加**配对样本**：
house_0001 的 Member 1/2/3，各做 nudge 与 baseline（同成员、同日期 2026-09-11）。

## 2. 设计（可复现）

```powershell
# Member 1: R043 的 ctrl_h1 vs nudge_h1
# Member 2
python run.py --mode simulate --world world_838587 --house house_0001 --member 1 --days 1 --env m2_ctl --workers 1
python run.py --mode simulate --world world_838587 --house house_0001 --member 1 --days 1 --env m2_nudge --policy nudge --workers 1
# Member 3
python run.py --mode simulate --world world_838587 --house house_0001 --member 2 --days 1 --env m3_ctl --workers 1
python run.py --mode simulate --world world_838587 --house house_0001 --member 2 --days 1 --env m3_nudge --policy nudge --workers 1
```

- 配对设计：同一成员、同一天，仅 s4 的政策文本不同（nudge vs 无）。
- 离线 `load_model.build_load_profile` 计算各成员总电量。

## 3. 结果（house_0001，2026-09-11）

| 成员 | baseline kWh | nudge kWh | 变化 |
|---|---|---|---|
| Member 1 | 10.081 | 8.409 | **−16.58%** |
| Member 2 | 10.566 | 9.266 | **−12.30%** |
| Member 3 | 12.609 | 9.677 | **−23.25%** |

**均值 ≈ −17.4%**，范围 **−12.3% ~ −23.3%**，**3/3 方向一致**。

## 4. 汇总（nudge 全样本）

| 住户 / 成员 | 变化 | 来源 |
|---|---|---|
| house_0002 M1 (09-11/12) | −10.29% / −5.76% | R037 |
| house_0001 M1 | −16.58% | R043 |
| house_0001 M2 | −12.30% | R048 |
| house_0001 M3 | −23.25% | R048 |

**5 个成员-日、2 个住户**：全部下降（−5.8% ~ −23.3%），**方向稳健**，**全部超 −1~3% 基准**。

## 5. 解读

- **方向可信**：多成员配对后，nudge 降耗方向**稳健**（首次达到"多成员证据"）。
- **幅度仍超基准**：−12~−23%（house_0001）远高于 −1~3% → 支持 **prompt 过度遵从**（R039/R040）。
- **样本内异质性**：成员间差异（−12 vs −23）提示**个体异质性可观测**（可对接 RQ3 分组）。

## 6. token 消耗（估算）

- 本轮 3 成员 × 2 臂 × (4 步 × 1 天) ≈ **24 次调用**（M1 复用 R043；实际本轮 4 run × 4 = 16）。

## 7. 论文更新

- `paper/experiments/nudge.md`：新增多成员配对小节与全样本汇总；结论强化为"**方向多成员稳健、幅度超基准**"。

## 8. 下一步（候选）

1. 同法为**热浪**（二进制）与 **TOU** 增多样本，形成"多成员平均"的方法学闭环；
2. 用 `analyze_groups.py` 看 nudge 响应的**个体异质性**是否与 awareness/尽责性相关（RQ3）。
