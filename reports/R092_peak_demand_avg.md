# R092 — 需量电费 `peak_demand` 多run平均：N=3 下 **null**

- **轮次**：Round 92
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_172148 house_0002 M1；baseline×3 vs peak_demand×3；~24 calls）
- **结论**：⚪ **null**：需求电费未削峰（峰值 +4.2%、峰段 −3.2%，均在噪声内）

---

## 1. 目标

B2（占位实验）+ C1（多run平均）合并：对**大效应候选** `peak_demand`（12 AUD/kW 需量电费）做
N=3 的 baseline/policy 对照，报告 mean±std 并检验是否削峰（guide §2.3 期望 −10~20%）。

## 2. 设计（可复现）

```powershell
# world_172148 house_0002 Member 1, 1 天；baseline (bp1-3) 与 peak_demand (pp1-3) 各 3 次
foreach ($i in 1,2,3) {
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env "bp$i" --workers 1
  python run.py --mode simulate --world world_172148 --house house_0002 --member 0 --days 1 --env "pp$i" --policy peak_demand --workers 1
}
```

指标：总电量、峰值 W、峰段(16–21) kWh，各取 mean/std。

## 3. 结果

| 指标 | baseline (n=3) | peak_demand (n=3) | 变化 |
|---|---|---|---|
| 总电量 kWh | 9.402 ± 0.624 | 9.491 ± 0.125 | +0.9% |
| **峰值 W** | **3183 ± 94** | **3316 ± 163** | **+4.2%**（未降） |
| **峰段 kWh** | **3.753 ± 0.620** | **3.633 ± 1.062** | **−3.2%**（噪声内） |

- 峰值**反而名义上升 4.2%**（远小于两臂 std）；峰段仅 −3.2%，而 baseline 峰段 **CV≈17%**。

## 4. 解读

- **无削峰**：需求电费在本设置下未产生可检出的峰削减（期望 −10~20% 未出现）；
- 变化量远小于噪声 → 与 R057/R058 一致：**效应未超噪声地板则不可判**；
- 也符合本工作主线：**软/价格干预（非结构改变）效应弱且噪声大**；只有改行为的**大效应事件**稳健。
- **限制**：n=3、单成员、1 天；但即便按此噪声，−3% 也远不足以支持 guide 的 −10~20% 期望。

## 5. token 消耗（估算）

- 6 个 run × (4 步 × 1 成员 × 1 天) ≈ **24 次调用**。

## 6. 论文更新

- `paper/experiments/peak_demand.md`：第 5 节填初步结果（N=3 null），状态“初步(null)”。

## 7. 附带结论（C2）

- **C2（EV prompt 重设计）判定为 moot**：R080 已证即使 `--natural-ev`（剥离 overnight 提示），
  EV 仍 100% 谷期 → **EV 峰移天花板是内在的**，改默认 prompt **无效**（不改）。

## 8. 结论

`peak_demand` 在 N=3 平均下 **null**；C2 无效（内在天花板）。
下一步候选：B1 寒潮扩样（需干净采暖世界）；B3 更多“改行为结构”的大效应事件。
