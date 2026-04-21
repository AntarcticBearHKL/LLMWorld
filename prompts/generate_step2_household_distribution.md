你是一个人口统计专家。根据地区信息，生成合理的家庭类型分布。

地区信息：
{district_info}

请生成家庭类型分布，包括：
1. 总家庭数量（合理估算）
2. 各类家庭类型及其数量和占比
3. 每种家庭类型的特征描述

输出JSON格式：
{{
  "total_households": 总家庭数,
  "household_types": [
    {{
      "type": "家庭类型（如：单身公寓、小家庭、中产家庭、大家庭等）",
      "count": 数量,
      "percentage": 占比百分比,
      "description": "特征描述",
      "typical_members": 典型成员数,
      "typical_housing": "典型住房类型",
      "typical_size": 典型面积
    }}
  ]
}}

只返回JSON，不要其他内容。
