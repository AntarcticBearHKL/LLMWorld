Token使用: prompt_cache_miss=21814, prompt_cache_hit=0, completion=51346

# 04_第四层_批量用电决策_Mei-Ling Zhang

生成时间: 2026-08-14 15:29:21

---

## 提示词

```
你是一个家庭用电行为专家。请为Mei-Ling Zhang的一天生成完整的用电决策。

成员信息：
- 姓名：Mei-Ling Zhang
- 年龄：28
- 职业：注册护士
- 习惯：{
  "wake_time": "07:30",
  "sleep_time": "00:30",
  "exercise": "偶尔散步或拉伸",
  "hobbies": [
    "逛折扣店",
    "画插画",
    "看YouTube",
    "阅读"
  ]
}

该成员的完整时间线：
[
  {
    "time": "00:00-00:30",
    "location": "卧室",
    "activity": "睡前在手机上浏览艺术类内容，准备入睡",
    "desc": "躺在床。拿起手机。打开艺术类应用。滑动屏幕浏览图片。关闭手机。将手机放在床头柜。闭上眼睛。"
  },
  {
    "time": "00:30-07:30",
    "location": "卧室",
    "activity": "睡觉",
    "desc": "保持躺卧。闭眼。入睡。偶尔翻身。"
  },
  {
    "time": "07:30-07:45",
    "location": "卧室",
    "activity": "起床，整理床铺，换衣服",
    "desc": "睁开眼。坐起身。掀开被子。下床站立。拉平床单。叠好被子。从衣柜取出便服。脱下睡衣。穿上便服。"
  },
  {
    "time": "07:45-08:00",
    "location": "卫生间",
    "activity": "洗漱，护肤",
    "desc": "走进卫生间。打开灯。拧开水龙头。用手捧水洗脸。关水龙头。拿起毛巾擦干脸。拿起牙刷。挤牙膏。刷牙。含水漱口。冲洗牙刷。将牙刷放回。倒爽肤水在手上。拍在脸上。涂保湿乳液。"
  },
  {
    "time": "08:00-08:30",
    "location": "厨房",
    "activity": "准备并吃早餐，同时用手机看艺术类视频",
    "desc": "走进厨房。打开冰箱取出牛奶和鸡蛋。关冰箱。打开电磁炉。放平底锅。倒入油。打入鸡蛋。煎蛋。从橱柜取出杯子。把牛奶倒进杯子。把杯子放入微波炉。启动微波炉。取出热牛奶。将煎蛋盛入盘子。从冰箱取出面包。拿面包片放在盘子里。坐在餐桌前。拿起手机，打开视频应用。边吃早餐边看视频。与Arjun交谈，互道早安。"
  },
  {
    "time": "08:30-09:00",
    "location": "厨房",
    "activity": "清洗餐具，整理厨房",
    "desc": "站起身。收拾碗筷。端到水槽边。打开水龙头。挤洗洁精。用海绵刷洗盘子。冲洗干净。放沥水架。擦干碗盘。放回橱柜。用抹布擦餐桌。把剩余食材放回冰箱。清理台面。"
  },
  {
    "time": "09:00-11:00",
    "location": "书房",
    "activity": "用电脑画插画，浏览艺术设计网站获取灵感",
    "desc": "走进书房。坐在电脑桌前。按下电脑电源键。等待开机。移动鼠标。打开绘图软件。点击新建画布。拿起数位笔。在数位板上绘制线条。点击调色板选择颜色。滚动鼠标轮放大画布。继续绘制。使用快捷键切换工具。打开浏览器。输入艺术设计网站网址。滚动页面浏览图片。点击图片查看大图。返回绘图软件。继续绘制。保存画稿。"
  },
  {
    "time": "11:00-11:15",
    "location": "客厅",
    "activity": "做简单的拉伸运动",
    "desc": "走到客厅。站立。举起双臂向头顶伸展。弯腰用手触碰脚尖。转动脖子。活动手腕。伸展腿部。走回厨房。"
  },
  {
    "time": "11:15-11:45",
    "location": "厨房",
    "activity": "准备午餐（健康素食搭配）",
    "desc": "打开冰箱。取出生菜、番茄和黄瓜。放在案板上。拧开水龙头冲洗蔬菜。关水龙头。用刀切番茄和黄瓜。生菜撕成小片。将蔬菜放入碗中。从橱柜取出盘子。将蔬菜装盘。淋上橄榄油。撒盐和黑胡椒。用筷子拌匀。"
  },
  {
    "time": "11:45-12:15",
    "location": "厨房",
    "activity": "吃午餐",
    "desc": "坐在餐桌前。拿起筷子。夹取蔬菜。送入口中。咀嚼吞咽。偶尔拿起水杯喝水。放下筷子。用餐巾擦嘴。"
  },
  {
    "time": "12:15-12:30",
    "location": "厨房",
    "activity": "收拾餐具，清理台面",
    "desc": "站起身。拿起碗筷。端到水槽。打开水龙头。冲洗碗筷。擦干。放回橱柜。用抹布擦餐桌。清洗案板。擦干放好。清理台面。"
  },
  {
    "time": "12:30-13:30",
    "location": "卧室",
    "activity": "午休小憩，恢复精力",
    "desc": "走进卧室。脱下便服。躺到床上。闭上眼睛。保持休息。偶尔翻身。"
  },
  {
    "time": "13:30-14:00",
    "location": "卧室",
    "activity": "更换护士制服，整理上班随身物品",
    "desc": "起身下床。走到衣柜。取出护士服和护士裤。穿上护士服和护士裤。穿上袜子。穿上工作鞋。拿起梳子梳理头发。拿起手机和工牌。放入背包。检查背包内物品。拉上背包拉链。"
  },
  {
    "time": "14:00-14:30",
    "location": "外出",
    "activity": "通勤去医院（乘坐公共交通）",
    "desc": "走出家门。步行至公交站。站在站点等候。公交车到站。上车。刷卡。找座位坐下。拿出手机浏览。听到报站。下车。步行至医院大门。"
  },
  {
    "time": "14:30-22:30",
    "location": "外出",
    "activity": "在医院上班，进行护理工作、记录患者情况、参与团队会议等",
    "desc": "进入医院。走进护士站。打卡签到。查看交班记录本。拿起血压计和听诊器。走进病房。为患者测量血压。记录数值。为患者测体温。在表格上记录。到配药室。按处方配药。核对药品名称。推治疗车进入病房。为患者输液。调节输液速度。巡视病房。观察患者情况。与患者简短交流。参加团队会议。坐在会议室。听取汇报。记录笔记。回到护士站。填写护理记录。处理呼叫铃响。协助患者翻身。"
  },
  {
    "time": "22:30-23:00",
    "location": "外出",
    "activity": "下班通勤回家（乘坐公共交通）",
    "desc": "走出医院。步行至公交站。在站点等候。公交车到站。上车。刷卡。找座位坐下。闭眼休息。听到报站。下车。步行回家。用钥匙开门。"
  },
  {
    "time": "23:00-23:30",
    "location": "卫生间",
    "activity": "洗漱，卸妆，护肤",
    "desc": "走进卫生间。打开灯。拿起卸妆棉。倒卸妆水。擦拭面部。卸除唇妆。用洗面奶搓出泡沫。涂抹面部。用清水冲洗。用毛巾擦干。倒爽肤水在手上。拍在脸上。涂保湿乳液。关灯。"
  },
  {
    "time": "23:30-23:59",
    "location": "卧室",
    "activity": "换上睡衣，坐在床上阅读或放空，准备入睡",
    "desc": "进入卧室。从衣柜取出睡衣。脱下护士服。穿上睡衣。坐在床边。拿起纸质书。翻阅阅读。放下书。躺下。盖上被子。闭上眼睛。"
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
        "brand": "Sony",
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
        "unique_id": "厨房_微波炉",
        "name": "微波炉",
        "type": "on_demand",
        "power_watts": 1000,
        "brand": "Panasonic",
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
        "unique_id": "厨房_电饭煲",
        "name": "电饭煲",
        "type": "on_demand",
        "power_watts": 800,
        "brand": "Midea",
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
        "unique_id": "厨房_电磁炉",
        "name": "电磁炉",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Bosch",
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
        "unique_id": "厨房_油烟机",
        "name": "油烟机",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Bosch",
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
        "brand": "Rheem",
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
        "unique_id": "卫生间_洗衣机",
        "name": "洗衣机",
        "type": "on_demand",
        "power_watts": 500,
        "brand": "Samsung",
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
        "unique_id": "卫生间_灯",
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
  "卧室": {
    "appliances": [
      {
        "unique_id": "卧室_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Fujitsu",
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
        "unique_id": "卧室_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "YiLight",
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
        "unique_id": "卧室_灯",
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
  "书房": {
    "appliances": [
      {
        "unique_id": "书房_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Apple",
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
        "unique_id": "书房_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "BenQ",
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
        "unique_id": "书房_灯",
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
  "Mei-Ling Zhang的个人电器": {
    "appliances": [
      {
        "unique_id": "mei_ling_zhang_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "Apple",
        "age": 2,
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
        "unique_id": "mei_ling_zhang_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Apple",
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
  }
}

环境信息：
- 季节：夏天
- 天气：多云
- 温度：31度





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
  "member": "Mei-Ling Zhang",
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
  "member": "Mei-Ling Zhang",
  "appliance_decisions": [
{
      "time": "00:00-00:30",
      "location": "卧室",
      "activity": "睡前在手机上浏览艺术类内容，准备入睡",
      "operations": [
{"unique_id": "卧室_空调", "action": "use"},
{"unique_id": "卧室_台灯", "action": "use"},
{"unique_id": "卧室_灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "use"}
      ]
    },
{
      "time": "00:30-07:30",
      "location": "卧室",
      "activity": "睡觉",
      "operations": [
{"unique_id": "卧室_空调", "action": "idle"},
{"unique_id": "卧室_台灯", "action": "idle"},
{"unique_id": "卧室_灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "charge_home"}
      ]
    },
{
      "time": "07:30-07:45",
      "location": "卧室",
      "activity": "起床，整理床铺，换衣服",
      "operations": [
{"unique_id": "卧室_空调", "action": "idle"},
{"unique_id": "卧室_台灯", "action": "idle"},
{"unique_id": "卧室_灯", "action": "use"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "07:45-08:00",
      "location": "卫生间",
      "activity": "洗漱，护肤",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"},
{"unique_id": "卫生间_灯", "action": "use"}
      ]
    },
{
      "time": "08:00-08:30",
      "location": "厨房",
      "activity": "准备并吃早餐，同时用手机看艺术类视频",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "use"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "mei_ling_zhang_手机", "action": "use"}
      ]
    },
{
      "time": "08:30-09:00",
      "location": "厨房",
      "activity": "清洗餐具，整理厨房",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "09:00-11:00",
      "location": "书房",
      "activity": "用电脑画插画，浏览艺术设计网站获取灵感",
      "operations": [
{"unique_id": "书房_电脑", "action": "use"},
{"unique_id": "书房_台灯", "action": "use"},
{"unique_id": "书房_灯", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "11:00-11:15",
      "location": "客厅",
      "activity": "做简单的拉伸运动",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"}
      ]
    },
{
      "time": "11:15-11:45",
      "location": "厨房",
      "activity": "准备午餐（健康素食搭配）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "11:45-12:15",
      "location": "厨房",
      "activity": "吃午餐",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "12:15-12:30",
      "location": "厨房",
      "activity": "收拾餐具，清理台面",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "12:30-13:30",
      "location": "卧室",
      "activity": "午休小憩，恢复精力",
      "operations": [
{"unique_id": "卧室_空调", "action": "use"},
{"unique_id": "卧室_台灯", "action": "idle"},
{"unique_id": "卧室_灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "13:30-14:00",
      "location": "卧室",
      "activity": "更换护士制服，整理上班随身物品",
      "operations": [
{"unique_id": "卧室_空调", "action": "idle"},
{"unique_id": "卧室_台灯", "action": "idle"},
{"unique_id": "卧室_灯", "action": "use"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "14:00-14:30",
      "location": "外出",
      "activity": "通勤去医院（乘坐公共交通）",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"}
      ]
    },
{
      "time": "14:30-22:30",
      "location": "外出",
      "activity": "在医院上班，进行护理工作、记录患者情况、参与团队会议等",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"}
      ]
    },
{
      "time": "22:30-23:00",
      "location": "外出",
      "activity": "下班通勤回家（乘坐公共交通）",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"}
      ]
    },
{
      "time": "23:00-23:30",
      "location": "卫生间",
      "activity": "洗漱，卸妆，护肤",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"},
{"unique_id": "卫生间_灯", "action": "use"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    },
{
      "time": "23:30-23:59",
      "location": "卧室",
      "activity": "换上睡衣，坐在床上阅读或放空，准备入睡",
      "operations": [
{"unique_id": "卧室_空调", "action": "use"},
{"unique_id": "卧室_台灯", "action": "use"},
{"unique_id": "卧室_灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"}
      ]
    }
  ]
}
```
