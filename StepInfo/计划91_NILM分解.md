# 计划91:NILM 可分解性分析(负荷分解基准)

## 做什么

新增 `Implement/analyze_nilm.py`:在模拟数据上运行**简单
NILM(非侵入式负荷分解)基准**——利用已知电器功率表做
"功率指纹直方图匹配",从户级聚合曲线估计各电器用电,
与上帝视角真值(电器级 JSON)对比,输出 MAE/相对误差/分解率。
评估 LLM 模拟负荷曲线的"可分解性"(真实 NILM 研究的
前置条件,也是 IHD 个性化反馈的数据基础)。

## 为什么(论文依据 + 思考过程)

搜索过程:arXiv search UI 搜 "appliance load disaggregation NILM
deep learning" → 24 篇 → 选定:

1. **Azad, Rajabi & Estebsari (2023), arXiv:2306.05017**
   《Non-Intrusive Load Monitoring (NILM) using Deep Neural Networks:
   A Review》:NILM 综述,标准评估指标 MAE(能量误差)/
   相对误差/分解率。
   → 思考:本项目模拟数据是"带标签的聚合数据"
   (电器级 JSON=真值标签),天然是 NILM 基准数据集;
   简单指纹匹配是基线方法(与深度 NILM 对比的下限)。
2. **Xue et al. (2025), arXiv:2505.06330**(同搜索):
   LLM 提示式 NILM(零训练),泛化强但精度低于深度模型
   → 佐证"简单方法即可评估可分解性"。

## 怎么做

1. `Implement/analyze_nilm.py`:
   - 真值:读每户 `用电信息/` 下各电器 JSON
     (unique_id/name/power_watts/minute_by_minute_usage 或
     usage_segments)→ 各电器日 kWh
   - 指纹匹配:聚合 1440min 曲线中"功率稳定平台"
     (连续 ≥10 分钟,波动 <5%)→ 与电器功率表匹配(±10%)
     → 估计各电器使用分钟与 kWh
   - 指标:各电器 MAE/相对误差、总分解率
     (估计总电/真值总电)、未匹配功率占比
   - 输出 outputs/<world>/analysis/nilm_<scenario>_<date>.json
2. `server.py`:`GET /api/worlds/<id>/nilm/<scenario>/<date>`
3. 前端:新增"NILM 分解"面板(电器真值 vs 估计表)
4. 测试:TestNilm——合成曲线(2000W 电磁炉 60min + 100W 灯
   全程)→ 指纹匹配还原 MAE 低;空数据报错

## 怎么验证

- `python Implement/test_offline.py` 全绿
- 合成数据 CLI 冒烟
