# R005 — 人格落地（Big Five / energy_awareness）+ 冗余房间去除 L1 锁定

- **轮次**：Round 5
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 131/131 单测绿，本轮新增 30 项）

---

## 1. 目标（现状 → 期望）

**现状（Feature B2，此前未提交）**：`s3_household_build` 之前只用 LLM 自由生成 `personality`，
缺少可分析的**结构化异质性参数**；且 LLM 可能生成多余共享房间（Study/Office/Laundry…），
导致同一家庭设备被重复计入。

**期望**：
1. 从 s2 采样的**权威 persona 行**（BFI-2 五列 + Energy level）确定性地推导
   `personality.big_five`（5 维 0–1）与 `personality.energy_awareness`（Low/Medium/High）；
   行缺失时回退到 **portrait 文本标记**的确定性映射（同一画像 → 同一分数）。
2. 删除与其它房间**设备族重复**的共享房间，但保留 ≥1 个共享房间、保护
   Bedroom/Living/Kitchen/Bathroom。

**性质**：RQ1 大规模异质人群模拟的**参数落地**（可分组分析）+ 装配健壮性；不新增研究方向。

## 2. 依据（先读后做）

- **文献（计划22 / RQ1 异质性）**：`RefPaper/README.md` 计划22 组——PsyAgent (2026) Big Five 驱动
  agent、Personality Student Agents (2026)、Personality-Driven LLM Agents、LLM Social Particle Swarm；
  研究计划 §2.7 Costa & Kahn 2010（同一政策在不同价值取向群体响应分化）、§4.1 RQ1/RQ3 要求
  "household agents 需要差异化的 value 参数而非同质效用函数"。
- **analyz脚本**：`analysis scripts` 读取 `personality.big_five` / `energy_awareness`
  （`analyze_groups.py` 分组响应的基础）。
- **研究计划** §4.2 领域模型层（成员画像）。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `src/steps/world/s3_household_build.py` | `HOUSEHOLD_SCHEMA.personality` 增补 `energy_awareness`+`big_five`；新增 `PERSONA_BIG_FIVE_COLUMNS`/`BFI_LEVEL_SCORES`/`ENERGY_LEVEL_AWARENESS`/portrait 标记表与 `_apply_personality`/`_portrait_big_five`/`_portrait_energy_awareness`/`_load_persona_rows`；`_drop_redundant_rooms` 等 |
| `src/prompts/generate_world_step3_home.md` | 限定房间集合（N 卧室 + 1 厨房 + 1 卫生间 + ≤1 共享间），禁止多余房间与重复设备 |
| `src/prompts/generate_world_step3_member.md` | 明示"不要捏造 energy_awareness/big_five，系统从 persona 确定性推导" |

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 131 tests - OK
```

新增 `tests/test_personality_rooms.py`（30 例）：

- 标记命中（整词边界、不匹配子串）；
- `_portrait_big_five`：中性=0.5、单标记±0.1、正/负向钳制 [0.1,0.9]、确定性；
- `_portrait_energy_awareness`：High/Low/Medium（平局→Medium）；
- `_level_to_score` / `_level_to_awareness` 的映射与未知/None；
- `_apply_personality`：**优先 persona 行**、无行回退 portrait、**部分行时用 portrait 补缺维度**、
  非字典 personality 被替换、既有键（traits）保留；
- `_room_family_set` / `_is_protected_room`；
- `_drop_redundant_rooms`：删重复共享间、**当会删掉最后一个共享间时保留**、空房间不删、
  仅保护房间不动、非列表不动；
- `_normalize_personal_appliances` / `normalize_type`；
- `_load_persona_rows`：命中缓存+provenance seed、缓存不匹配重采样、重采样失败返回空、
  损坏文件回退默认 seed（`generate_world.sample_personas` 被 mock，**0 API**）。

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 131 tests — OK**（轮前 101 + 本轮 30） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**（persona 采样被 mock）。

## 7. 反思

- **并发处理**：提交前确认 `s3_household_build.py` 哈希稳定（>10 分钟未变）后才入库；
  外部 `run.py --mode simulate --world world_838587 --days 2` 仅写 `output/`，与本轮源码提交不冲突。
  已核实只 stage B2 源码 + 测试 + 本报告，未触碰 `output/`。
- **设计注意**：`_drop_redundant_rooms` 的"保留最后一个共享间"判断只把 bedroom/kitchen/bathroom
  视为非共享，Living Room 计为共享间——测试已锁定该语义，防止误删导致家庭无公共空间。
- 本轮为结构化参数与装配基础设施；**persona 对行为的"有效果"影响尚未在真调中验证 → 本轮结论不入
  `paper/`**（按 §6 分流）。真正的 RQ1/RQ3 异质性效果需后续 L2/L3 实验。

## 8. 下一步（候选）

1. **L2 小范围真调**（待并发 run 结束、避免额度争抢）：单户 ×1 天，核对
   `personality.big_five`/`energy_awareness` 确实写入 `household.json`，并抽查 `exclude_families`
   的 `behavior_total_kwh`；
2. 文档漂移修复：`population_runner.py`/`engine/news*.py`/`compare_worlds.py`；
3. 为 `analyze_groups.py` 的 Big Five/energy_awareness 分组逻辑补 L1。
