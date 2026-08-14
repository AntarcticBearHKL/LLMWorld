Token使用: prompt_cache_miss=54795, prompt_cache_hit=0, completion=115800

# 04_第四层_批量用电决策_Mei-Ling Patel

生成时间: 2026-08-14 15:32:51

---

## 提示词

```
你是一个家庭用电行为专家。请为Mei-Ling Patel的一天生成完整的用电决策。

成员信息：
- 姓名：Mei-Ling Patel
- 年龄：34
- 职业：医院行政人员
- 习惯：{
  "wake_time": "06:30",
  "sleep_time": "22:30",
  "exercise": "从不锻炼",
  "hobbies": [
    "逛便宜货市场",
    "去咖啡馆",
    "做慈善捐款"
  ]
}

该成员的完整时间线：
[
  {
    "time": "00:00-06:30",
    "location": "主卧",
    "activity": "睡觉",
    "desc": "躺在床上。闭眼。入睡。保持睡眠。翻身。6:30醒来。"
  },
  {
    "time": "06:30-07:00",
    "location": "卫生间",
    "activity": "洗漱",
    "desc": "起床。穿拖鞋。走进卫生间。开灯。打开水龙头。洗脸。擦干。刷牙。漱口。梳头。关水。关灯。"
  },
  {
    "time": "07:00-07:30",
    "location": "厨房",
    "activity": "准备和吃早餐",
    "desc": "走进厨房。打开冰箱。取出牛奶和鸡蛋。关冰箱。点燃炉灶。煎鸡蛋。倒牛奶。摆餐具。坐下。吃早餐。与Diya交谈。收拾碗碟。"
  },
  {
    "time": "07:30-08:00",
    "location": "外出",
    "activity": "通勤上班",
    "desc": "穿上外套。拿起手提包。换鞋。与Aarav一起出门。步行到公交站。等候公交车。上车。刷卡。找座位坐下。看向窗外。到站下车。走向医院。"
  },
  {
    "time": "08:00-17:00",
    "location": "外出",
    "activity": "在医院进行行政工作",
    "desc": "到达医院。进入办公室。放下包。打开电脑。登录系统。查看邮件。回复邮件。接听电话。记录信息。整理文件。打印资料。参加部门会议。记录要点。操作电脑录入数据。处理行政单据。与同事讨论工作。"
  },
  {
    "time": "17:00-17:30",
    "location": "外出",
    "activity": "通勤回家",
    "desc": "关闭电脑。收拾包。穿外套。离开办公室。走到公交站。等车。上车。刷卡。坐下。到站。下车。走回家。"
  },
  {
    "time": "17:30-18:00",
    "location": "客厅",
    "activity": "看手机放松并浏览社区信息",
    "desc": "进入客厅。坐在沙发上。拿出手机。解锁。打开社区App。浏览社区新闻。查看通知。滑动屏幕。阅读帖子。点赞评论。关闭手机。放下手机。"
  },
  {
    "time": "18:00-18:30",
    "location": "厨房",
    "activity": "做晚餐",
    "desc": "走进厨房。系上围裙。打开冰箱。取出蔬菜。在水槽清洗。放在砧板上切菜。点燃炉灶。往锅里倒油。放入食材翻炒。加入调味料。盛出装盘。摆放餐桌。"
  },
  {
    "time": "18:30-19:00",
    "location": "厨房",
    "activity": "吃晚餐",
    "desc": "端着菜走到餐桌。坐下。拿起碗筷。夹菜。咀嚼。喝汤。与家人交谈。继续吃饭。擦嘴。放下碗筷。起身收拾碗碟。"
  },
  {
    "time": "19:00-20:00",
    "location": "客厅",
    "activity": "看电视新闻",
    "desc": "走到客厅。坐在沙发上。拿起遥控器。打开电视。调到新闻频道。放下遥控器。看着电视。与Diya评论新闻。拿起水杯喝水。放下水杯。继续观看。调高音量。"
  },
  {
    "time": "20:00-21:00",
    "location": "客厅",
    "activity": "用电脑处理社区志愿者事务",
    "desc": "打开笔记本电脑。放在茶几上。坐在沙发上。登录社区网站。查看邮件。回复邮件。整理志愿者名单。编辑活动通知。发送消息。拨打电话确认细节。打印名单。关闭电脑。"
  },
  {
    "time": "21:00-22:00",
    "location": "主卧",
    "activity": "用手机查看明天日程并阅读",
    "desc": "走进主卧。打开衣柜。取出睡衣。换上睡衣。坐在床上。拿起手机。解锁。打开日历App。查看明天日程。滑动屏幕。阅读新闻文章。关闭手机。放到床头柜。"
  },
  {
    "time": "22:00-22:30",
    "location": "卫生间",
    "activity": "洗漱准备睡觉",
    "desc": "走进卫生间。开灯。拧开水龙头。挤牙膏。刷牙。漱口。洗脸。用毛巾擦干。涂护肤品。关水。关灯。走出卫生间。"
  },
  {
    "time": "22:30-23:59",
    "location": "主卧",
    "activity": "睡觉",
    "desc": "躺到床上。盖被子。闭眼。入睡。保持睡眠。"
  }
]

家庭结构和电器：
{
  "客厅": {
    "appliances": [
      {
        "unique_id": "客厅_电视",
        "name": "电视",
        "type": "on_demand",
        "power_watts": 150,
        "brand": "Samsung",
        "age": 3,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "客厅_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Daikin",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "客厅_灯",
        "name": "灯",
        "type": "on_demand",
        "power_watts": 40,
        "brand": "Philips",
        "age": 1,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "厨房": {
    "appliances": [
      {
        "unique_id": "厨房_冰箱",
        "name": "冰箱",
        "type": "always_on",
        "power_watts": 100,
        "brand": "LG",
        "age": 4,
        "is_exclusive": false,
        "available_actions": [],
        "description": "持续耗电设备（无需操作，自动运行）",
        "daily_energy_kwh": 1.2,
        "action_description": {}
      },
      {
        "unique_id": "厨房_电饭煲",
        "name": "电饭煲",
        "type": "on_demand",
        "power_watts": 800,
        "brand": "Panasonic",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "厨房_微波炉",
        "name": "微波炉",
        "type": "on_demand",
        "power_watts": 1000,
        "brand": "Sharp",
        "age": 5,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "厨房_电磁炉",
        "name": "电磁炉",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Bosch",
        "age": 1,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "厨房_油烟机",
        "name": "油烟机",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Westinghouse",
        "age": 3,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "厨房_灯",
        "name": "灯",
        "type": "on_demand",
        "power_watts": 40,
        "brand": "Philips",
        "age": 1,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "主卧": {
    "appliances": [
      {
        "unique_id": "主卧_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Daikin",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "主卧_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "IKEA",
        "age": 1,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "次卧1（Aarav）": {
    "appliances": [
      {
        "unique_id": "次卧1aarav_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Toshiba",
        "age": 4,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "次卧1aarav_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "IKEA",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "次卧2（Diya）": {
    "appliances": [
      {
        "unique_id": "次卧2diya_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Toshiba",
        "age": 4,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "次卧2diya_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "IKEA",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "卫生间": {
    "appliances": [
      {
        "unique_id": "卫生间_热水器",
        "name": "热水器",
        "type": "on_demand",
        "power_watts": 3000,
        "brand": "Rinnai",
        "age": 3,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "洗衣房": {
    "appliances": [
      {
        "unique_id": "洗衣房_洗衣机",
        "name": "洗衣机",
        "type": "on_demand",
        "power_watts": 500,
        "brand": "Bosch",
        "age": 3,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      },
      {
        "unique_id": "洗衣房_吸尘器",
        "name": "吸尘器",
        "type": "on_demand",
        "power_watts": 1200,
        "brand": "Dyson",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  },
  "Mei-Ling Patel的个人电器": {
    "appliances": [
      {
        "unique_id": "mei_ling_patel_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "Samsung",
        "age": 1,
        "is_exclusive": false,
        "available_actions": [
          "charge_home",
          "charge_external",
          "use",
          "idle"
        ],
        "description": "充电设备（可使用家庭电力或外部电力充电）",
        "action_description": {
          "charge_home": "使用家庭电力充电（计入家庭用电）",
          "charge_external": "使用外部电力充电（不计入家庭用电）",
          "use": "使用设备（消耗之前充入的电量，不耗电）",
          "idle": "不使用也不充电"
        }
      },
      {
        "unique_id": "mei_ling_patel_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Apple",
        "age": 2,
        "is_exclusive": false,
        "available_actions": [
          "use",
          "idle"
        ],
        "description": "使用时才耗电的设备（可开关）",
        "action_description": {
          "use": "使用该设备（耗电）",
          "idle": "不使用该设备（不耗电）"
        }
      }
    ]
  }
}

环境信息：
- 季节：春天
- 天气：晴天
- 温度：22度





## 电器类型说明

### 1. on_demand（按需使用电器）
- 描述：使用时才耗电的设备（如台灯、电视、空调）
- 可用操作：
  - "use": 使用该设备（耗电）
  - "idle": 不使用该设备（不耗电）

### 2. charging（充电设备）
- 描述：充电设备（如手机、电动汽车）
- 可用操作：
  - "charge_home": 使用家庭电力充电（计入家庭用电）
  - "charge_external": 使用外部电力充电（不计入家庭用电）
  - "use": 使用设备（消耗之前充入的电量，不耗电）
  - "idle": 不使用也不充电

### 3. always_on（持续耗电设备）
- 描述：持续耗电设备（如冰箱）
- 可用操作：无（自动运行，无需操作）

## 决策原则

1. **根据活动内容决策**：根据该成员的活动和所在房间，决定需要使用哪些电器
2. **只使用可用操作**：每个电器只能使用其 available_actions 中列出的操作
3. **always_on 设备无需决策**：冰箱等持续耗电设备自动运行，不要在输出中包含
4. **考虑环境因素**：季节、天气、温度影响用电需求（如夏天开空调）
5. **符合生活习惯**：根据成员的习惯特征决策
6. **注意节能**：离开房间时将该房间的电器设为 idle
7. **外出时的电器使用**：
   - 外出时把"外出"当作一个特殊的房间
   - 外出时可以使用个人电器（手机等）
   - 外出时可以选择充电方式：charge_home（家庭供电）或 charge_external（外部供电）
   - 具体的用电统计会在后续处理中根据电力来源进行筛选

## 典型使用时长（务必遵守，保持真实）

| 电器 | 典型一次使用时长 | 一天累计上限 |
|---|---|---|
| 电动汽车充电 | 晚上充 2-4 小时即可充满，**充满即停**；建议夜间 22:00 后充 | 4 小时 |
| 热水器 | 每次洗澡 15-30 分钟 | 45 分钟 |
| 空调 | 开 1-3 小时后可关（达到舒适温度） | 6 小时 |
| 洗衣机 | 一筒 1-1.5 小时 | 2 小时 |
| 电磁炉/电饭煲 | 做饭 30-60 分钟 | 2 小时 |
| 微波炉 | 加热 3-10 分钟 | 1 小时 |
| 电视 | 看 1-3 小时 | 8 小时 |
| 电脑 | 工作时段用 | 10 小时 |
| 手机充电 | 充 1-2 小时即满 | 4 小时 |
| 灯/台灯 | 人在房间就开 | 16 小时 |
| 吸尘器 | 一次清洁 15-30 分钟 | 1 小时 |
| 油烟机 | 做饭时开 | 2 小时 |

**重要**：不要连续长时间开大功率电器（空调/电动汽车/热水器）。比如电动汽车一天最多充 4 小时，充满后应设 idle。

## 典型使用时段（澳大利亚作息锚定，Xia et al. 2026）

| 时段 | 典型电器活动 |
|---|---|
| 6:30-8:00 起床/早餐 | 电饭煲/微波炉/电磁炉（早餐）、灯 |
| 8:00-17:00 工作时段 | 电脑（居家办公时）、待机 |
| 17:00-19:00 返家/晚餐 | 电磁炉/油烟机/电饭煲（晚餐）、热水器（洗浴） |
| 19:00-22:30 晚间休闲 | 电视/电脑/灯、洗衣机/吸尘器（按需） |
| 22:30-07:00 夜间 | 电动汽车充电（22:00 后开始，2-4 小时）、手机充电 |

- 空调：夏季炎热时段（12:00-21:00 按需），达到舒适温度即关
- 洗衣机/吸尘器：工作日傍晚或周末白天（勿在深夜运行，噪音）
- 以上为典型时段，须与成员时间线活动一致，允许合理偏差

## 输出格式

输出JSON格式：
{
  "member": "Mei-Ling Patel",
  "appliance_decisions": [
    {
      "time": "时间段（如 08:00-09:00）",
      "location": "房间名称",
      "activity": "活动描述",
      "operations": [
        {
          "unique_id": "电器唯一ID",
          "action": "操作（必须是该电器的 available_actions 之一）"
        }
      ]
    }
  ]
}

## 重要约束

1. **必须使用 unique_id**：不要使用电器名称，必须使用 unique_id（如 "living_tv"）
2. **操作必须合法**：action 必须在该电器的 available_actions 列表中
3. **跳过 always_on 设备**：不要为 always_on 类型的电器生成决策
4. **每个时间段都要决策**：为该成员时间线中的每个时间段生成决策
5. **根据位置决策电器**：在具体房间时决策该房间的电器，外出时决策个人电器

## 示例

假设成员在客厅看电视：
```json
{
  "time": "19:00-20:00",
  "location": "客厅",
  "activity": "看电视",
  "operations": [
    {"unique_id": "living_tv", "action": "use"},
    {"unique_id": "living_light", "action": "use"},
    {"unique_id": "living_ac", "action": "idle"}
  ]
}
```

假设成员在卧室睡觉并给手机充电：
```json
{
  "time": "23:00-07:00",
  "location": "卧室1",
  "activity": "睡觉",
  "operations": [
    {"unique_id": "bedroom1_lamp", "action": "idle"},
    {"unique_id": "dad_phone", "action": "charge_home"},
    {"unique_id": "bedroom1_computer", "action": "idle"}
  ]
}
```

假设成员外出购物并使用手机：
```json
{
  "time": "15:00-17:00",
  "location": "外出",
  "activity": "购物",
  "operations": [
    {"unique_id": "dad_phone", "action": "use"}
  ]
}
```

假设成员外出时在充电站给电动车充电：
```json
{
  "time": "16:00-17:00",
  "location": "外出",
  "activity": "在充电站给车充电",
  "operations": [
    {"unique_id": "garage_ev", "action": "charge_external"}
  ]
}
```

```

