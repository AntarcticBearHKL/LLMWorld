# R025 — 实验采样控制（temperature / thinking / reasoning-effort 可覆盖）

- **轮次**：Round 25
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 212/212 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（来自 R024 的方法学发现）**：单成员 A/B 的**运行间方差主导**，无法评估政策幅度。
根因之一是采样不可控：`config.TEMPERATURE=1.0` 且 `engine/subagent.py` 在**导入时**
把它固化为 `DEFAULT_TEMPERATURE`，运行时无法调整；`thinking/REASONING_EFFORT` 也无 CLI 入口。

**期望**：让实验可**运行时**控制采样参数（温度/思考/推理力度），以便后续做方差敏感性实验。

## 2. 依据

- R024（方差主导 → 需控制采样）。
- `config.py`（`TEMPERATURE`/`THINKING`/`REASONING_EFFORT`）、`engine/subagent.py` 的请求构造。
- goal.md §5（性能/成本效率、可复现）与 §4（先小范围验证）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/subagent.py` | 删除导入期常量 `DEFAULT_TEMPERATURE`；两处请求体改为运行时读取 `config.TEMPERATURE`（`THINKING`/`REASONING_EFFORT` 本就近运行时读取） |
| `run.py` | 新增 `apply_sampling_overrides(temperature, thinking, reasoning_effort)`；CLI 增加 `--temperature`、`--no-thinking`、`--reasoning-effort {low,medium,high}`，在分发前应用并打印 |
| `tests/test_experiment_controls.py`（新增） | 4 个离线用例 |

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 212 tests - OK
```

覆盖：全量覆盖生效且返回 applied 字典；`None` 不改动；部分覆盖；`subagent` 不再有 `DEFAULT_TEMPERATURE` 陈旧常量。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 212 tests — OK**（轮前 208 + 本轮 4） |

**是否符合预期**：是。

## 6. 用法

```powershell
# 关闭思考 + 低温度（降低采样方差）做敏感性/复现实验
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 `
  --env tou_lowtemp --policy tou --no-thinking --temperature 0.2
```

## 7. 反思与限制

- 注意：`temperature` 仅在 **thinking 关闭**时进入请求体；thinking 打开时以 `reasoning.effort` 控制。
  因此"降方差"应主要通过 `--no-thinking`（+ 低温）或 `--reasoning-effort low` 实现。
- 供应商侧在 reasoning 模式下仍可能有内部采样；本改动是**尽力而为**的控制入口，非确定性保证。
- 0 token；属实验基础设施，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步

1. **R26**：用 `--no-thinking --temperature≤0.3` 或**多人户**重做 TOU/热浪，检验效应能否从噪声中分离；
2. `population_runner.py`（peer-nudge / policy-schedule）恢复或正式废弃。
