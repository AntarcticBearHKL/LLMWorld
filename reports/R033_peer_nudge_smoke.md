# R033 — `--peer-nudge` 端到端冒烟（L2 最小样本）

- **轮次**：Round 33
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（1 户 × 1 成员 × 2 天；复用 world_838587）
- **结论**：✅ 通过（社区均值按上一日计算并注入 s4；首日无 nudge）

---

## 1. 目标

R032 实现并 L1 测试了 `--peer-nudge`，但**未真调**。本轮做最小端到端冒烟，确认：
上一日社区均值被计算、渲染并进入 s4 prompt；首日（无上一日）不注入。

## 2. 命令（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 `
  --days 2 --env peer_smoke --peer-nudge --workers 1
```

## 3. 结果（证据）

| 检查 | 证据 |
|---|---|
| 逐日计算 | 运行日志：`[PeerNudge] 2026-09-12: For comparison, households in your community used about 7.43 kWh of electricity yesterday on average.` |
| 注入 s4（第 2 天） | `output/simulation/peer_smoke/2026-09-12/house_0002/log/00001_s4_appliance_decision.md:470` 含该句 |
| 首日不注入 | `.../2026-09-11/.../s4_appliance_decision.md` **无** "For comparison"/"community used about" |
| 流程 | `peer_nudge exit=0` |

**机制**：第 2 天用 `dataset.population_profile(world, "baseline", prev_date, env)` 取上一日
`per_house` 总量均值（7.43 kWh）→ `social.render_peer_nudge` → 并入 s4 的 `world_news`。

## 4. 结论与限制

- 能力成立：邻居比较是**动态的**（随社区逐日变化），符合 guide §6.1。
- 本轮**非效果实验**：单成员、仅确认注入；邻居比较是否压抑高耗家庭（Ayres 2013）需另行对照实验。
- 未改动源码 → 仅新增本报告。

## 5. token 消耗（估算）

- 1 臂 × (4 步 × 2 天) ≈ **8 次调用**。

## 6. 下一步

1. `--policy nudge` vs `--peer-nudge` 对照（固定文本 vs 真实邻居均值，guide §6.1）；
2. 多人户实验以分离政策信号与噪声；
3. 政策时间线真调（习惯黏性）。
