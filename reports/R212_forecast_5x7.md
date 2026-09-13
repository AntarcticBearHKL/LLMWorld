# R212 — 负荷预测（analyze_forecast，5 户 × 7 天）：RF 较 naive 提升 31.5%~57.1%

- **轮次**：Round 212（A1）
- **日期**：2026-09-12
- **验证层级**：**L0 分析**（复用 5 户 × 7 天数据；**0 token**）
- **结论**：✅ 预测工具在**真实 7 天数据**上跑通（此前 R153 因 <5 天受阻）；
  随机森林较 **naive（昨日同时刻）** 提升 **31.5%~57.1%**（均值 ≈44%），MAPE 0.20~0.46。

## 1. 目的（A1）

解锁 `analyze_forecast`（要求 ≥5 天/户）。用 R194/R195 的 **5 户 × 7 天** 数据集。

## 2. 改动
- `analyze_forecast.py`：新增 `--env`（此前只读默认 world 目录）→ 可分析自定义 env。

## 3. 方法（可复现）

```powershell
python src/analyze/analyze_forecast.py world_838587 --env week_b
python src/analyze/analyze_forecast.py world_838587 --env wk_838587_h001
python src/analyze/analyze_forecast.py world_143345 --env wk_143345_h001
python src/analyze/analyze_forecast.py world_143345 --env wk_143345_h002
python src/analyze/analyze_forecast.py world_143345 --env wk_143345_h003
```

## 4. 结果（5 户，7 天；train 5 / test 2）

| 住户 | MAE | naive MAE | 提升 | MAPE |
|---|---|---|---|---|
| W1h002 | 100.19 | 160.96 | **37.8%** | 0.350 |
| W1h001 | 119.47 | 174.49 | **31.5%** | 0.459 |
| W3h001 | 102.01 | 234.17 | **56.4%** | 0.418 |
| W3h002 | 115.29 | 189.84 | **39.3%** | 0.402 |
| W3h003 | 82.80 | 193.17 | **57.1%** | 0.196 |

- 均值提升 ≈ **44.4%**；RF 用 [hour, weekday] 预测小时电量。

## 5. 解读
1. **负荷可部分预测**（hour×weekday）：RF 显著优于持久性基线 → 生成负荷**结构合理**（RQ1 数据质量支持）；
2. MAPE 0.20~0.46 偏高（日内波动大）→ 与"住户行为异质/尖峰"一致；
3. **工具修复**：`--env` 使该分析可用于自定义数据集（此前仅默认目录）。
4. ⚠️**单位注记**：脚本标 "kW"，实际量级 ~80–120（= 小时均功率 **W**），为既有脚本单位标签问题（不影响相对结论）。

## 6. token
- **0**（复用产物）。
