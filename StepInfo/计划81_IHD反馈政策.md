# 计划81:实时电表反馈政策(in_home_display)

## 做什么

policy.py 新增第 8 种政策 **in_home_display**(智能电表实时反馈):
渲染"家中安装智能电表显示屏,可实时查看当前功率、电费与
近 7 日用电趋势"——信息反馈机制,刺激即时节能。

## 为什么(论文依据 + 思考过程)

搜索过程:arXiv search UI 搜 "energy bill feedback smart meter
display consumption reduction"(0 结果)→ 采用权威非 arXiv 综述:

1. **Faruqui, Sergici & Sharif (2010)**, The Electricity Journal
   23(8):39-48《The impact of informational feedback on energy
   consumption: A survey of the experimental evidence》:
   智能电表 + 信息反馈(In-Home Display)实验综述,
   IHD 平均削减用电 3-13%。
   → 思考:计划44 已引 Faruqui & Sergici (2010) 动态定价综述
   (同团队);IHD 是"信息反馈"类政策的经典代表,
   与 nudge(社会规范)互补——nudge 比"别人",IHD 给"自己"。
   本项目政策矩阵缺"自我监控"维度,第 8 种政策补齐。
2. **Cabezas-Rivière et al. (2025), arXiv:2512.16949**(计划75已引):
   法国调查显示居民对"实时反馈"兴趣高(与 IHD 一致)。

## 怎么做

1. `engine/policy.py`:
   - `Policy.in_home_display()`:渲染实时功率/电费显示、
     近 7 日趋势对比、即时反馈提示
   - from_name 注册;前端下拉 + README
2. 测试:TestPolicy 加渲染/注册
3. RefPaper:非 arXiv 期刊(Faruqui 2010)只记索引不下载
   (§一.23)——在 RefPaper/README.md 加索引行

## 怎么验证

- `python Implement/test_offline.py` 全绿
- 渲染文本人工检查
