# 计划 37 —— 批量人口生成叠加 LLM（程序化骨架 + LLM 细节）

> 依据：`StepInfo/00_需求与规则.md` §一.17（已重读）。

## 用户需求
批量人口生成也要用 LLM：纯程序化缺乏多样性、LLM 纯生成易重复——**程序化提供足够丰富的语境（骨架），让 LLM 输出家庭类型与成员细节**。

## 设计（混合生成管线）

```
build_population_llm(world_id, count, seed)
  1. 程序化骨架（确定性，census 校准）：
     - 类型配额（8 类）→ 每户蓝图 blueprint
     - 成员数 / 年龄关联（夫妻差≤5、孩子=父母-24~34） / 收入档
     - 住房与电器（_home_by_income） / Big Five 五维分数 / 新闻敏感度
  2. LLM 细节填充（每户 1 次调用）：
     - 输入语境：蓝图 JSON + Clayton 3168 census 特征 + 防重复指令
     - 输出：名字（多文化）/ 职业（与收入档匹配）/ 习惯 / 爱好 /
           性格文本（基于给定 Big Five）/ 住宅名 / 家庭独特故事
  3. 校验合并：
     - 成员数、年龄、Big Five 以程序化为准（LLM 不改）
     - LLM 输出非法/缺失 → 回退程序化默认（不崩溃）
  4. 落盘：household.json（结构不变，细节来自 LLM）

防重复措施：
- 每户 prompt 含"蓝图 + 种子标识 + 已有家庭摘要列表（前 N 户的名字/职业/习惯）"
  → LLM 看到社区全貌，避免同质化
- Big Five 程序化采样保证量化多样性；LLM 只负责叙事细节
```

## 做什么

| # | 任务 | 文件 | 验收 |
|---|---|---|---|
| 1 | 蓝图生成：从 `_build_template` 抽取骨架逻辑（成员数/年龄/收入/电器/Big Five，去名字去习惯） | `population.py` | 确定性 |
| 2 | LLM 细节填充：`_llm_fill_details(blueprint, context)` + 校验合并 + 回退 | `population.py` | mock 测试通过 |
| 3 | 新 prompt 模板：`generate_step4_household_details.md`（census 语境 + 蓝图 + 防重复） | `prompts/` | 渲染正常 |
| 4 | `build_population_llm()` 入口（CLI --llm 模式） | `population.py` | 可调用 |
| 5 | 测试：蓝图确定性/mock LLM 填充/校验回退/防重复上下文 | `test_offline.py` | 全绿 |
| 6 | 提交（真实 LLM 生成等用户确认后执行） | | |

## 验证（离线）
1. mock LLM（固定 JSON）→ 管线正确、字段齐全
2. LLM 输出成员数与蓝图不符 → 回退程序化默认不崩溃
3. 蓝图同 seed 确定性
4. git 提交

## 注意
- 按 §一.16：开发阶段不做 LLM 模拟；真实 LLM 生成调用在用户确认后小规模执行（生成本身是用户明确要求的功能）
