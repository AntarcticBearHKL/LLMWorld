# R069 — lockdown 扩样：Out 归零 7/7 → 0/7（p≈0.0003，最强二值结果）

- **轮次**：Round 69
- **日期**：2026-09-11
- **验证层级**：**L2 真实运行**（world_838587 house_0001 ×4 + world_172148 house_0002 ×2；~24 calls）
- **结论**：✅ **完美二值信号**：baseline Out>0 **7/7** vs lockdown Out>0 **0/7**，Fisher 单侧 **p ≈ 0.0003**

---

## 1. 目标

R068 在 n=1 发现 lockdown 使外出归零（615→0）。本轮扩样至 7 个成员-日（跨 2 世界），
以判定"Out 归零"这一准二值信号的显著性与稳健性。

## 2. 设计（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0001 --days 1 --env lockdown_h1 --event-template "2026-09-11|lockdown" --workers 4
python run.py --mode simulate --world world_172148 --house house_0002 --days 1 --env lockdown_nw --event-template "2026-09-11|lockdown" --workers 2
# baseline 复用各成员既有 no-event 运行
```

- "Out 分钟"取自 `s1_macro_<member>.json` 中 location 以 `out` 开头的活动时长之和。

## 3. 结果（2026-09-11）

| 世界 | 住户 | 成员 | baseline Out(min) | lockdown Out(min) |
|---|---|---|---|---|
| world_838587 | house_0001 | Member 1 | 600 | **0** |
| world_838587 | house_0001 | Member 2 | 465 | **0** |
| world_838587 | house_0001 | Member 3 | 280 | **0** |
| world_838587 | house_0001 | Member 4 | 570 | **0** |
| world_838587 | house_0002 | Member 1 | 615 | **0** |
| world_172148 | house_0002 | Member 1 | 600 | **0** |
| world_172148 | house_0002 | Member 2 | 600 | **0** |

**汇总**：baseline **7/7 有外出**；lockdown **0/7 有外出**（全部整日居家）。
**Fisher 精确检验：单侧 p ≈ 0.00029**（2×2 表 [[7,0],[0,7]]）。

## 4. 解读

- **最强、最清晰的结论**：7 个 baseline 全部有外出行程（280–615 分钟），lockdown 后**全部归零**；
- **跨 2 世界、跨成员**验证；因果链明确（封锁 → 居家 → 日间负荷上升，R068 已示 +294%）；
- **完美分离**（baseline 与 lockdown 无重叠），是本项工作**效应量最大**的结论；
- 与 R058 定位一致：**准二值/大效应**信号在噪声地板下依然极显著。

## 5. token 消耗（估算）

- 本轮 2 个 run × (4 步 × 成员数 × 1 天) ≈ **24 次调用**。

## 6. 论文更新

- `paper/experiments/event_lockdown.md`：更新为 **7/7 vs 0/7（p≈0.0003）**；
- `paper/99_discussion.md` RQ2：lockdown 升级为显著且最强；
- `paper/README.md`：状态更新。

## 7. 结论

**lockdown → 外出归零**（7/7→0/7, p≈0.0003）是当前**最强**的二值结论，超越热浪（9/10, p≈0.0004）。
三个环境/社会事件（热浪→制冷、寒潮→采暖、封锁→居家）共同构成"事件驱动行为"的显著证据集。
