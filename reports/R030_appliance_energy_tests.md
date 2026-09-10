# R030 — 家电能耗公式 L1（on-demand / always-on / cycle / 元数据）

- **轮次**：Round 30
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 231/231 单测绿）

---

## 1. 目标

能耗核算是所有负荷指标与论文数值的地基。`appliances/base.py` 的三类设备能耗公式
（`OnDemandAppliance`/`AlwaysOnAppliance`/`CycleAppliance`）此前**无直接单测**，
`catalog.apply_appliance_meta` 也无测试。本轮补上，防止公式回退污染下游。

## 2. 依据

- `src/appliances/base.py`：`calculate_energy` → `_calculate_energy_logic`
  （on-demand `power/1000*hours`；always-on `daily_energy/24*hours`；cycle `per_cycle*min(1,hours/cycle_hours)`；
  `power_source="external"` 记 0）。
- `src/appliances/catalog.py`：`apply_appliance_meta`（standby/duty/flexible/season/cycle）。
- `src/analyze/load_model.py` 依赖上述公式。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_appliance_energy.py`（新增） | 10 个离线用例（用受控的具体子类实例化三类基类） |

覆盖：
- on-demand：1000W×1h=1.0 kWh、×0.5h=0.5、`external`=0；
- always-on：2.4kWh/日 → 1h=0.1、24h=2.4；`daily_energy=None` 时按 `power/1000×24`（240W→5.76）；
- cycle：满周期 0.6、半周期 0.3、超周期封顶 0.6；
- `apply_appliance_meta`：TV → standby 3/duty 1.0/flexible False/season annual；
  WashingMachine（cycle）→ 补 `energy_per_cycle_kwh=0.6`、`cycle_minutes=90`、flexible True；未知类型 no-op。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 231 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 231 tests — OK**（轮前 221 + 本轮 10） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思

- 用**受控具体子类**（而非依赖 catalog 默认值）测基类公式，隔离了公式逻辑与目录数据两类回归。
- 属测试基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **多人户实验**（token-gated）以分离政策信号与运行噪声；
2. **`peer-nudge`**（guide §6.1）实现（注意跨层：需上一日社区均值）；
3. 政策时间线真调（习惯黏性）。
