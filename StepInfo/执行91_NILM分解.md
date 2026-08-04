# 执行91:NILM 分解基准

## 实际做了什么

1. **论文搜索**:arXiv search UI 搜 "appliance load disaggregation
   NILM deep learning" → 24 篇 → Azad et al. (2023)
   arXiv:2306.05017(NILM 综述,MAE 标准指标)
   → PDF 已下载 RefPaper(31/31)
2. **新增 `Implement/analyze_nilm.py`**:
   - `load_true_appliances`:读电器级 JSON(上帝视角真值)
   - `find_plateaus`:聚合曲线功率稳定平台(≥10 分钟,±5%)
   - `match_appliances`:功率指纹匹配(±10%)→ 估计各电器 kWh
   - 指标:MAE/相对误差/分解率
   - 输出 nilm_<scenario>_<date>.json
3. **`server.py`**:`GET /api/worlds/<id>/nilm/<scenario>/<date>`
4. **前端**:新增"NILM 分解基准"面板
5. **测试**:TestNilm 3 项 → 185 项全绿

## 结果

- `test_offline.py`:185 项 OK(skipped=5)
- 合成验证:电磁炉 2.0kWh 精确还原;灯 2.3kWh
  (叠加时段被大功率匹配占用=简单 NILM 固有局限,
  正是深度 NILM 的改进空间)
- RefPaper 31/31
- server 重启完成

## 偏差

- 叠加时段分解不完美(方法固有,测试断言反映该语义)

## 下一步候选(计划 92)

1. **存档同步**(里程碑 90-91 入档 + Design)
2. **户间双向社交网络**:引擎级大功能,需用户确认方向
