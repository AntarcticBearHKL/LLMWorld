Token使用: prompt_cache_miss=56454, prompt_cache_hit=7936, completion=144632

# 04_第四层_批量用电决策_Mei-Ling Zhang

生成时间: 2026-08-14 15:34:03

---

## 提示词

```
你是一个家庭用电行为专家。请为Mei-Ling Zhang的一天生成完整的用电决策。

成员信息：
- 姓名：Mei-Ling Zhang
- 年龄：22
- 职业：国际学生（莫纳什大学）
- 习惯：{
  "wake_time": "08:30",
  "sleep_time": "23:30",
  "exercise": "每周散步或瑜伽",
  "hobbies": [
    "阅读",
    "茶道",
    "写作"
  ]
}

该成员的完整时间线：
[
  {
    "time": "00:00-08:30",
    "location": "卧室1",
    "activity": "睡眠",
    "desc": "躺在床上。闭眼。双臂自然放在身体两侧。双腿伸直。偶尔翻身。清晨醒来。睁开眼睛。伸手拿起放在床头柜上的手机。看了一眼时间。放下手机。坐起身。掀开被子。双腿移到床边。下床。穿上拖鞋。"
  },
  {
    "time": "08:30-08:45",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "走进卫生间。打开灯。走到洗手台前。拧开水龙头。伸出双手用手接水。将水拍在脸上。在手掌上挤洗面奶。双手揉搓起泡。涂抹在脸上。打圈揉搓。用清水冲净。关闭水龙头。拿起牙刷。在牙刷上挤牙膏。打开水龙头。将牙刷放入口中。上下刷牙。吐泡沫。漱口。重复三次。关闭水龙头。拿起毛巾擦脸。擦干。将毛巾挂回。关灯。走出卫生间。"
  },
  {
    "time": "08:45-08:55",
    "location": "卧室1",
    "activity": "换衣、整理仪容",
    "desc": "走进卧室。打开衣柜。拿出上衣和裤子。放在床上。脱下睡衣。穿上内衣。穿上上衣。穿上裤子。站在穿衣镜前。用手梳理头发。整理衣领。拽平衣服。拿起桌上的润肤霜。拧开盖子。在手上挤出润肤霜。涂抹在脸上。拍打均匀。盖上盖子。放下。背起书包。走出卧室。"
  },
  {
    "time": "08:55-09:15",
    "location": "厨房",
    "activity": "准备并享用早餐",
    "desc": "走进厨房。打开冰箱。拿出牛奶和鸡蛋。关上冰箱门。走到灶台前。将牛奶倒入杯子。放入微波炉加热。从橱柜拿出碗和筷子。打鸡蛋到碗里。用筷子搅拌。打开电磁炉。在平底锅上倒油。等油热。倒入鸡蛋液。用铲子翻炒。关火。将炒蛋盛到盘子里。拿出面包片。放入面包机烤。面包弹出。取出面包。放在盘子里。坐到餐桌前。拿起筷子。夹鸡蛋。吃面包。喝牛奶。与身旁的人交谈。"
  },
  {
    "time": "09:15-09:40",
    "location": "外出",
    "activity": "步行去莫纳什大学",
    "desc": "走到门口。换上运动鞋。穿上外套。拿起雨伞。打开门。走出家门。与其他人一起。沿人行道行走。穿过十字路口。看到绿灯亮起。快步走过斑马线。继续行走。到达莫纳什大学校门。走进校园。"
  },
  {
    "time": "09:40-12:00",
    "location": "外出",
    "activity": "在莫纳什大学上课/学习",
    "desc": "走进教学楼。找到教室。推开门。走进去。找到空座位。放下书包。坐在椅子上。从书包拿出笔记本。翻开笔记。拿出笔。听老师讲课。低头在笔记本上写字。抬头看黑板。偶尔用手机拍照。休息时间。打开水杯喝水。合上笔记本。收拾笔。将笔记本放入书包。背起书包。走出教室。"
  },
  {
    "time": "12:00-13:00",
    "location": "外出",
    "activity": "在校园餐厅用午餐",
    "desc": "和同学一起走到学校餐厅。在门口拿托盘。排队。站在点餐台前。看菜单。指向一种食物。在收银台付钱。端着托盘走到餐桌前。放下托盘。坐在椅子上。拿起筷子。夹菜。吃一口。喝汤。与对面的同学交谈。低头继续吃。吃完了。用餐巾纸擦嘴。将托盘端到回收处。倒掉残渣。放下托盘。走出餐厅。"
  },
  {
    "time": "13:00-15:00",
    "location": "外出",
    "activity": "在莫纳什大学上课/学习",
    "desc": "走进实验楼或教学楼。找到教室。坐下。从书包拿出电脑。打开电脑。在键盘上打字。听讲。做笔记。看到老师在黑板上写字。抄写。和旁边同学讨论问题。翻阅课本。继续听课。收拾电脑。合上电脑。放进包。起身离开。"
  },
  {
    "time": "15:00-17:00",
    "location": "外出",
    "activity": "在图书馆自习",
    "desc": "走进图书馆。找到空座位。坐下。从书包拿出笔记本电脑。打开电脑。翻开专业书籍。在笔记本上做笔记。在电脑上编辑文档。思考时手支下巴。偶尔喝水。起身去洗手间。回来继续学习。整理笔记。保存文档。收起电脑。放入书包。"
  },
  {
    "time": "17:00-17:30",
    "location": "外出",
    "activity": "步行回家",
    "desc": "拿起书包。起身离开座位。走出图书馆。在门口与朋友会合。一起走出校门。沿来时路返回。穿过马路。经过商店。走到公寓楼下。按下电梯按钮。走进电梯。按楼层。走出电梯。走到家门前。拿出钥匙。打开门。走进屋内。"
  },
  {
    "time": "17:30-18:30",
    "location": "卧室1",
    "activity": "休息、浏览手机",
    "desc": "走进卧室。放下书包。脱下外套。挂在衣架上。走到床边。坐在床上。躺下。从口袋里拿出手机。解锁屏幕。手指滑动屏幕。点开社交应用。浏览页面。打开视频。观看。切换应用。查看消息。拿起水杯喝水。放下手机。坐起来。"
  },
  {
    "time": "18:30-20:00",
    "location": "厨房",
    "activity": "准备并享用晚餐",
    "desc": "走进厨房。穿上围裙。打开水龙头洗手。关水。用毛巾擦手。打开冰箱。取出蔬菜和肉。放在水槽里。将蔬菜放入水盆。加水。用手揉洗。捞出沥干。放在砧板上。拿起刀。切菜。将切好的菜放入盘子。打开电磁炉。在锅里倒油。放入肉片翻炒。变色后加入蔬菜。继续翻炒。加盐和酱油。炒熟后盛出。在电饭锅盛饭。将菜端到餐桌。摆好碗筷。坐在餐桌前。拿起筷子。夹菜吃饭。喝一口汤。和家人交谈。吃完。放下碗筷。"
  },
  {
    "time": "20:00-20:15",
    "location": "厨房",
    "activity": "洗碗、清洁厨房",
    "desc": "站起来。收拾碗筷。将碗碟拿到厨房水槽。打开水龙头。倒洗洁精。拿海绵。洗刷碗碟。冲洗干净。放入沥水架。用抹布擦餐桌。擦灶台。倒掉水槽里的垃圾。擦干手。"
  },
  {
    "time": "20:15-21:15",
    "location": "卧室1",
    "activity": "阅读（台灯下阅读书籍）",
    "desc": "走进卧室。打开台灯。走到书桌前。从书架上抽出书籍。坐回床上。翻开书。阅读。用手指指着文字。翻页。偶尔拿起笔在书上画线。看了半小时后。合上书。放在床头柜。继续拿起另一本书。翻开阅读。过了一会儿。放下书。"
  },
  {
    "time": "21:15-21:45",
    "location": "客厅",
    "activity": "泡茶、品尝茶",
    "desc": "走出卧室。走到客厅。拿起电热水壶。去厨房接水。放回底座。按下开关。等待水烧开。从储物柜拿出茶叶。打开罐子。舀一勺茶叶放入茶杯。水开后。举起水壶。将水冲入茶杯。盖上杯盖。等待片刻。端起茶杯。吹气。小口啜饮。放下杯子。和周围人说话。"
  },
  {
    "time": "21:45-22:45",
    "location": "卧室1",
    "activity": "写作（用电脑或纸笔）",
    "desc": "回到卧室。坐在书桌前。打开电脑。打开文档。双手放在键盘上。打字。停顿。看屏幕。修改文字。移动鼠标。用笔在纸上写草稿。站起来伸展双臂。坐下继续打字。最后保存文档。关闭电脑。合上电脑。"
  },
  {
    "time": "22:45-23:00",
    "location": "卫生间",
    "activity": "洗漱（刷牙、洗脸）",
    "desc": "走进卫生间。开灯。站在洗手台前。拿起牙刷。挤牙膏。刷牙。漱口。用毛巾擦嘴。拧开水龙头洗脸。擦干。关灯。走出卫生间。"
  },
  {
    "time": "23:00-23:30",
    "location": "卧室1",
    "activity": "睡前阅读或看手机",
    "desc": "走到床边。掀开被子。躺到床上。拿起手机。解锁。浏览新闻。切换应用。看视频。放下手机。拿起书。看了几页。放下书。关灯。躺下。"
  },
  {
    "time": "23:30-23:59",
    "location": "卧室1",
    "activity": "睡眠",
    "desc": "闭上眼睛。躺在床上。身体不再移动。呼吸放缓。翻身一次。静止。入睡。"
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
  "Mei-Ling Zhang的个人电器": {
    "appliances": [
      {
        "unique_id": "mei_ling_zhang_手机",
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
        "unique_id": "mei_ling_zhang_电脑",
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
      },
      {
        "unique_id": "mei_ling_zhang_台灯",
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
      "time": "00:00-08:30",
      "location": "卧室1",
      "activity": "睡眠",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "charge_home"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"},
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"}
      ]
    },
{
      "time": "08:30-08:45",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "08:45-08:55",
      "location": "卧室1",
      "activity": "换衣、整理仪容",
      "operations": [
{"unique_id": "卧室1_灯", "action": "use"},
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "08:55-09:15",
      "location": "厨房",
      "activity": "准备并享用早餐",
      "operations": [
{"unique_id": "厨房_微波炉", "action": "use"},
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "09:15-09:40",
      "location": "外出",
      "activity": "步行去莫纳什大学",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "09:40-12:00",
      "location": "外出",
      "activity": "在莫纳什大学上课/学习",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "12:00-13:00",
      "location": "外出",
      "activity": "在校园餐厅用午餐",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "13:00-15:00",
      "location": "外出",
      "activity": "在莫纳什大学上课/学习",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "use"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "15:00-17:00",
      "location": "外出",
      "activity": "在图书馆自习",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "use"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "17:00-17:30",
      "location": "外出",
      "activity": "步行回家",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "17:30-18:30",
      "location": "卧室1",
      "activity": "休息、浏览手机",
      "operations": [
{"unique_id": "卧室1_灯", "action": "use"},
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "18:30-20:00",
      "location": "厨房",
      "activity": "准备并享用晚餐",
      "operations": [
{"unique_id": "厨房_电磁炉", "action": "use"},
{"unique_id": "厨房_油烟机", "action": "use"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "20:00-20:15",
      "location": "厨房",
      "activity": "洗碗、清洁厨房",
      "operations": [
{"unique_id": "厨房_电磁炉", "action": "idle"},
{"unique_id": "厨房_油烟机", "action": "idle"},
{"unique_id": "厨房_电饭煲", "action": "idle"},
{"unique_id": "厨房_微波炉", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "20:15-21:15",
      "location": "卧室1",
      "activity": "阅读（台灯下阅读书籍）",
      "operations": [
{"unique_id": "卧室1_灯", "action": "use"},
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "use"}
      ]
    },
{
      "time": "21:15-21:45",
      "location": "客厅",
      "activity": "泡茶、品尝茶",
      "operations": [
{"unique_id": "客厅_灯", "action": "use"},
{"unique_id": "客厅_电视", "action": "idle"},
{"unique_id": "客厅_空调", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "21:45-22:45",
      "location": "卧室1",
      "activity": "写作（用电脑或纸笔）",
      "operations": [
{"unique_id": "卧室1_灯", "action": "use"},
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "use"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "use"}
      ]
    },
{
      "time": "22:45-23:00",
      "location": "卫生间",
      "activity": "洗漱（刷牙、洗脸）",
      "operations": [
{"unique_id": "卫生间_热水器", "action": "idle"},
{"unique_id": "卫生间_洗衣机", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "idle"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"}
      ]
    },
{
      "time": "23:00-23:30",
      "location": "卧室1",
      "activity": "睡前阅读或看手机",
      "operations": [
{"unique_id": "卧室1_灯", "action": "idle"},
{"unique_id": "卧室1_空调", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "mei_ling_zhang_手机", "action": "use"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "use"}
      ]
    },
{
      "time": "23:30-23:59",
      "location": "卧室1",
      "activity": "睡眠",
      "operations": [
{"unique_id": "mei_ling_zhang_手机", "action": "charge_home"},
{"unique_id": "mei_ling_zhang_电脑", "action": "idle"},
{"unique_id": "mei_ling_zhang_台灯", "action": "idle"},
{"unique_id": "卧室1_灯", "action": "idle"},
{"unique_id": "卧室1_台灯", "action": "idle"},
{"unique_id": "卧室1_空调", "action": "idle"}
      ]
    }
  ]
}
```
