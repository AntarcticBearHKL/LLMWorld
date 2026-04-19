你是一个家庭用电行为专家。请为{member_name}的一天生成完整的用电决策。

成员信息：
- 姓名：{member_name}
- 年龄：{member_age}
- 职业：{member_occupation}
- 习惯：{member_habits}

该成员的完整时间线：
{member_timeline}

家庭结构和电器：
{home_structure_with_appliances}

环境信息：
- 季节：{season}
- 天气：{weather}
- 温度：{temperature}度

请为该成员一天中的每个时间段决策所有相关电器的开关状态。

决策原则：
1. 根据活动内容和所在房间，决定需要使用哪些电器
2. 考虑环境因素（季节、天气、温度）影响用电需求
3. 符合该成员的生活习惯
4. 注意节能（离开房间关灯、不用的电器关闭）
5. 常开电器（如冰箱）保持开启状态
6. 考虑行为描述中的细节（如"开灯"、"关灯"等）

输出JSON格式：
{
  "member": "{member_name}",
  "appliance_decisions": [
    {
      "time": "时间段",
      "location": "房间",
      "activity": "活动",
      "operations": [
        {
          "appliance": "电器名称",
          "action": "开启或关闭",
          "reason": "简短原因"
        }
      ]
    }
  ]
}

要求：
- 每个时间段都必须有决策
- operations列表包含该时间段所在房间的所有电器的状态决策
- action只能是"开启"或"关闭"
- reason简短说明为什么这样决策（可选，用于调试）
