# R035 — 恢复其余文档化政策（价格/行为引导，guide §2.2/§2.3/§2.4/§4.1/§4.2）

- **轮次**：Round 35
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 260/260 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（drift，R34 扫描发现）**：guide §1 能力表列出的
`subsidy`（谷期补贴）、`peak_demand`（需量电费）、`ev_delay`（EV 延迟激励）、
`night_setback`（夜间回温）、`in_home_display`（实时反馈）在 `engine/policy.py` 中**均缺失**。

**期望**：恢复这 5 项政策的**自然语言文本渲染**入口，使 guide 中的实验命令可直接运行。

## 2. 依据

- `intervention_experiment_guide.md` §2.2（subsidy 0.18 AUD/kWh，Alexeenko & Bitar 2023）、
  §2.3（demand charge 12 AUD/kW，Escarrega 2025）、§2.4（ev_delay，时间贴现）、
  §4.1（night_setback，Cabezas-Riviere 2025）、§4.2（in_home_display，Monacchi 2015）。
- 研究语义红线：仅自然语言注入，效果涌现。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/policy.py` | 新增 `render_subsidy_policy` / `render_peak_demand_policy` / `render_ev_delay_policy` / `render_night_setback_policy` / `render_in_home_display_policy`；`parse_policy_arg` 支持这 5 个名字（前 3 个可选数值参数）；错误信息列出全部支持项 |
| `tests/test_core_logic.py` | 新增 5 项用例 |

**用法**：
```powershell
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 --policy peak_demand
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 --policy "subsidy:0.25"
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 260 tests - OK
```

覆盖：各政策默认文本关键短语（off-peak/0.18、12 AUD/kW、0.02 AUD/kWh、set heating/cooling back、
in-home display）与自定义数值；标签正确。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 260 tests — OK**（轮前 255 + 本轮 5） |

**是否符合预期**：是。至此 guide §1 能力表的**全部干预入口均已具备**：
TOU/TOU-soft、nudge、nudge_loss、subsidy、peak_demand、ev_delay、night_setback、in_home_display +
news（10 模板/自定义）、community-notice、policy-schedule、peer-nudge。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思与限制

- 这些政策**尚未真调验证效果**；文本已就绪，可跑 guide §2/§4 的实验。
- 文本为**中性告知**（subsidy/peak_demand/ev_delay 无强制措辞；night_setback 为建议；
  in_home_display 为信息），以降低 prompt 偏置（吸取 R023–R026 的教训）。
- 属能力恢复；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **nudge vs `--peer-nudge` 对照**（固定文本 vs 真实邻居均值，guide §6.1）；
2. 价格类政策（subsidy/peak_demand）真调，但须**多人户平均**以降噪；
3. 政策时间线真调（习惯黏性）。
