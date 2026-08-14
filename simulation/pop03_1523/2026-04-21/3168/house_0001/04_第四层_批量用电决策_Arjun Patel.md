Token使用: prompt_cache_miss=56454, prompt_cache_hit=7936, completion=144632

# 04_第四层_批量用电决策_Arjun Patel

生成时间: 2026-08-14 15:34:03

---

## 提示词

```
你是一个家庭用电行为专家。请为Arjun Patel的一天生成完整的用电决策。

成员信息：
- 姓名：Arjun Patel
- 年龄：24
- 职业：国际学生/兼职咖啡师
- 习惯：{
  "wake_time": "10:00",
  "sleep_time": "02:00",
  "exercise": "从不锻炼",
  "hobbies": [
    "打游戏",
    "刷TikTok",
    "阅读"
  ]
}

该成员的完整时间线：
[
  {
    "time": "00:00-07:30",
    "location": "卧室1",
    "activity": "睡眠（与Mei-Ling同步睡眠）",
    "desc": "躺在床上。闭上眼睛。翻身。调整枕头。把手放在肚子上。转成侧卧。打哈欠。踢腿。拉过被子。翻身到另一侧。动动手指。睁开眼睛。坐起身。"
  },
  {
    "time": "07:30-07:50",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "下床。穿拖鞋。进卫生间。开灯。拧开水龙头。洗脸。拿起牙刷。挤牙膏。刷牙。漱口。关水龙头。擦脸。"
  },
  {
    "time": "07:50-08:20",
    "location": "卧室1",
    "activity": "换衣、整理仪容",
    "desc": "走进卧室。打开衣柜。取出一件衬衫。脱下睡衣。穿上衬衫。扣上扣子。拿起裤子。穿上裤子。拉上拉链。扣上腰带。照镜子。整理头发。喷发胶。再看镜子。拿上手机。"
  },
  {
    "time": "08:20-08:55",
    "location": "厨房",
    "activity": "准备早餐（为与Mei-Ling共进早餐做准备）",
    "desc": "走进厨房。系上围裙。打开冰箱。拿出鸡蛋。关上冰箱。打开电磁炉。倒油。打鸡蛋入锅。用铲子翻炒。盛到盘子。烤面包。涂果酱。热牛奶。取出牛奶。将早餐端到餐桌。摆放餐具。倒橙汁。喊Mei-Ling吃饭。"
  },
  {
    "time": "08:55-09:15",
    "location": "厨房",
    "activity": "与Mei-Ling一起吃早餐",
    "desc": "在餐桌坐下。拿起叉子。叉起煎蛋。送入口中。咀嚼。放下叉子。拿起杯子。喝一口牛奶。拿起面包。咬一口。擦嘴。起身。"
  },
  {
    "time": "09:15-09:40",
    "location": "外出",
    "activity": "与Mei-Ling一同步行去莫纳什大学",
    "desc": "从椅子上站起。拿起背包。背上。拿起雨伞。与Mei-Ling一起走出家门。按下电梯按钮。等待。进入电梯。走出电梯。走出公寓楼。撑开雨伞。步行。过马路。"
  },
  {
    "time": "09:40-11:20",
    "location": "外出",
    "activity": "在莫纳什大学图书馆自习（等待上课）",
    "desc": "走进图书馆。找到空桌。放下背包。坐下。取出笔记本电脑。打开电脑。按电源键。输入密码。打开文档。滑动鼠标。点击页面。打字。拿起手机。查看。放下手机。从包中拿出笔记本。拿起笔。写字。喝水。伸懒腰。收拾桌面。"
  },
  {
    "time": "11:20-13:30",
    "location": "外出",
    "activity": "在莫纳什大学上课",
    "desc": "走出图书馆。走进教学楼。进入教室。找座位。坐下。拿出笔记本。打开笔。抬头看黑板。听讲。低头记笔记。举手。回答问题。翻看课本。与邻座讨论。看手表。喝水。继续听讲。收拾书本。拿出手机。看消息。"
  },
  {
    "time": "13:30-14:00",
    "location": "外出",
    "activity": "在学校食堂吃午餐",
    "desc": "离开教室。走进食堂。排队。看菜单。点餐。刷卡付款。端餐盘。找座位。坐下。拿起筷子。夹菜。吃饭。喝汤。擦嘴。收拾餐盘。"
  },
  {
    "time": "14:00-15:00",
    "location": "外出",
    "activity": "在图书馆自习",
    "desc": "走进图书馆。找到座位。放下书包。打开电脑。启动。打开学习资料。滚动页面。点击鼠标。记笔记。拿笔写字。搜索资料。看手机。回复消息。放回手机。喝口水。继续学习。伸懒腰。设置计时器。"
  },
  {
    "time": "15:00-15:30",
    "location": "外出",
    "activity": "通勤去咖啡馆（步行/公交）",
    "desc": "从图书馆出来。走到公交站。拿出手机。看时间。等车。车来。刷卡。上车。找座位。坐下。戴耳机。听音乐。看窗外。到站。下车。走向咖啡馆。推门进入。"
  },
  {
    "time": "15:30-18:00",
    "location": "外出",
    "activity": "在咖啡馆工作（兼职咖啡师）",
    "desc": "进入员工区。换工作服。系围裙。洗手。清理咖啡机。预热机器。研磨咖啡豆。装入手柄。压实。扣上咖啡机。按萃取键。萃取咖啡。取杯。倒入牛奶。蒸汽棒打奶泡。将奶泡倒入咖啡。拉花。递出咖啡。擦吧台。收银。"
  },
  {
    "time": "18:00-19:00",
    "location": "外出",
    "activity": "与朋友社交，喝咖啡",
    "desc": "下班。在咖啡馆座位坐下。端杯咖啡。与朋友聊天。大笑。拿出手机。滑屏幕。给朋友看照片。放手机。喝咖啡。继续谈话。碰拳。起身。拿外套。"
  },
  {
    "time": "19:00-19:30",
    "location": "外出",
    "activity": "通勤回家",
    "desc": "走出咖啡馆。撑开伞。步行到公交站。等车。看手机。车来。上车。刷卡。坐下。靠着窗。闭眼休息。到站。下车。走到公寓楼。收伞。按电梯。"
  },
  {
    "time": "19:30-20:00",
    "location": "厨房",
    "activity": "与Mei-Ling一起吃晚餐（Mei-Ling的晚餐时间为18:30-20:00）",
    "desc": "走进餐厅。洗手。在餐桌前坐下。拿起碗筷。盛饭。夹菜。送入口中。咀嚼。喝汤。与Mei-Ling交谈。放下筷子。擦嘴。"
  },
  {
    "time": "20:00-20:15",
    "location": "厨房",
    "activity": "与Mei-Ling一起洗碗、清洁厨房",
    "desc": "放下碗筷。收拾碗碟。端到水槽。打开水龙头。挤洗洁精。用海绵擦洗。冲洗。擦干。放回橱柜。擦桌子。"
  },
  {
    "time": "20:15-21:15",
    "location": "客厅",
    "activity": "使用电脑看视频、刷社交",
    "desc": "走进客厅。坐在沙发上。拿起笔记本电脑。打开。放在腿上。按电源键。等待启动。点击浏览器。输入网址。打开视频。点击播放。观看。按空格暂停。移动鼠标。打开社交媒体。滑动页面。点击消息。打字回复。放下电脑。拿起手机。浏览手机。"
  },
  {
    "time": "21:15-21:45",
    "location": "客厅",
    "activity": "与Mei-Ling一起泡茶、品尝茶",
    "desc": "与Mei-Ling一起到厨房。打开水壶。接水。放到底座。按下开关。水烧开。提壶。拿茶壶。放茶叶。倒水入壶。等待。倒茶入杯。端给Mei-Ling。端自己的杯。回到客厅。坐下。品尝。"
  },
  {
    "time": "21:45-22:30",
    "location": "客厅",
    "activity": "阅读或学习",
    "desc": "坐在沙发上。拿起书。翻到上次位置。阅读。翻页。拿出笔记本。记笔记。翻页。揉眼睛。看手机。放下。继续阅读。调整坐姿。打哈欠。合上书。"
  },
  {
    "time": "22:30-22:45",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "从沙发上站起。走进卫生间。打开灯。拿起牙刷。挤牙膏。刷牙。漱口。洗脸。擦干。关灯。"
  },
  {
    "time": "22:45-23:00",
    "location": "卧室1",
    "activity": "换睡衣、睡前准备",
    "desc": "走进卧室。打开衣柜。取出睡衣。脱掉外套。穿上睡衣。坐在床边。整理枕头。拿起手机。设置闹钟。放在床头充电。"
  },
  {
    "time": "23:00-23:30",
    "location": "卧室1",
    "activity": "与Mei-Ling一起睡前阅读（各自看书）",
    "desc": "靠在床头。打开台灯。拿起书。翻开。阅读。翻页。与Mei-Ling交谈。翻页。揉眼睛。放下书。关闭台灯。躺下。"
  },
  {
    "time": "23:30-23:59",
    "location": "卧室1",
    "activity": "睡眠（与Mei-Ling同步睡眠）",
    "desc": "闭上眼睛。翻身。调整睡姿。拉起被子。在枕头上转过头。平静下来。入睡。"
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
        "unique_id": "客厅_灯",
        "name": "灯",
        "type": "on_demand",
        "power_watts": 40,
        "brand": "Philips",
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
        "unique_id": "客厅_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Fujitsu",
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
        "age": 5,
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
        "brand": "Midea",
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
        "unique_id": "厨房_电饭煲",
        "name": "电饭煲",
        "type": "on_demand",
        "power_watts": 800,
        "brand": "Tiger",
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
        "age": 6,
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
        "brand": "Haier",
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
  "卧室1": {
    "appliances": [
      {
        "unique_id": "卧室1_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "Mitsubishi",
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
        "unique_id": "卧室1_灯",
        "name": "灯",
        "type": "on_demand",
        "power_watts": 40,
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
      },
      {
        "unique_id": "卧室1_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "Xiaomi",
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
        "unique_id": "卧室1_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "Apple",
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
        "unique_id": "卧室1_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Dell",
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
  "卧室2": {
    "appliances": [
      {
        "unique_id": "卧室2_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
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
        "unique_id": "卧室2_灯",
        "name": "灯",
        "type": "on_demand",
        "power_watts": 40,
        "brand": "Philips",
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
        "unique_id": "卧室2_台灯",
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
      },
      {
        "unique_id": "卧室2_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "Samsung",
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
        "unique_id": "卧室2_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "HP",
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
  "卧室3": {
    "appliances": [
      {
        "unique_id": "卧室3_空调",
        "name": "空调",
        "type": "on_demand",
        "power_watts": 2000,
        "brand": "LG",
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
        "unique_id": "卧室3_灯",
        "name": "灯",
        "type": "on_demand",
        "power_watts": 40,
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
      },
      {
        "unique_id": "卧室3_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
        "brand": "Muji",
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
        "unique_id": "卧室3_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "Google",
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
        "unique_id": "卧室3_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Lenovo",
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
  "Arjun Patel的个人电器": {
    "appliances": [
      {
        "unique_id": "arjun_patel_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "Samsung",
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
        "unique_id": "arjun_patel_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "HP",
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
        "unique_id": "arjun_patel_台灯",
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
  }
}

环境信息：
- 季节：秋天
- 天气：阵雨
- 温度：14度





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
  "member": "Arjun Patel",
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
  "member": "Arjun Patel",
  "appliance_decisions": [
{
      "time": "00:00-07:30",
      "location": "卧室1",
      "activity": "睡眠（与Mei-Ling同步睡眠）",
      "operations": [
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "07:30-07:50",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "07:50-08:20",
      "location": "卧室1",
      "activity": "换衣、整理仪容",
      "operations": [
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "use"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "08:20-08:55",
      "location": "厨房",
      "activity": "准备早餐（为与Mei-Ling共进早餐做准备）",
      "operations": [
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "08:55-09:15",
      "location": "厨房",
      "activity": "与Mei-Ling一起吃早餐",
      "operations": [
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "09:15-09:40",
      "location": "外出",
      "activity": "与Mei-Ling一同步行去莫纳什大学",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "09:40-11:20",
      "location": "外出",
      "activity": "在莫纳什大学图书馆自习（等待上课）",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "use"},
{"unique_id": "arjun_patel_电脑", "action": "use"}
      ]
    },
{
      "time": "11:20-13:30",
      "location": "外出",
      "activity": "在莫纳什大学上课",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "use"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "13:30-14:00",
      "location": "外出",
      "activity": "在学校食堂吃午餐",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "14:00-15:00",
      "location": "外出",
      "activity": "在图书馆自习",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "use"},
{"unique_id": "arjun_patel_电脑", "action": "use"}
      ]
    },
{
      "time": "15:00-15:30",
      "location": "外出",
      "activity": "通勤去咖啡馆（步行/公交）",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "use"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "15:30-18:00",
      "location": "外出",
      "activity": "在咖啡馆工作（兼职咖啡师）",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "18:00-19:00",
      "location": "外出",
      "activity": "与朋友社交，喝咖啡",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "use"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "19:00-19:30",
      "location": "外出",
      "activity": "通勤回家",
      "operations": [
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "19:30-20:00",
      "location": "厨房",
      "activity": "与Mei-Ling一起吃晚餐（Mei-Ling的晚餐时间为18:30-20:00）",
      "operations": [
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "20:00-20:15",
      "location": "厨房",
      "activity": "与Mei-Ling一起洗碗、清洁厨房",
      "operations": [
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "20:15-21:15",
      "location": "客厅",
      "activity": "使用电脑看视频、刷社交",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "use"},
{"unique_id": "arjun_patel_电脑", "action": "use"}
      ]
    },
{
      "time": "21:15-21:45",
      "location": "客厅",
      "activity": "与Mei-Ling一起泡茶、品尝茶",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "21:45-22:30",
      "location": "客厅",
      "activity": "阅读或学习",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "22:30-22:45",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "idle"}
      ]
    },
{
      "time": "22:45-23:00",
      "location": "卧室1",
      "activity": "换睡衣、睡前准备",
      "operations": [
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "use"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "charge_home"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "23:00-23:30",
      "location": "卧室1",
      "activity": "与Mei-Ling一起睡前阅读（各自看书）",
      "operations": [
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "use"},
{"unique_id": "arjun_patel_手机", "action": "charge_home"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    },
{
      "time": "23:30-23:59",
      "location": "卧室1",
      "activity": "睡眠（与Mei-Ling同步睡眠）",
      "operations": [
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "arjun_patel_手机", "action": "charge_home"},
{"unique_id": "arjun_patel_电脑", "action": "idle"}
      ]
    }
  ]
}
```
