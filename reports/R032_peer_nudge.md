# R032 — 恢复 `--peer-nudge`（邻居比较社会信号，guide §6.1）

- **轮次**：Round 32
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 251/251 单测绿；compileall exit 0）

---

## 1. 目标（现状 → 期望）

**现状（drift）**：`intervention_experiment_guide.md` §6.1 的**邻居比较**（`--peer-nudge`，
用**真实邻居均值**而非固定文本，随社区改善而"滚动"，动态社会规范演变）在重构后缺失，
是文档漂移账本中**最后一项**未恢复的能力。

**期望**：把**上一日社区平均日用电量**渲染成自然语言比较信息，注入 s4 提示，
形成随社区变化而更新的社会规范。

## 2. 依据

- `intervention_experiment_guide.md` §6.1（real neighbor mean vs fixed text；动态比较略优）。
- 文献：Ayres, Raseman & Shih (2013)（Opower 同伴比较，高耗家庭响应最强）。
- 研究语义红线：仅自然语言注入，效果涌现。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/engine/social.py`（新增） | `community_mean_kwh(house_totals)`（忽略 None、四舍五入、空→None）与 `render_peer_nudge(mean_kwh)`（自然语言比较句；None→""） |
| `run.py` | 新增 `--peer-nudge`；`_peer_nudge_text` 用上一日 `dataset.population_profile` 的 `per_house` 均值渲染（**懒加载 + try/except 兜底**，失败不中断）；把 peer 文本并入 s4 的 `world_news` |
| `tests/test_social.py`（新增） | 7 个离线用例 |

**用法**：
```powershell
python run.py --mode simulate --world <w> --house house_0002 --member 0 --days 3 --peer-nudge --workers 1
```

## 4. 测试

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py     # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 251 tests - OK
```

覆盖：均值（含忽略 None、四舍五入、空/全 None→None）；渲染（None→""、含数值/community/yesterday、0.00 可渲染）。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 251 tests — OK**（轮前 244 + 本轮 7） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（未真调）。

## 7. 反思与限制

- **分层**：`run.py` 为计算社区均值**懒加载** `analyze.dataset`（仅在 `--peer-nudge` 时），
  并以 `try/except` 兜底——若分析层不可用则该日跳过 nudge，不影响主流程。
- 均值取**上一日**的 `per_house` 总量（baseline 口径）；动态性来自逐日滚动。
- **尚未真调验证**；端到端注入（s4 prompt 含邻居均值）留待后续 L2（≈8–16 次调用）。
- 至此 guide 中记录的主要能力（TOU/subsidy/…、news、community-notice、policy-schedule、peer-nudge）
  **均已具备入口**；属基础设施，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **`--peer-nudge` L2 冒烟**（确认注入 + 与 `--policy nudge` 对照）；
2. **多人户实验**（token-gated）以分离政策信号与运行噪声；
3. 政策时间线真调（习惯黏性）。
