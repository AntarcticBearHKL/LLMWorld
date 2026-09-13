# R217 — A6 季节对比：**冬季采暖 / 夏季制冷**（季节正确的设备选择）

- **轮次**：Round 217（A6）
- **日期**：2026-09-12
- **验证层级**：**L1**（293 单测全绿，+4）+ **L2 真调**（world_838587 h002；冬 2026-07-15 vs 夏 2026-01-15；n=15；~120 calls）
- **结论**：✅ **季节正确**：冬季 → **采暖（SpaceHeater 3.40 kWh，无制冷）**；夏季 → **制冷（AC 3.64 + Fan 0.35，无采暖）**。

## 1. 目的（A6）

此前 weather 是 **stub**（season 恒为 Spring，不随日期变）。实现 **日期→季节** 映射（澳季），再对比冬/夏。

## 2. 改动
- `src/engine/weather.py`：新增 `season_for_date()`（南半球：12–2 夏 / 3–5 秋 / 6–8 冬 / 9–11 春）与季节气温；
  `get_weather(date)` 现按日期给 season/temperature（override 仍生效）。
- `tests/test_weather_season.py`：+4 测试。**293 绿**。
- 注：既有 9 月运行 = Spring，**不受影响**。

## 3. 方法（可复现）

```powershell
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-07-15 --env "se_w_$i" --workers 1
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-01-15 --env "se_s_$i" --workers 1
# 聚合日总/设备能量
```

## 4. 结果（n=15）

| 季节 | 总电量 | AirConditioner | SpaceHeater（采暖） | Fan |
|---|---|---|---|---|
| **冬季 (07-15)** | 11.71 | **0.00** | **3.40** | 0.00 |
| **夏季 (01-15)** | 12.71 | **3.64** | **0.00** | 0.35 |

## 5. 解读
1. **季节正确的设备选择**：冬季用 **SpaceHeater**（采暖）、夏季用 **AC+Fan**（制冷）→ 与 prompt 的 season 规则一致（"heating in cold, cooling in hot"）；
2. **互为排他**：冬无制冷、夏无采暖 → 平台能区分季节行为；
3. **总电量夏 > 冬**（12.71 vs 11.71，+8.5%，未做显著性）——描述性；
4. **意义**：**解锁季节维度**（此前 stub 无法做）；既有春季结果不受影响。

## 6. 论文更新
- `paper/99_discussion.md` / `01_method.md`：weather 由 stub 升级为**按日期季节**；补"冬季采暖/夏季制冷（R217）"。

## 7. token
- 约 **120 次调用**。
