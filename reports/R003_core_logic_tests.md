# R003 — 核心干预/解析/校验逻辑 L1 锁定（跳过并发中的 B2）

- **轮次**：Round 3
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 94/94 单测绿，本轮新增 44 项）

---

## 1. 目标（现状 → 期望）

**现状**：goal.md §4 明确要求优先为纯逻辑写 L1 离线测试，覆盖
`json_parse`、`utils` 的时间/决策校验、`catalog.backfill_power`、`policy.parse_policy_arg`。
目前只有 Round 1/2 建立的 `day_state`、电池/负载模型测试，**干预入口与容错解析仍未锁定**。

**期望**：为这些"真实链路的前置纯逻辑"补齐离线单测，确保后续 L2/L3 真调前，
容错 JSON、TOU 干预文本、时间归一化、家电操作修复/越界丢弃都行为正确。

## 2. 依据（先读后做）

- **干预语义**：`intervention_experiment_guide.md` §2.1（TOU 文本注入 `--policy tou`）——本轮锁定
  `policy.parse_policy_arg` 的文本与 tag，保证"政策以自然语言告知 agent"的研究语义不被破坏。
- **研究计划**：`研究计划.md` §4.2——s4 阶段"自然语言活动序列 → 家电操作"依赖 JSON 容错与操作校验。
- **goal.md** §4 L1 清单（对 `json_parse` / `utils` / `catalog` / `policy` 的显式要求）。

## 3. ⚠️ 并发情况（重要，遵循 goal.md §9 处理）

本轮开始时发现**有外部进程正在同一工作树上跑真实实验**，证据：

- 进程 `python.exe run.py --mode simulate --world world_838587 --days 2`（PID 4936/32676），
  `CreationDate=2026-09-11 00:46:04`，**并非本会话启动**；持续写入
  `output/simulation/world_838587/...`（00:48 时仍在 s2/s3）。
- 另有新增 `output/worlds/world_838587/`、`output/world_gen_val.log`、`output/sim_run_val.log`。
- `src/steps/world/s3_household_build.py` 在会话中途由 333 行增长到 589 行（Feature B2 正在落地）。

按 §9「出现必须由用户拍板的重大歧义 → 记入 report 并跳过该项，转去做不受影响的其他优化点」：
**本轮跳过 Feature B2**（避免与并发工作冲突/覆盖），改做**与之互不相干的**核心逻辑 L1 测试。

## 4. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_core_logic.py`（新增） | 44 个离线用例，见下 |

覆盖点：

- **`engine.json_parse.parse`**：纯对象、markdown 代码围栏、前后夹杂散文、单引号键/值、尾逗号、
  未加引号键、裸 `True/False/None`、字符串内花括号、字符串内原始换行转义、嵌套对象。
- **`engine.policy.parse_policy_arg`**：空值、默认 TOU 文本/费率、自定义费率、三值（肩峰）、
  单值回退默认、未知政策抛 `ValueError`。
- **`utils.normalize_time_range`**：补零、全角冒号/破折号归一、去空格、单时间用下一段补全、
  默认 +60 分钟、23:30 封顶 24:00、`None` 透传、非法原样返回、逆序区间不重排。
- **`utils.normalize_activity_times`**：借下一段补全并记日志、非字典透传、空列表。
- **`catalog.backfill_power`**：缺功率回填估计值、越界钳制、合法保留、bool 视为非法、
  A/C 卧室位置感知（1800）、Light 位置感知（客厅60/厨房40/卫生间30）、冰箱补 `daily_energy_kwh`、**不改输入**。
- **`utils.repair_appliance_operations`**：合法操作保留、幻觉类型按 family 修复
  （`kitchen_television`→`kitchen_tv`）、非法动作记 unknown、未知 id 记 unknown、非字典跳过。
- **`utils.validate_and_clean_decisions`**：居家操作保留且带 `start/end_minutes` 且 `valid=True`、
  离家场景丢弃房间设备（原因含 "out of home"）、未知操作丢弃且 `operations_kept=0`。

## 5. 测试（L0/L1）

```powershell
.venv\Scripts\python.exe -m compileall -q src run.py          # exit=0
.venv\Scripts\python.exe -m unittest discover -s tests        # Ran 94 tests - OK
```

## 6. 结果

| 检查 | 结果 |
|---|---|
| `compileall src run.py` | exit 0 |
| `unittest discover -s tests` | **Ran 94 tests — OK**（轮前 50 + 本轮 44） |

**是否符合预期**：是。

## 7. token 消耗

- LLM 调用：**0**；token：**0**。未与并发真调争抢额度。

## 8. 反思

- **并发是首要风险**：同仓两个工作流会让 `git status`/diff 抖动、并可能互相覆盖。已按 §9 规避，
  未提交任何 B2/提示词/`output` 文件。
- **建议（需用户确认）**：确认 `world_838587` 的模拟是否由另一会话/用户手动发起；
  若是另一永续会话，建议**只保留一个写入者**，否则提交历史会交错。
- 本轮为纯测试基础设施，**无"有效果"结论 → 仅入 `reports/`**，不进 `paper/`。

## 9. 可复现命令

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 10. 下一步（候选）

1. **B2 锁定**：待上述 `world_838587` 真调结束、工作树稳定后，为
   `s3_household_build` 的 Big Five/energy_awareness 与冗余房间去除写 L1 并提交；
2. **L2 小范围**：单户 ×1 天 `--s4-only`，对照 `analyze_behavior_load` 的
   `behavior_total_kwh` vs 原始 `total_kwh`（验证 Round 2 的 `exclude_families`）；
3. **文档漂移**：`population_runner.py`/`engine/news*.py`/`compare_worlds.py` 缺失的归位或标注。
