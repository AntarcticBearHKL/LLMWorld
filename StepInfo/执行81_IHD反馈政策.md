# 执行81:实时电表反馈政策(in_home_display)

## 实际做了什么

1. **论文依据**:Faruqui, Sergici & Sharif (2010) Electricity
   Journal 23(8)(IHD 平均削减 3-13%,非 arXiv 只记索引)+
   Cabezas-Rivière 2025(实时反馈兴趣高,计划75已引)
2. **`engine/policy.py`**:第 8 种政策 `in_home_display`
   (实时功率/电费显示、近 7 日趋势、大功率即时提醒);
   from_name 注册;未知政策报错更新
3. **前端**:政策实验下拉加 in_home_display
4. **RefPaper/README.md**:非 arXiv 文献索引区
   (Faruqui 2010×2/Allcott 2011/2014/Ayres 2013)
5. **测试**:TestPolicy 新增 in_home_display 渲染
   → 172 项全绿

## 结果

- `test_offline.py`:172 项 OK(skipped=5)
- 政策矩阵现 8 种政策 + 组合
- server 重启完成

## 偏差

- 无

## 下一步候选(计划 82)

1. **存档同步**(里程碑 80-81 入档 + README)
2. **户间双向社交网络**:引擎级大功能,需用户确认方向
