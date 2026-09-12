# R188 — ac_tax **无热浪**对照：**null**（AC 未开 → 无可削）

- **轮次**：Round 188
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002 M1；baseline×9 + `ac_tax`(preset)×9；~72 calls）
- **结论**：⚪ **null**：无热浪时 **AC = 0.000 kWh（未开）**，ac_tax 使峰 −4.1%（n.s.）、总 −6.1%（n.s.）
  → 证实 **ac_tax 削峰以"AC 正在运行（热浪）"为前提**。

---

## 1. 目的

机制对照：`ac_tax` headline（峰 −22.5%）是否**依赖热浪**（即 AC 已开启）？无热浪时 AC 应关闭 → 无靶可削。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..9) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "aconly_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "aconly_t_$i" --event-template "2026-09-11|ac_tax" --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix aconly_b --treat-prefix aconly_t --n 9 --tag baseline
```

## 3. 结果（n=9，无热浪）

| 指标 | baseline | ac_tax | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.569 | 8.048 | −6.1% | −0.55 | 0.60（n.s.） |
| 峰段 16–21 | 3.570 | 3.423 | −4.1% | −0.35 | 0.73（n.s.） |
| 谷期 22–7 | 1.677 | 1.386 | −17.4% | −0.69 | 0.51（n.s.） |
| **AirConditioner** | **0.000** | **0.000** | — | — | AC **未开** |

## 4. 解读

1. **AC 未开**（两臂 0.000）→ 无热浪时空调不使用，ac_tax **无靶可削**；
2. **无显著效应**（峰 −4.1% n.s.）→ 与 R118（有热浪：峰 −22.5%，AC 15/15→7/15）**对照**；
3. **机制结论**：`ac_tax` 削峰 = **设备运行（热浪）× 设备+窗口锚定 × 可关闭性** 三者共同作用；
   → **事件效应是条件性的**（与 R082 基线特异一致）。

## 5. 论文更新

- `paper/99_discussion.md`：补"ac_tax 以热浪（AC 运行）为前提（R188 对照）"。

## 6. token
- 约 **72 次调用**。
