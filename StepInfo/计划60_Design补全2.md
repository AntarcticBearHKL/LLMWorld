# 计划60:Design 文档补全第二轮(计划51-59 新模块)

## 做什么

为计划51-59 新增模块补 Design/.aas 架构文档并同步存档:
- compare_worlds.py(计划51 多世界政策对比)
- analyze_event_response.py(计划55 事件响应)
- engine/world.py 日期时间线约束函数(计划58)
- 前端开启模拟闭环/新闻模板(计划53/57/59)
同步 00_需求与规则 §三 能力清单、§七 下一步候选重排。

## 为什么(依据)

1. **00 规则 §七.5 + 读档契约**:Design 是架构层存档,
   新模块必须有 .aas 才能被无上下文 agent 接续(运维经验)。
2. **§一.18**:文档性内容放 Design/(零注释标准的配套)。

## 怎么做

1. 新增:
   - `Design/engine/CompareWorlds.aas`(load_world_policies/
     _to_float/build_matrix,输出 worlds_matrix.json)
   - `Design/engine/AnalyzeEventResponse.aas`(事件日 vs
     非事件日迁移率/用电变化,日期格式兼容)
   - `Design/engine/TimelineGuard.aas`(get_world_last_date/
     parse_world_date/validate_start_date,三入口接入)
2. 更新:
   - `Server.aas`:新端点(timeline/news-templates/event-response/
     jobs/stop)+ 前端面板(事件响应/时间线/开启模拟闭环)
   - `AnalyzeTools.aas`:compare_worlds/analyze_event_response
   - `World.aas`:日期约束函数
   - `PopulationRunner.aas`(如有):--peer-nudge
3. 00_需求与规则 §三 能力清单同步(analyze_event_response/
   compare_worlds/时间线约束/peer-nudge)+ §七 候选重排
4. 测试:无代码变更,144 项全绿

## 怎么验证

- `python Implement/test_offline.py` 144 项全绿(未动代码)
- git status 确认仅文档变更
