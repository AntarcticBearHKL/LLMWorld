Token使用: prompt_cache_miss=56454, prompt_cache_hit=7936, completion=144632

# 04_第四层_批量用电决策_Wei Chen

生成时间: 2026-08-14 15:34:03

---

## 提示词

```
你是一个家庭用电行为专家。请为Wei Chen的一天生成完整的用电决策。

成员信息：
- 姓名：Wei Chen
- 年龄：25
- 职业：国际学生/兼职研究助理
- 习惯：{
  "wake_time": "08:00",
  "sleep_time": "00:00",
  "exercise": "每周骑车通勤",
  "hobbies": [
    "听音乐",
    "淘二手货",
    "研究科技"
  ]
}

该成员的完整时间线：
[
  {
    "time": "00:00-07:00",
    "location": "卧室3",
    "activity": "睡眠",
    "desc": "躺在床上。闭上眼睛。入睡。睡眠中偶尔翻身。持续睡眠。"
  },
  {
    "time": "07:00-07:15",
    "location": "卧室3",
    "activity": "起床、整理床铺、换衣",
    "desc": "坐起身。掀开被子。下床。站在床边。拉直床单。铺平被子。摆放枕头。脱下睡衣。拿起T恤。穿上T恤。拿起裤子。穿上裤子。"
  },
  {
    "time": "07:15-07:30",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "走进卫生间。打开灯。拿起牙刷。挤上牙膏。刷牙。漱口。放下牙刷。打开水龙头。捧水洗脸。用毛巾擦干。关闭水龙头。关灯。走出卫生间。"
  },
  {
    "time": "07:30-07:50",
    "location": "厨房",
    "activity": "准备早餐（煮燕麦、切水果），为与Arjun、Priya共进早餐做准备",
    "desc": "走进厨房。打开橱柜。取出燕麦。拿出锅。将燕麦倒入锅。加水。放在电磁炉上。打开电磁炉。从冰箱取出水果。清洗水果。切水果。装盘。"
  },
  {
    "time": "07:50-08:10",
    "location": "厨房",
    "activity": "品尝自制的咖啡，继续准备早餐（Priya在卫生间）",
    "desc": "提起咖啡壶。往杯里倒咖啡。端起杯子。喝了一口。放下杯子。打开冰箱。拿出牛奶。将牛奶倒入小锅。放在炉子上加热。搅拌牛奶。关闭火。将牛奶倒入奶壶。"
  },
  {
    "time": "08:10-08:20",
    "location": "厨房",
    "activity": "与Priya一起准备早餐",
    "desc": "与Priya一同站在厨房。拿起碗碟。放到餐桌上。摆放筷子。递上酱料。与Priya交谈。"
  },
  {
    "time": "08:20-08:55",
    "location": "厨房",
    "activity": "与Arjun和Priya一起准备早餐（布置餐桌、热牛奶等）",
    "desc": "与Arjun和Priya合作。铺桌布。摆餐盘。放刀叉。从厨房端出燕麦。摆上水果。倒牛奶。加热牛奶。将奶壶放桌。摆好椅子。"
  },
  {
    "time": "08:55-09:15",
    "location": "厨房",
    "activity": "与Mei-Ling、Arjun、Priya一起吃早餐",
    "desc": "坐在餐桌前。拿起筷子。夹取燕麦。放入口中。咀嚼。吞咽。夹食水果。喝牛奶。与Mei-Ling交谈。与Arjun交谈。与Priya交谈。"
  },
  {
    "time": "09:15-09:40",
    "location": "外出",
    "activity": "与Mei-Ling、Arjun、Priya步行去莫纳什大学",
    "desc": "从椅子上起身。穿上外套。背起背包。走出宿舍门。与同伴一起步行。沿人行道行走。通过马路。到达莫纳什大学。"
  },
  {
    "time": "09:40-12:00",
    "location": "外出",
    "activity": "在实验室做研究工作",
    "desc": "走进实验室。放下背包。坐到实验台前。打开电脑。输入密码。查看屏幕。翻阅数据。在笔记本上记录。起身取试剂。滴加试剂。观察反应。回到座位。"
  },
  {
    "time": "12:00-13:00",
    "location": "外出",
    "activity": "在学校餐厅与Mei-Ling、Priya一起吃午餐",
    "desc": "离开实验室。走到学校餐厅。在柜台排队。拿起餐盘。选择菜品。端到餐桌。坐下。用叉子吃饭。喝饮料。与Mei-Ling和Priya交谈。"
  },
  {
    "time": "13:00-16:30",
    "location": "外出",
    "activity": "在实验室继续工作学习",
    "desc": "返回实验室。坐下。打开电脑。查看文档。阅读论文。做笔记。运行软件。分析数据。点击鼠标。滚动页面。记录结果。整理文件。"
  },
  {
    "time": "16:30-17:00",
    "location": "外出",
    "activity": "骑自行车回家",
    "desc": "离开实验室。走向自行车棚。掏出钥匙。解开自行车锁。骑上车。蹬踏踏板。骑行至宿舍楼下。停下。下车。锁好自行车。"
  },
  {
    "time": "17:00-17:30",
    "location": "厨房",
    "activity": "准备晚餐（洗菜、切菜）",
    "desc": "走进厨房。打开水龙头。洗手。关水。从冰箱取出蔬菜。将蔬菜放入水槽。打开水龙头。洗蔬菜。关水。将蔬菜放上砧板。拿起菜刀。切菜。"
  },
  {
    "time": "17:30-18:30",
    "location": "厨房",
    "activity": "独自继续准备晚餐（Mei-Ling和Priya在休息）",
    "desc": "继续切菜。打开电磁炉。放上炒锅。倒入油。将切好的菜倒入锅中。用锅铲翻炒。加入盐、酱油。炒熟。关火。盛入盘中。淘米。放入电饭煲。按下煮饭开关。"
  },
  {
    "time": "18:30-20:00",
    "location": "厨房",
    "activity": "与Mei-Ling、Priya一起准备并享用晚餐（Arjun 19:30加入）",
    "desc": "端起菜盘。走到餐桌。放下菜盘。摆放饭碗和筷子。拉开椅子。坐下。拿起筷子。夹菜。放入口中。咀嚼。咽下。与Mei-Ling交谈。与Priya交谈。Arjun回来后打招呼。继续用餐。"
  },
  {
    "time": "20:00-20:15",
    "location": "厨房",
    "activity": "与Mei-Ling、Arjun、Priya一起洗碗、清洁厨房",
    "desc": "起身。收拾餐桌上的碗筷。将碗碟端到水槽。打开水龙头。挤洗洁精。用海绵擦洗碗筷。冲洗干净。擦干碗碟。放回柜子。用抹布擦桌子。清扫地面。"
  },
  {
    "time": "20:15-20:45",
    "location": "卫生间",
    "activity": "洗澡",
    "desc": "走进卫生间。脱下衣服。打开淋浴器。调节水温。站在花洒下。淋湿身体。将沐浴露涂在身体上。用手搓洗。冲洗干净。关闭淋浴。拿起毛巾。擦干身体。穿上睡衣。"
  },
  {
    "time": "20:45-21:15",
    "location": "卧室3",
    "activity": "听音乐放松",
    "desc": "回到卧室3。拿起手机。打开音乐应用。选择歌曲。播放音乐。插入耳机。戴上耳机。坐在床边。躺下。闭着眼睛。"
  },
  {
    "time": "21:15-21:45",
    "location": "客厅",
    "activity": "与Mei-Ling、Arjun、Priya一起泡茶、品尝茶",
    "desc": "从卧室走到客厅。坐在沙发上。拿起茶壶。放入茶叶。倒入热水。盖上壶盖。等待片刻。拿起茶杯。倒茶。端起茶杯。喝一口。与其他人交谈。"
  },
  {
    "time": "21:45-22:15",
    "location": "卧室3",
    "activity": "阅读书籍",
    "desc": "回到卧室3。从书架上拿起一本书。坐在床上。翻开书页。阅读。翻页。继续阅读。"
  },
  {
    "time": "22:15-23:00",
    "location": "卧室3",
    "activity": "用电脑做研究或学习",
    "desc": "坐在书桌前。打开电脑。启动程序。点击文件。输入文字。查看资料。做笔记。保存文件。打开网页。搜索信息。记录要点。关闭程序。"
  },
  {
    "time": "23:00-23:15",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "走进卫生间。拿起牙刷。挤牙膏。刷牙。漱口。放下牙刷。打开水龙头。双手接水洗脸。用毛巾擦干。关闭水龙头。"
  },
  {
    "time": "23:15-23:30",
    "location": "卧室3",
    "activity": "换睡衣、睡前准备",
    "desc": "回到卧室3。脱下衣服。穿上睡衣。铺平床单。展开被子。摆好枕头。"
  },
  {
    "time": "23:30-24:00",
    "location": "卧室3",
    "activity": "躺在床上用手机浏览网页，逐渐入睡",
    "desc": "躺在床上。拿起手机。打开浏览器。点击网页。滑动屏幕。浏览内容。放下手机。闭上眼睛。调整睡姿。入睡。"
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
  "Wei Chen的个人电器": {
    "appliances": [
      {
        "unique_id": "wei_chen_手机",
        "name": "手机",
        "type": "charging",
        "power_watts": 20,
        "brand": "OnePlus",
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
        "unique_id": "wei_chen_电脑",
        "name": "电脑",
        "type": "on_demand",
        "power_watts": 200,
        "brand": "Asus",
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
        "unique_id": "wei_chen_台灯",
        "name": "台灯",
        "type": "on_demand",
        "power_watts": 15,
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
  "member": "Wei Chen",
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
  "member": "Wei Chen",
  "appliance_decisions": [
{
      "time": "00:00-07:00",
      "location": "卧室3",
      "activity": "睡眠",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "idle"},
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "07:00-07:15",
      "location": "卧室3",
      "activity": "起床、整理床铺、换衣",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "use"},
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "07:15-07:30",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"}
      ]
    },
{
      "time": "07:30-07:50",
      "location": "厨房",
      "activity": "准备早餐（煮燕麦、切水果），为与Arjun、Priya共进早餐做准备",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "07:50-08:10",
      "location": "厨房",
      "activity": "品尝自制的咖啡，继续准备早餐（Priya在卫生间）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "08:10-08:20",
      "location": "厨房",
      "activity": "与Priya一起准备早餐",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "08:20-08:55",
      "location": "厨房",
      "activity": "与Arjun和Priya一起准备早餐（布置餐桌、热牛奶等）",
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
      "activity": "与Mei-Ling、Arjun、Priya一起吃早餐",
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
      "activity": "与Mei-Ling、Arjun、Priya步行去莫纳什大学",
      "operations": [
{"unique_id": "wei_chen_手机", "action": "use"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "09:40-12:00",
      "location": "外出",
      "activity": "在实验室做研究工作",
      "operations": [
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "12:00-13:00",
      "location": "外出",
      "activity": "在学校餐厅与Mei-Ling、Priya一起吃午餐",
      "operations": [
{"unique_id": "wei_chen_手机", "action": "use"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "13:00-16:30",
      "location": "外出",
      "activity": "在实验室继续工作学习",
      "operations": [
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "16:30-17:00",
      "location": "外出",
      "activity": "骑自行车回家",
      "operations": [
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "17:00-17:30",
      "location": "厨房",
      "activity": "准备晚餐（洗菜、切菜）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "17:30-18:30",
      "location": "厨房",
      "activity": "独自继续准备晚餐（Mei-Ling和Priya在休息）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_电饭煲", "action": "use"}
      ]
    },
{
      "time": "18:30-20:00",
      "location": "厨房",
      "activity": "与Mei-Ling、Priya一起准备并享用晚餐（Arjun 19:30加入）",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "20:00-20:15",
      "location": "厨房",
      "activity": "与Mei-Ling、Arjun、Priya一起洗碗、清洁厨房",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"}
      ]
    },
{
      "time": "20:15-20:45",
      "location": "卫生间",
      "activity": "洗澡",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "use"},
{"unique_id": "卫生间_洗衣机", "action": "idle"}
      ]
    },
{
      "time": "20:45-21:15",
      "location": "卧室3",
      "activity": "听音乐放松",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "use"},
{"unique_id": "wei_chen_手机", "action": "use"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    },
{
      "time": "21:15-21:45",
      "location": "客厅",
      "activity": "与Mei-Ling、Arjun、Priya一起泡茶、品尝茶",
      "operations": [
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "客厅_空调", "action": "idle"}
      ]
    },
{
      "time": "21:45-22:15",
      "location": "卧室3",
      "activity": "阅读书籍",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "idle"},
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "use"}
      ]
    },
{
      "time": "22:15-23:00",
      "location": "卧室3",
      "activity": "用电脑做研究或学习",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "idle"},
{"unique_id": "wei_chen_手机", "action": "charge_home"},
{"unique_id": "wei_chen_电脑", "action": "use"},
{"unique_id": "wei_chen_台灯", "action": "use"}
      ]
    },
{
      "time": "23:00-23:15",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"}
      ]
    },
{
      "time": "23:15-23:30",
      "location": "卧室3",
      "activity": "换睡衣、睡前准备",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "idle"},
{"unique_id": "wei_chen_手机", "action": "idle"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "use"}
      ]
    },
{
      "time": "23:30-24:00",
      "location": "卧室3",
      "activity": "躺在床上用手机浏览网页，逐渐入睡",
      "operations": [
{"unique_id": "卧室3_空调", "action": "idle"},
{"unique_id": "卧室3_灯", "action": "idle"},
{"unique_id": "wei_chen_手机", "action": "use"},
{"unique_id": "wei_chen_电脑", "action": "idle"},
{"unique_id": "wei_chen_台灯", "action": "idle"}
      ]
    }
  ]
}
```
