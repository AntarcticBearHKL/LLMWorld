# R034 — 恢复社会规范政策 `nudge` / `nudge_loss`（guide §3.1/§3.2）

- **轮次**：Round 34
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 255/255 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（drift，R34 扫描发现）**：`intervention_experiment_guide.md` §1/§3 列出的社会规范干预
`--policy nudge`、`--policy nudge_loss`（以及 subsidy/peak_demand/ev_delay/night_setback/in_home_display）
在 `engine/policy.py` 中**均未实现**——此前只有 `tou`/`tou_soft`。这是比 R9 更大的漂移面。

**期望**：先恢复最核心的两项**社会规范**干预（RQ2 非价格干预的基准）：
- `nudge`：固定邻居均值的社会比较文本（guide §3.1）；
- `nudge_loss`：损失框架（不省电则失去补贴，guide §3.2）。

## 2. 依据

- `intervention_experiment_guide.md` §3.1（nudge，Allcott 2011：−2%；高耗家庭更强）、
  §3.2（nudge_loss，Ghesla 2019：比增益框架多 ~5%）。
- 研究计划 §2.7（非价格行为干预的实证基准）。
- 研究语义红线：仅自然语言注入，效果涌现。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/policy.py` | 新增 `render_nudge_policy(neighbor_kwh=18.0)` 与 `render_nudge_loss_policy(rebate=30.0)`；`parse_policy_arg` 支持 `nudge`、`nudge:<kwh>`、`nudge_loss`、`nudge_loss:<aud>`；更新错误信息 |
| `tests/test_core_logic.py` | 新增 4 项 nudge/nudge_loss 用例；原"未知政策"用例由 `nudge` 改为真正未知的 `meteor` |

**用法**：
```powershell
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 --policy nudge
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 --policy nudge_loss
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 255 tests - OK
```

覆盖：`nudge` 默认文本（含 neighbours/18）、`nudge:12`（含 12 kWh）、
`nudge_loss` 默认（含 rebate/30 AUD）、`nudge_loss:50` 标签；未知政策仍抛错。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 255 tests — OK**（轮前 251 + 本轮 4） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思与教训

- **教训（重要）**：把 `nudge` 设为合法政策后，原"未知政策"用例失效 → 已改用 `meteor`。
  这提示：新增可选值时，须同步审查依赖"该值非法"的既有测试。
- **剩余漂移**：`subsidy` / `peak_demand` / `ev_delay` / `night_setback` / `in_home_display`
  仍未实现（价格类与行为引导类），列为后续轮次。
- 属能力恢复；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. 恢复其余价格/行为引导政策（`subsidy`/`peak_demand`/`ev_delay`/`night_setback`/`in_home_display`）；
2. `nudge` vs `--peer-nudge` 对照实验（固定文本 vs 真实邻居均值）；
3. 多人户实验以分离政策信号与噪声。
