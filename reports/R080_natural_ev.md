# R080 — `--natural-ev` 消融：移除提示后仍 100% 谷期（天花板是内在的）

- **轮次**：Round 80
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_143345 house_0002 M2；`--s4-only --natural-ev`，**1 次调用**）
- **结论**：⚪ **天花板是内在的**：移除 overnight 提示后，EV 充电仍 **100% 谷期**（仅 30 min @23:30–24:00）

---

## 1. 目标

R076/R077 发现基线 EV 充电 100% 谷期，疑因 s4 prompt 预置"prefer overnight charging"。
本轮新增 **opt-in** `--natural-ev`（剥离该指示）并测试：移除提示后 EV 是否改为峰段/到即充。

## 2. 改动（代码）

| 文件 | 改动 |
|---|---|
| `src/steps/simulate/s4_appliance_decision.py` | 新增 `EV_OVERNIGHT_GUIDANCE` 常量与 `strip_ev_guidance(prompt)`；`run_step(..., natural_ev=False)` 时剥离该指示 |
| `run.py` | 新增 opt-in `--natural-ev`（默认关，**不改默认 prompt**） |
| `tests/test_natural_ev.py` | 3 个离线用例 |

## 3. 实验（可复现）

```powershell
# 复用基线 s1-s3 时间线，只重跑 s4（1 次调用）
copy output/simulation/world_143345/2026-09-11/house_0002/{s1,s2,s3}_*.json -> w143_nat/...
python run.py --mode simulate --world world_143345 --house house_0002 --member 1 --days 1 `
  --env w143_nat --s4-only --natural-ev --workers 1
```

## 4. 结果

| 臂 | EV charge_home 分钟（峰/谷/肩） | 谷期时段 |
|---|---|---|
| baseline（原 prompt） | 0 / **120** / 0 | 22:00–24:00 |
| **natural_ev（剥离提示）** | 0 / **30** / 0 | 23:30–24:00 |

**移除提示后仍 100% 谷期**（峰/肩段恒 0）。

## 5. 解读（关键）

- **天花板是内在的**：即使不提示"overnight"，agent 仍自发选择深夜充电 →
  说明**"夜间充电"是模型的常识性默认**，而非仅 prompt 造成；
- 因此 `subsidy`/TOU/`ev_delay` 的 **EV 峰移**在本平台**结构性无效应**（baseline 与处理均谷期）；
- 与主线一致：LLM 代理的**默认行为**可能已经位于干预目标态，使干预失去意义。

## 6. token 消耗（估算）

- `--s4-only` 复用时间线 → **1 次调用**。

## 7. 论文更新

- `paper/experiments/subsidy.md` / `ev_delay.md`：结论更新为"**EV 充电天花板是内在的**
  （连自然基线亦 100% 谷期，R080）→ 峰移类 EV 干预在本平台不可评估"。

## 8. 结论

- 新增 `--natural-ev` opt-in 能力（不改默认）；
- 证实 **EV 峰移干预的结构性 null**：不是 prompt 问题，而是 agent 默认即谷期充电。
