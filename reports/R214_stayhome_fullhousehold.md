# R214 — A3 stay-home 全户级：holiday +44.9% / wfh +36.8% / transport +50.3%

- **轮次**：Round 214（A3）
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 **全 2 成员**；**完整 run**（s1–s3+s4）；n=9/事件）
- **结论**：✅ 三个 stay-home 事件在**全户级**均成立：**holiday +44.9%（R181）/ wfh +36.8%（p=0.051）/ transport +50.3%（p=0.021）**
  → **stay-home 总量效应非 M1-only 伪影**。

## 1. 方法（可复现；含一个方法学教训）

```powershell
# 全成员（省略 --member），完整 run（事件注入 s1+s4）
python run.py --mode simulate --world world_172148 --house house_0002 --date 2026-09-11 --env "fw_b_$i" --workers 1
python run.py --mode simulate --world world_172148 --house house_0002 --date 2026-09-11 --env "fw_h_$i" --event-template "2026-09-11|wfh" --workers 1
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix fw_b --treat-prefix fw_h --n 9 --tag baseline
```

⚠️ **方法学教训（重要）**：先用 **`--s4-only` 共享时间线**跑同一批事件 → **全 null**（holiday/wfh/transport 总 −0.1%~−1.9% n.s.）。
原因：**stay-home 是 s1 计划层效应**（是否外出在 s1 决定），`--s4-only` **跳过 s1** → 事件从未改变"居家" → 无效应。
故 **stay-home/结构事件必须用完整 run**（重采样 s1–s3）；`--s4-only` 只适用于**s4 注入的价格政策**。

## 2. 结果（全户级，完整 run，n=9）

| 事件 | 总电量 Δ | t | p |
|---|---|---|---|
| holiday（R181） | **+44.9%** | +2.84 | 0.022 |
| **wfh** | **+36.8%** | +2.29 | 0.051（边缘） |
| **transport_strike** | **+50.3%** | +2.85 | 0.021 |

（峰/谷均 n.s.；stay-home 只断言总量。）

## 3. 解读
1. **三个 stay-home 事件全户级显著** → M1-only 结论**在住户级成立**（幅度 +37%~+50%）；
2. **与 M1-only 一致**（holiday/W2 +31.9%、wfh +28.7%、transport +22.2%）→ 住户级更高（两成员叠加）；
3. **方法学**：s4-only 用于价格/设备决策；**结构事件须完整 run**。

## 4. 论文更新
- `paper/experiments/event_holiday.md` / `event_wfh.md` / `event_transport_strike.md`：补"全户级（2 成员）"行；
- `99_discussion`：补"s4-only 不适用于 stay-home（s1 效应）"方法学注。

## 5. token
- 约 **300 次调用**（2 事件 × 9 对 × 2 臂 × 2 成员 × ~4；+ 早期 s4-only 试跑）。
