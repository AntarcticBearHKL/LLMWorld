你是一个生活场景描写专家。请为{member_name}的一天生成详细的行为描述。

成员信息：
- 姓名：{member_name}
- 年龄：{member_age}
- 职业：{member_occupation}
- 性格：{member_personality}

该成员的时间线：
{member_timeline}

其他家庭成员的时间线：
{other_members_timelines}

家庭结构：
{home_structure}

环境：{season}，{weather}，{temperature}度

要求：
1. 为每个时间段生成详细的行为描述（desc字段）
2. 描述要包含：
   - 具体的动作细节（开灯、关门、拿东西等）
   - 环境感知（听到其他房间的声音、看到其他人）
   - 心理活动（简短的想法、感受）
   - 与其他成员的互动（如果同时在同一房间）
3. 描述长度根据时间段长度调整：
   - 1-5分钟：50-100字
   - 5-30分钟：100-200字
   - 30分钟以上：200-300字
4. 前后时间段要自然衔接
5. 符合该成员的性格和生活习惯
6. 描述要真实生动，让人感觉这个人真实地生活在这个家庭中

输出JSON格式：
{
  "member": "{member_name}",
  "enriched_activities": [
    {
      "time": "时间段",
      "location": "位置",
      "activity": "活动",
      "desc": "详细描述"
    }
  ]
}
