你是一个家庭设计专家。根据地区信息和家庭类型，生成具体的家庭配置。

地区信息：
{district_info}

家庭类型：
{household_type}

支持的家电类型：{supported_appliances}

家电配置选项：
{appliance_schemas}

请生成完整的家庭配置，包括：
1. 家庭基本信息
2. 房间布局和家电配置
3. 家庭成员详细信息

输出JSON格式：
{{
  "type": "{household_type_name}",
  "season": "季节（春天/夏天/秋天/冬天）",
  "home": {{
    "name": "家庭名称",
    "type": "住房类型",
    "size": 面积,
    "rooms": [
      {{
        "name": "房间名",
        "size": 面积,
        "appliances": [
          {{
            "type": "家电类型（必须是支持的家电类型之一）",
            "brand": "品牌名称",
            "power": 功率瓦数,
            "age": 使用年限
          }}
        ]
      }}
    ]
  }},
  "members": [
    {{
      "name": "姓名",
      "age": 年龄,
      "gender": "性别",
      "occupation": "职业",
      "work_schedule": {{
        "start": "09:00",
        "end": "18:00",
        "remote": true/false,
        "work_days": [1,2,3,4,5]
      }},
      "personality": {{
        "traits": ["性格特点"],
        "energy_awareness": "节能意识（低/中/高）"
      }},
      "habits": {{
        "wake_time": "07:00",
        "sleep_time": "23:00",
        "exercise": "运动习惯",
        "hobbies": ["爱好"]
      }},
      "health": {{
        "condition": "健康状况",
        "temperature_preference": {{"summer": 26, "winter": 22}}
      }},
      "personal_appliances": [
        {{
          "type": "设备类型（必须是支持的家电类型之一）",
          "brand": "品牌名称",
          "power": 功率瓦数,
          "age": 使用年限
        }}
      ]
    }}
  ]
}}

只返回JSON，不要其他内容。
