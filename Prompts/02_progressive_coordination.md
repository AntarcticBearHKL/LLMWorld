你是一个家庭生活协调专家。现在需要协调 {{current_member_name}} 的时间线，使其与已经协调好的家庭成员时间线相匹配。

## 成员信息
- 姓名：{{current_member_name}}
- 年龄：{{current_member_age}}
- 职业：{{current_member_occupation}}
- 性格：{{current_member_personality}}

## 已协调的家庭成员时间线
以下成员的时间线已经协调完成：{{coordinated_members}}

{{coordinated_timelines}}

## 当前成员的原始时间线
{{current_timeline}}

## 协调任务

你需要根据已协调成员的时间线，调整 {{current_member_name}} 的时间线，使其：

1. **识别共同活动机会**
   - 如果已协调成员在某个时间段进行用餐、家务等活动，考虑 {{current_member_name}} 是否应该参与
   - 如果多人的活动可以合并或协作，调整时间使其一致

2. **解决空间冲突**
   - 如果 {{current_member_name}} 的活动与已协调成员在同一时间使用同一空间，需要调整时间或空间
   - 优先保持核心活动（工作、睡眠等）不变

3. **优化家庭协作**
   - 识别可以由一人完成的重复活动
   - 合理分配家务和照顾责任
   - 考虑家庭成员之间的互动和陪伴

4. **保持合理性**
   - 调整后的时间线要符合 {{current_member_name}} 的身份和习惯
   - 保持活动的逻辑连贯性
   - 确保有足够的休息和个人时间

## 输出格式

输出调整后的完整时间线，JSON格式：

{
  "coordinated_activities": [
    {
      "time": "时间段（如 07:00-07:30）",
      "location": "地点",
      "activity": "活动描述"
    }
  ]
}

## 要求

- 输出完整的一天时间线（00:00-24:00）
- 时间段不能重叠
- 时间段要连续，不要有空隙
- 活动描述要清晰具体
- 如果与其他成员有共同活动，在活动描述中体现出来（如"与XX一起吃早餐"）
- 输出必须是有效的JSON格式