---

## LLM返回结果

```json
{
  "member": "Mei-Ling Patel",
  "appliance_decisions": [
{
      "time": "00:00-06:30",
      "location": "主卧",
      "activity": "睡觉",
      "operations": [
{"unique_id": "主卧_空调", "action": "idle"},
{"unique_id": "主卧_台灯", "action": "idle"},
{"unique_id": "mei_ling_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "06:30-07:00",
      "location": "卫生间",
      "activity": "洗漱",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"}
      ]
    },
{
      "time": "07:00-07:30",
      "location": "厨房",
      "activity": "准备和吃早餐",
      "operations": [
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_灯", "action": "use"}
      ]
    },
{
      "time": "07:30-08:00",
      "location": "外出",
      "activity": "通勤上班",
      "operations": [
{"unique_id": "mei_ling_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "08:00-17:00",
      "location": "外出",
      "activity": "在医院进行行政工作",
      "operations": [
{"unique_id": "mei_ling_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "17:00-17:30",
      "location": "外出",
      "activity": "通勤回家",
      "operations": [
{"unique_id": "mei_ling_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "17:30-18:00",
      "location": "客厅",
      "activity": "看手机放松并浏览社区信息",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "mei_ling_patel_手机", "action": "use"}
      ]
    },
{
      "time": "18:00-18:30",
      "location": "厨房",
      "activity": "做晚餐",
      "operations": [
{"unique_id": "厨房_电饭煲", "action": "use"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_灯", "action": "use"}
      ]
    },
{
      "time": "18:30-19:00",
      "location": "厨房",
      "activity": "吃晚餐",
      "operations": [
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_灯", "action": "use"}
      ]
    },
{
      "time": "19:00-20:00",
      "location": "客厅",
      "activity": "看电视新闻",
      "operations": [
{"unique_id": "客厅_电视", "action": "use"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "mei_ling_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "20:00-21:00",
      "location": "客厅",
      "activity": "用电脑处理社区志愿者事务",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "mei_ling_patel_电脑", "action": "use"},
{"unique_id": "mei_ling_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "21:00-22:00",
      "location": "主卧",
      "activity": "用手机查看明天日程并阅读",
      "operations": [
{"unique_id": "主卧_空调", "action": "idle"},
{"unique_id": "主卧_台灯", "action": "use"},
{"unique_id": "mei_ling_patel_手机", "action": "use"}
      ]
    },
{
      "time": "22:00-22:30",
      "location": "卫生间",
      "activity": "洗漱准备睡觉",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"}
      ]
    },
{
      "time": "22:30-23:59",
      "location": "主卧",
      "activity": "睡觉",
      "operations": [
{"unique_id": "主卧_空调", "action": "idle"},
{"unique_id": "主卧_台灯", "action": "idle"},
{"unique_id": "mei_ling_patel_手机", "action": "charge_home"}
      ]
    }
  ]
}
```
