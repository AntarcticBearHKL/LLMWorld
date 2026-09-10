# R038 — 社会规范去指令消融入口 `nudge_soft`

- **轮次**：Round 38
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 262/262 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（跨轮发现）**：R023（TOU）与 R037（nudge）都出现同一现象——**仿真幅度超出文献基准**
（TOU 峰 −18~−26% vs −3~6%；nudge 总量 −6~−10% vs −1~3%），指向 **prompt 过度遵从**。
R024 已为 TOU 提供 `tou_soft` 消融入口；**社会规范尚无对应消融**。

**期望**：新增 `nudge_soft`——**仅陈述邻居均值、去掉规范性压力**（"Most households try to keep …
below this level"），作为社会规范 prompt 强度的消融对照。

## 2. 依据

- R023/R037（幅度超基准 → 疑 prompt 偏置）。
- R024（`tou_soft` 消融先例）。
- guide §3.1（nudge 机制）、§8（"若远超合理区间，先查 prompt 是否写太强"）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/policy.py` | 新增 `render_nudge_soft_policy(neighbor_kwh=18.0)`（仅一句事实均值，无规范性措辞）；`parse_policy_arg` 支持 `nudge_soft`/`nudge_soft:<kwh>`；错误信息更新 |
| `tests/test_core_logic.py` | 新增 2 项用例 |

**用法**：
```powershell
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 2 --policy nudge_soft
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 262 tests - OK
```

覆盖：`nudge_soft` 标签正确、文本含 "18 kWh"、**不含**规范性短语 "keep their usage"；自定义均值。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 262 tests — OK**（轮前 260 + 本轮 2） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思与限制

- 与 `tou_soft` 对称：形成"**政策文本强度**"的消融入口（tou/tou_soft、nudge/nudge_soft）。
- **尚未真调**；`nudge` vs `nudge_soft` 的对照（≈16 次调用）留待后续——但须注意 R024/R026 的教训：
  单成员方差可能掩盖文本强度效应，优先在**多人户**上做。
- 属基础设施；**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. `nudge` vs `nudge_soft` 多人户消融（token-gated，优先多人以降噪）；
2. 把"prompt 过度遵从"作为**方法学发现**写入 `paper/99_discussion.md` 的 validity 小节；
3. 政策时间线真调（习惯黏性）。
