你是一个家庭用电行为专家。请根据以下信息，决定该时间段需要操作哪些家电。

家庭结构：
{{home_structure}}

时间段信息：
- 时间：{{time}}
- 人物：{{member_name}}（{{member_age}}岁，{{member_occupation}}）
- 地点：{{location}}
- 活动：{{activity}}

环境信息：
- 季节：{{season}}
- 天气：{{weather}}
- 气温：{{temperature}}度

{{location}}的家电：
{{appliances_info}}

当前电器状态：
{{status_str}}

人物用电习惯：
- {{member_habits}}

请决策：
1. 需要开启哪些家电（如果已经开启则不需要重复开启）
2. 需要关闭哪些家电
3. 每个操作的原因

要求：
- 只操作家中的电器，不涉及家外的设备
- 符合活动需求
- 符合人物习惯
- 合理真实
- 检查电器当前状态，避免重复操作

输出JSON格式：
{
  "operations": [
    {"appliance": "家电名称", "action": "开启/关闭", "reason": "原因"}
  ]
}
