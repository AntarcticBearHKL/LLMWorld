Token使用: prompt_cache_miss=56454, prompt_cache_hit=7936, completion=144632

# 04_第四层_批量用电决策_Priya Nair

生成时间: 2026-08-14 15:34:03

---

## 提示词

```
你是一个家庭用电行为专家。请为Priya Nair的一天生成完整的用电决策。

成员信息：
- 姓名：Priya Nair
- 年龄：23
- 职业：国际学生（莫纳什大学）
- 习惯：{
  "wake_time": "07:30",
  "sleep_time": "22:30",
  "exercise": "每周跑步或瑜伽",
  "hobbies": [
    "看剧",
    "听音乐",
    "烘焙"
  ]
}

该成员的完整时间线：
[
  {
    "time": "00:00-07:30",
    "location": "卧室2",
    "activity": "睡眠",
    "desc": "躺进被窝。闭上眼睛。翻了个身。调整枕头。入睡。睡眠中偶然翻身。将手臂伸出被子。缩回。继续睡。"
  },
  {
    "time": "07:30-07:40",
    "location": "卧室2",
    "activity": "起床、整理床铺、穿衣",
    "desc": "睁开眼睛。坐起身。掀开被子。下床。走到床边。弯腰拉平床单。将枕头放正。叠好被子。拿起衣服。穿上上衣。穿上裤子。穿上袜子。穿上鞋。"
  },
  {
    "time": "07:40-07:50",
    "location": "卧室2",
    "activity": "收拾房间、整理个人物品",
    "desc": "走到书桌前。将桌面物品摆放整齐。拿起书本放入书包。将水杯放好。检查书包内物品。拉开抽屉。整理抽屉内杂物。关闭抽屉。整理床上用品。将物品归位。"
  },
  {
    "time": "07:50-08:10",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "走进卫生间。打开灯。走到洗手台前。拧开水龙头。伸出手试水温。低头弯腰用双手接水。取洗面奶。涂抹在脸上。双手揉搓面部。用水冲洗。用毛巾擦干。拿起牙刷。挤上牙膏。开始刷牙。上下刷洗。俯身漱口。冲洗牙刷。放回牙杯。关水龙头。用毛巾擦手。关灯。"
  },
  {
    "time": "08:10-08:55",
    "location": "厨房",
    "activity": "与Arjun一起准备早餐（布置餐桌、热牛奶等）",
    "desc": "走进厨房。看到Arjun正在忙碌。向Arjun打招呼。走到冰箱前。打开冰箱门。取出牛奶。关上冰箱门。将牛奶倒入锅中。将锅放在电磁炉上。打开电磁炉开关。调节火候。从橱柜拿出碗和盘子。走到餐桌旁。摆放餐具。从冰箱取出水果。拿到水槽清洗。放在砧板上切块。将切好的水果放入碗中。走到锅边。查看牛奶是否热。关掉电磁炉。端起锅。将牛奶倒入杯中。将杯子端上餐桌。"
  },
  {
    "time": "08:55-09:15",
    "location": "厨房",
    "activity": "与Mei-Ling和Arjun一起吃早餐，并服药",
    "desc": "走到餐桌前。拉开椅子坐下。拿起一片面包。用果酱涂抹。咬一口面包。咀嚼。喝一口牛奶。与Mei-Ling交谈。放下食物。从衣袋取出药盒。打开药盒。取出一粒药片。拿起水杯喝一口水。将药片放入口中。咽下。继续吃早餐。"
  },
  {
    "time": "09:15-09:40",
    "location": "外出",
    "activity": "与Mei-Ling和Arjun一起步行去莫纳什大学",
    "desc": "起身离开餐桌。走回卧室。穿上外套。拿起雨伞。走到门口。换鞋。打开门。走出门。与Mei-Ling和Arjun一起走下台阶。沿街道行走。右转。路过一个公园。遇到十字路口。按按钮。等待绿灯。穿过马路。继续前行。到达莫纳什大学。"
  },
  {
    "time": "09:40-12:00",
    "location": "外出",
    "activity": "在莫纳什大学上课",
    "desc": "走进教学楼。找到教室。推门进入。环顾座位。走向空位。放下背包。坐下。从背包取出笔记本和笔。翻开笔记本。拿起笔。抬头看讲台。听老师讲授。低头记录笔记。翻页。听到同学提问。也举手发言。课间休息时，起身喝水。与旁边同学交谈。继续上课。做课堂练习。整理笔记。"
  },
  {
    "time": "12:00-13:00",
    "location": "外出",
    "activity": "在学校餐厅与Mei-Ling一起吃午餐",
    "desc": "下课收拾物品。背上背包。与Mei-Ling一起走出教室。走到学校餐厅。排队买午餐。查看今日菜单。点了一份鸡肉饭。拿出校园卡刷卡付款。端取餐盘。找到空位。坐下。与Mei-Ling聊天。打开饭盒。拿起筷子。夹起米饭。送入口中。咀嚼。喝一口汤。继续用餐。用餐完毕后，将餐盘放到回收处。走出餐厅。"
  },
  {
    "time": "13:00-15:00",
    "location": "外出",
    "activity": "在莫纳什大学上课/学习",
    "desc": "走进另一间教室。找到座位坐下。拿出电脑和书本。翻开课本。听讲并记笔记。参与小组讨论。课间休息。在校园学习空间继续学习。查阅资料。完成练习题。整理笔记。"
  },
  {
    "time": "15:00-17:00",
    "location": "外出",
    "activity": "在莫纳什大学图书馆自习（与Mei-Ling一起）",
    "desc": "走进图书馆。将书包放到座位。坐下。拿出书本。翻到需要学习的页码。开始阅读。用笔划重点。写笔记。偶尔抬头看看窗外。喝口水。与Mei-Ling低声讨论问题。继续学习。整理笔记。收拾物品。"
  },
  {
    "time": "17:00-17:30",
    "location": "外出",
    "activity": "与Mei-Ling一起步行回家",
    "desc": "收拾东西。背上书包。与Mei-Ling一起走出图书馆。穿上外套。打开伞。沿路散步。聊着一天的事。经过超市。进入超市买水果。付款。继续走。到达公寓楼下。开门。进入电梯。上楼。"
  },
  {
    "time": "17:30-18:30",
    "location": "卧室2",
    "activity": "休息、听音乐",
    "desc": "走进卧室。放下书包。换上家居服。走到床边。躺下。从床头柜拿起手机。打开音乐应用。选择播放列表。戴上耳机。闭上眼睛。听音乐。翻个身。伸展身体。调整音量。继续听。"
  },
  {
    "time": "18:30-20:00",
    "location": "厨房",
    "activity": "与Mei-Ling一起准备并享用晚餐（Arjun 19:30加入）",
    "desc": "走进厨房。系上围裙。打开水龙头。洗菜。将菜放在砧板上。切菜。打开电磁炉。倒油。放入食材。翻炒。加入调料。盛出。摆好餐桌。与Mei-Ling一起吃晚餐。聊天。Arjun迟到后加入。边吃边聊。加菜。"
  },
  {
    "time": "20:00-20:15",
    "location": "厨房",
    "activity": "与Mei-Ling和Arjun一起洗碗、清洁厨房",
    "desc": "站起来。收拾碗筷。将脏盘子端到水槽。拧开水龙头。挤洗洁精。用洗碗布擦拭。冲洗干净。放在沥水架。倒掉剩菜。擦桌子。清理水槽。擦干手。"
  },
  {
    "time": "20:15-21:15",
    "location": "卧室2",
    "activity": "阅读、学习",
    "desc": "走进卧室。坐到书桌前。打开台灯。从书包拿出书。翻开。阅读。用荧光笔划重点。做笔记。翻页。查字典。写总结。休息片刻。继续学习。"
  },
  {
    "time": "21:15-21:45",
    "location": "客厅",
    "activity": "与Mei-Ling和Arjun一起泡茶、品尝茶",
    "desc": "走到客厅。坐在沙发上。拿出茶壶。放入茶叶。倒入热水。等待冲泡。倒出茶水。端起茶杯。闻香。喝一口。与Mei-Ling和Arjun交谈。续杯。吃一点茶点。"
  },
  {
    "time": "21:45-22:15",
    "location": "卫生间",
    "activity": "洗漱、洗澡",
    "desc": "走进卫生间。脱去衣服。调好水温。打开淋浴。冲洗身体。涂沐浴露。揉搓。冲洗干净。关水。用毛巾擦干。穿上睡衣。走到洗手台。刷牙。漱口。洗脸。涂护肤品。走出卫生间。"
  },
  {
    "time": "22:15-22:30",
    "location": "卧室2",
    "activity": "冥想、祷告",
    "desc": "走进卧室。拿出瑜伽垫。铺在地上。盘腿坐下。双手放在膝上。闭上眼睛。深吸一口气。呼气。静坐。口中默念祷文。睁开眼。起身。收起垫子。"
  },
  {
    "time": "22:30-23:00",
    "location": "卧室2",
    "activity": "睡前放松（听轻音乐）",
    "desc": "关掉大灯。打开床头台灯。躺到床上。戴上耳机。播放轻音乐。闭上眼睛。调整姿势。伸展手臂。设置睡眠定时。取下耳机。"
  },
  {
    "time": "23:00-23:59",
    "location": "卧室2",
    "activity": "睡眠",
    "desc": "闭眼。入眠。身体保持安静。"
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
  "Priya Nair的个人电器": {
    "appliances": [
      {
        "unique_id": "priya_nair_手机",
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
        "unique_id": "priya_nair_电脑",
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
      },
      {
        "unique_id": "priya_nair_台灯",
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
  "member": "Priya Nair",
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
  "member": "Priya Nair",
  "appliance_decisions": [
{
      "time": "00:00-07:30",
      "location": "卧室2",
      "activity": "睡眠",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "idle"},
{"unique_id": "卧室2_台灯", "action": "idle"},
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    },
{
      "time": "07:30-07:40",
      "location": "卧室2",
      "activity": "起床、整理床铺、穿衣",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "use"},
{"unique_id": "卧室2_台灯", "action": "idle"},
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    },
{
      "time": "07:40-07:50",
      "location": "卧室2",
      "activity": "收拾房间、整理个人物品",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "use"},
{"unique_id": "卧室2_台灯", "action": "idle"},
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    },
{
      "time": "07:50-08:10",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"}
      ]
    },
{
      "time": "08:10-08:55",
      "location": "厨房",
      "activity": "与Arjun一起准备早餐（布置餐桌、热牛奶等）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "08:55-09:15",
      "location": "厨房",
      "activity": "与Mei-Ling和Arjun一起吃早餐，并服药",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "09:15-09:40",
      "location": "外出",
      "activity": "与Mei-Ling和Arjun一起步行去莫纳什大学",
      "operations": [
{"unique_id": "priya_nair_手机", "action": "use"},
{"unique_id": "priya_nair_电脑", "action": "idle"}
      ]
    },
{
      "time": "09:40-12:00",
      "location": "外出",
      "activity": "在莫纳什大学上课",
      "operations": [
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "idle"}
      ]
    },
{
      "time": "12:00-13:00",
      "location": "外出",
      "activity": "在学校餐厅与Mei-Ling一起吃午餐",
      "operations": [
{"unique_id": "priya_nair_手机", "action": "use"},
{"unique_id": "priya_nair_电脑", "action": "idle"}
      ]
    },
{
      "time": "13:00-15:00",
      "location": "外出",
      "activity": "在莫纳什大学上课/学习",
      "operations": [
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "use"}
      ]
    },
{
      "time": "15:00-17:00",
      "location": "外出",
      "activity": "在莫纳什大学图书馆自习（与Mei-Ling一起）",
      "operations": [
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "use"}
      ]
    },
{
      "time": "17:00-17:30",
      "location": "外出",
      "activity": "与Mei-Ling一起步行回家",
      "operations": [
{"unique_id": "priya_nair_手机", "action": "use"},
{"unique_id": "priya_nair_电脑", "action": "idle"}
      ]
    },
{
      "time": "17:30-18:30",
      "location": "卧室2",
      "activity": "休息、听音乐",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "use"},
{"unique_id": "卧室2_台灯", "action": "idle"},
{"unique_id": "priya_nair_手机", "action": "use"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    },
{
      "time": "18:30-20:00",
      "location": "厨房",
      "activity": "与Mei-Ling一起准备并享用晚餐（Arjun 19:30加入）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_电饭煲", "action": "use"}
      ]
    },
{
      "time": "20:00-20:15",
      "location": "厨房",
      "activity": "与Mei-Ling和Arjun一起洗碗、清洁厨房",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "20:15-21:15",
      "location": "卧室2",
      "activity": "阅读、学习",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "use"},
{"unique_id": "卧室2_台灯", "action": "idle"},
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "use"}
      ]
    },
{
      "time": "21:15-21:45",
      "location": "客厅",
      "activity": "与Mei-Ling和Arjun一起泡茶、品尝茶",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "客厅_空调", "action": "idle"}
      ]
    },
{
      "time": "21:45-22:15",
      "location": "卫生间",
      "activity": "洗漱、洗澡",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "use"},
{"unique_id": "卫生间_洗衣机", "action": "idle"}
      ]
    },
{
      "time": "22:15-22:30",
      "location": "卧室2",
      "activity": "冥想、祷告",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "idle"},
{"unique_id": "卧室2_台灯", "action": "use"},
{"unique_id": "priya_nair_手机", "action": "idle"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    },
{
      "time": "22:30-23:00",
      "location": "卧室2",
      "activity": "睡前放松（听轻音乐）",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "idle"},
{"unique_id": "卧室2_台灯", "action": "use"},
{"unique_id": "priya_nair_手机", "action": "use"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    },
{
      "time": "23:00-23:59",
      "location": "卧室2",
      "activity": "睡眠",
      "operations": [
{"unique_id": "卧室2_空调", "action": "idle"},
{"unique_id": "卧室2_灯", "action": "idle"},
{"unique_id": "卧室2_台灯", "action": "idle"},
{"unique_id": "priya_nair_手机", "action": "charge_home"},
{"unique_id": "priya_nair_电脑", "action": "idle"},
{"unique_id": "priya_nair_台灯", "action": "idle"}
      ]
    }
  ]
}
```
