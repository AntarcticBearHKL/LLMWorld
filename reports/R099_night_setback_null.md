# R099 — `night_setback`：未降采暖（单例反而上升）→ null

- **轮次**：Round 99
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 house_0002；cold_snap + night_setback vs cold_snap only；~4 calls）
- **结论**：⚪ **null/反向**：night_setback 未降采暖（10.2→14.2 kWh，+39%，单例噪声内）

---

## 1. 目标（B2 续）

`night_setback`（夜间回温建议，guide §4.1 期望采暖 −5~10%）需冷天场景。本轮用 `cold_snap`
（已知启用采暖）作背景，测 night_setback 是否降低采暖能耗。

## 2. 设计（可复现）

```powershell
# baseline：cold_snap only（复用 R062 cold_run）
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --days 1 `
  --env ns_run --event-template "2026-09-11|cold_snap" --policy night_setback --workers 1
```

## 3. 结果（2026-09-11）

| 臂 | 采暖 kWh | 总 kWh |
|---|---|---|
| cold_snap only | 10.200 | 21.140 |
| **cold_snap + night_setback** | **14.200** | **25.341** |

- 采暖 **+39%**（未下降）；总电量 +20%。

## 4. 解读

- **未观察到回温节能**（反而上升）——与 guide §4.1 期望（−5~10%）**不符**；
- **限制**：**单例**（n=1），波动大，不能据此断言"有害"；但**无证据**支持其节能；
- 与主线一致：**软行为引导（nudge/nudge_loss/night_setback/in_home_display）在 LLM 代理上效应弱/不稳**；
  只有**改行为结构的大效应事件**稳健。

## 5. token 消耗（估算）

- 1 个 run × (4 步 × 1 成员 × 1 天） ≈ **4 次调用**。

## 6. 论文更新

- `paper/experiments/night_setback.md`：第 5 节填 null（单例），状态“初步(null)”。

## 7. 结论

`night_setback` **null**（无节能证据）；B2 占位实验现完成 **peak_demand / in_home_display / night_setback**
三项（皆 null / 不显著），印证"软干预不可判"。
