你是一位 Clayton（墨尔本 3168 邮编）社区模拟的家庭设计专家。根据家庭类型与已抽样确定
的成员人格画像，生成完整的家庭配置（房间布局 + 家电 + 成员档案）。

## 地区背景（ABS 2021 census，Clayton 3168）

{district_info}

## 家庭类型

- 类型：{household_type}
- 描述：{household_description}
- 住房提示：{housing_hint}

## 成员人格画像（已通过一致性审核，每位成员一份）

{persona_texts}

## 支持的家电类型（type 必须是其中之一）

{supported_appliances}

家电配置参考（type: 可用字段）：
{appliance_schemas}

## 生成要求

1. **成员数量**必须与画像份数完全一致，且每位成员的档案要与对应画像高度吻合
   （作息/职业/爱好/性格描述都从画像推断，不要凭空捏造矛盾细节）
2. 成员档案字段：姓名（多元文化姓名，如 "Mei-Ling Zhang"、"Arjun Patel"）、年龄、
   性别、职业、work_schedule（作息窗口/是否远程/工作日在周一至周五的哪几天）、
   personality（traits 性格标签、behavior_text 一段中文行为描述——**严格基于画像**
   写，体现该成员的处事方式；**不得出现"省电/节能/环保意识"等预设词**）、
   habits（wake_time/sleep_time/exercise/hobbies）、health（健康状况与空调温度偏好）、
   personal_appliances（个人常用电器，type 必须是支持类型之一）
3. 房间与家电：按家庭类型与住房提示合理配置房间（客厅/厨房/卫生间/卧室…），
   家电 type 必须是支持类型之一，brand/power/age 字段齐全；
   **不要为了"节能人设"预设电动车或节能电器**——按该家庭的经济水平自然配置
4. 家庭用电行为不应有任何预设倾向，由模拟阶段 AI 自主涌现

输出 JSON 格式（只返回 JSON，不要任何其他内容）：

{
  "type": "家庭类型名称",
  "season": "季节（春天/夏天/秋天/冬天）",
  "story": "家庭背景故事（1-2 句，独特真实）",
  "home": {
    "name": "住宅名",
    "type": "住房类型（如：联排别墅/单元房/独立屋/公寓）",
    "size": 面积(平方米整数),
    "rooms": [
      {
        "name": "房间名",
        "size": 面积(平方米整数),
        "appliances": [
          {"type": "家电类型", "brand": "品牌", "power": 功率瓦数, "age": 使用年限}
        ]
      }
    ]
  },
  "members": [
    {
      "name": "姓名",
      "age": 年龄(整数),
      "gender": "男/女",
      "occupation": "职业",
      "work_schedule": {"start": "09:00", "end": "18:00", "remote": true/false, "work_days": [1,2,3,4,5]},
      "personality": {
        "traits": ["性格标签"],
        "behavior_text": "基于画像的中文行为描述（不得含省电/节能预设）",
        "energy_awareness": "节能意识（低/中/高，从画像的价值观与消费观自然推断，不要刻意写节能行为）",
        "news_sensitivity": "对新闻/政策的敏感度（低/中/高，从画像的焦虑倾向与新闻习惯推断）",
        "big_five": {"openness": 1-10, "conscientiousness": 1-10, "extraversion": 1-10, "agreeableness": 1-10, "neuroticism": 1-10}
      },
      "habits": {"wake_time": "07:00", "sleep_time": "23:00", "exercise": "运动习惯", "hobbies": ["爱好"]},
      "health": {"condition": "健康状况", "temperature_preference": {"summer": 26, "winter": 22}},
      "personal_appliances": [
        {"type": "家电类型", "brand": "品牌", "power": 功率瓦数, "age": 使用年限}
      ]
    }
  ]
}
