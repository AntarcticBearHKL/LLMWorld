# R004 — create_home_from_household 去重逻辑 L1 锁定

- **轮次**：Round 4
- **日期**：2026-09-11
- **验证层级**：L0 + L1（**0 token**）
- **结论**：✅ 通过（累计 101/101 单测绿，本轮新增 7 项）

---

## 1. 目标（现状 → 期望）

**现状**：`simulate.create_home_from_household` 承担"房间内同族家电去重、个人设备替换/让位房间设备"
的职责，是每户 Home 装配的唯一入口；goal.md §4 明确将其去重逻辑列为 L1 优先目标，但此前无测试。

**期望**：用离线单测锁定 5 类去重行为，防止后续改动破坏装配正确性（错误去重会直接扭曲负荷与设备占用）。

## 2. 依据（先读后做）

- **代码**：`src/simulate.py:create_home_from_household`、`appliances.catalog.appliance_family`
  （Laptop/Computer 同族）、`PERSONAL_DEVICE_TYPES`。
- **研究计划** §4.2 领域模型层（成员/房间/家电组合对象）——装配正确性是行为→负荷映射的前提。
- **goal.md** §4 L1 清单。

## 3. 改动

| 文件 | 改动 |
|---|---|
| `tests/test_home_dedup.py`（新增） | 7 个离线用例 |

覆盖：

- 房间内**同族去重**（Computer + Laptop → 仅保留 1 个）、异族保留；
- 个人设备**替换**房间 fixture（卧室 Computer 被个人 Laptop 按 `PERSONAL_DEVICE_TYPES` 规则替换，
  且 owner 正确）；
- 非个人设备**不替换**房间 fixture（个人 TV 让位房间 TV）；
- 个人设备**同族去重**（两个 Phone 仅留 1）；
- 字符串条目归一化、非字典条目忽略；
- 基本装配：members/rooms/registry 注册与 `kitchen_tv` 取值。

## 4. 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # Ran 101 tests - OK
```

## 5. 结果

| 检查 | 结果 |
|---|---|
| `unittest discover -s tests` | **Ran 101 tests — OK**（轮前 94 + 本轮 7） |

**是否符合预期**：是。

## 6. token 消耗

- LLM 调用：**0**；token：**0**。

## 7. 反思

- 本轮继续遵守 §9：**未触碰**并发工作流持有的 `s3_household_build.py` / `generate_world_step3_*` / `output/`。
- 至此 goal.md §4 的 L1 清单（`json_parse`、`utils` 时间/校验、`catalog.backfill_power`、
  `policy.parse_policy_arg`、`create_home_from_household`）**已全部有离线测试覆盖**。
- 纯测试基础设施，**无"有效果"结论 → 仅入 `reports/`**。

## 8. 下一步（候选）

1. **B2 锁定**（待并发真调结束、工作树稳定后）；
2. **L2 小范围真调**：`--mode simulate --house house_0001 --member 0 --days 1`（或 `--s4-only`）
   验证连续性与 `exclude_families`；
3. 文档漂移修复。
