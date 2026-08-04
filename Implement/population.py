"""人口构建器：本地确定性生成 Clayton 3168 的异质家庭人口（0 LLM 调用）。

设计依据（Clayton 3168 census 统计，来自 clayton_3168_*.csv）：
- 总人口约 2.2 万，中位年龄 28（年轻社区）→ 家庭构成以年轻夫妇/有孩家庭为主
- 住宅约 7150 套，中位月供 2000 澳元 → 中等居住成本社区
- 典型家庭类型（参考 census 家庭构成）：年轻夫妇/丁克、有孩家庭、独居、合租

所有随机都由 seed 控制 → 同种子两次生成结果完全一致（论文可复现要求）。
"""

import json
import os
import random
from datetime import datetime

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "墨尔本"
CLAYTON_DISTRICT = "Clayton"


# ---------- 姓名池（与 census 社区构成相符）----------

FIRST_NAMES_M = ["David", "Jack", "Lucas", "Ethan", "James", "Daniel", "Ryan", "Ben"]
FIRST_NAMES_F = ["Alice", "Sophia", "Emma", "Olivia", "Chloe", "Grace", "Mia", "Lily"]
SURNAMES = ["Chen", "Wang", "Li", "Zhang", "Smith", "Nguyen", "Patel", "Brown"]

OCCUPATIONS = [
    "软件工程师", "数据分析师", "护士", "教师", "会计", "销售经理",
    "建筑工人", "厨师", "研究生", "超市收银员", "电工", "律师助理",
]

# ---------- 家庭模板（参照 census 家庭构成，结构对齐 household.json）----------

def _base_home(name, size, room_appliances):
    """room_appliances: {房间名: [电器类型列表]} → 标准 home 结构。"""
    rooms = []
    for room_name, appliance_types in room_appliances.items():
        rooms.append({
            "name": room_name,
            "size": 0,
            "appliances": [{"type": t, "brand": "Generic", "power": None, "age": 0}
                           for t in appliance_types],
        })
    return {"name": name, "type": "联排别墅", "size": size, "rooms": rooms}


def _standard_rooms(with_ev=False):
    """Clayton 典型联排的房间与电器配置（参考 worlds/495 的户型）。"""
    rooms = {
        "客厅": ["电视", "空调", "灯"],
        "厨房": ["冰箱", "电饭煲", "微波炉", "电磁炉", "油烟机", "灯"],
        "主卧": ["空调", "灯", "台灯"],
        "次卧/书房": ["空调", "灯", "台灯"],
        "卫生间": ["热水器", "洗衣机", "灯"],
        "阳台": ["灯"],
    }
    if with_ev:
        rooms["车库"] = ["电动汽车"]
    return rooms


def _member(name, age, gender, occupation, traits, energy_awareness, habits, personal):
    return {
        "name": name, "age": age, "gender": gender, "occupation": occupation,
        "work_schedule": {"start": "09:00", "end": "17:00", "remote": False,
                          "work_days": [1, 2, 3, 4, 5]},
        "personality": {"traits": traits, "energy_awareness": energy_awareness},
        "habits": habits,
        "health": {"condition": "良好",
                   "temperature_preference": {"summer": 26, "winter": 22}},
        "personal_appliances": [{"type": t, "brand": "Generic", "power": None, "age": 0}
                                for t in personal],
    }


def _build_template(household_type, rng):
    """按家庭类型生成一个完整 household.json 结构（含随机变化，由 seed 控制）。"""
    surname = rng.choice(SURNAMES)
    size = rng.choice([90, 100, 110, 120])

    if household_type == "young_couple":
        return {
            "type": "年轻夫妇/丁克家庭",
            "season": "春天",
            "home": _base_home("Clayton温馨联排", size, _standard_rooms(with_ev=rng.random() < 0.25)),
            "members": [
                _member(f"{rng.choice(FIRST_NAMES_F)} {surname}", rng.randint(26, 32), "女",
                        rng.choice(OCCUPATIONS), ["细心", "喜欢烹饪"],
                        rng.choice(["高", "中", "高"]),
                        {"wake_time": "07:00", "sleep_time": "23:00", "exercise": "每周跑步三次",
                         "hobbies": ["烹饪", "阅读"]},
                        ["手机", "电脑", "台灯"]),
                _member(f"{rng.choice(FIRST_NAMES_M)} {surname}", rng.randint(27, 34), "男",
                        rng.choice(OCCUPATIONS), ["理性", "爱运动"],
                        rng.choice(["中", "中", "低"]),
                        {"wake_time": "08:00", "sleep_time": "00:00", "exercise": "每周去健身房两次",
                         "hobbies": ["游戏", "摄影"]},
                        ["手机", "电脑"]),
            ],
        }

    if household_type == "family_with_kids":
        return {
            "type": "有孩家庭",
            "season": "春天",
            "home": _base_home("Clayton家庭住宅", size + 30,
                               {**_standard_rooms(with_ev=True), "儿童房": ["灯", "台灯"]}),
            "members": [
                _member(f"{rng.choice(FIRST_NAMES_F)} {surname}", rng.randint(33, 40), "女",
                        rng.choice(OCCUPATIONS), ["有条理", "重视家庭"],
                        rng.choice(["高", "中", "高"]),
                        {"wake_time": "06:30", "sleep_time": "22:30", "exercise": "周末散步",
                         "hobbies": ["烘焙", "园艺"]},
                        ["手机", "电脑"]),
                _member(f"{rng.choice(FIRST_NAMES_M)} {surname}", rng.randint(35, 45), "男",
                        rng.choice(OCCUPATIONS), ["稳重", "顾家"],
                        rng.choice(["中", "中", "低"]),
                        {"wake_time": "06:45", "sleep_time": "22:30", "exercise": "晨跑",
                         "hobbies": ["钓鱼", "修车"]},
                        ["手机", "电脑"]),
                _member(f"{rng.choice(['Liam', 'Noah', 'Emma', 'Olivia', 'Ava'])} {surname}",
                        rng.randint(5, 12), rng.choice(["男", "女"]), "小学生",
                        ["活泼"], "低",
                        {"wake_time": "07:00", "sleep_time": "21:00", "exercise": "课间活动",
                         "hobbies": ["画画", "乐高"]},
                        ["手机"]),
            ],
        }

    if household_type == "single_living":
        return {
            "type": "独居",
            "season": "春天",
            "home": _base_home("Clayton一居室", rng.choice([55, 65, 75]),
                               {"客厅": ["电视", "空调", "灯"], "厨房": ["冰箱", "微波炉", "灯"],
                                "卧室": ["空调", "台灯"], "卫生间": ["热水器", "洗衣机", "灯"]}),
            "members": [
                _member(f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {surname}",
                        rng.randint(22, 30) if rng.random() < 0.7 else rng.randint(60, 75),
                        rng.choice(["男", "女"]), rng.choice(OCCUPATIONS + ["退休", "学生"]),
                        ["安静", "独立"], rng.choice(["低", "中", "中"]),
                        {"wake_time": "07:30", "sleep_time": "23:30", "exercise": "偶尔散步",
                         "hobbies": ["看剧", "打游戏"]},
                        ["手机", "电脑", "台灯"]),
            ],
        }

    # share_house 合租
    return {
        "type": "合租",
        "season": "春天",
        "home": _base_home("Clayton合租公寓", size,
                           {"客厅": ["电视", "灯"], "厨房": ["冰箱", "微波炉", "电磁炉", "灯"],
                            "卧室A": ["空调", "台灯"], "卧室B": ["空调", "台灯"],
                            "卧室C": ["灯", "台灯"], "卫生间": ["热水器", "洗衣机", "灯"]}),
        "members": [
            _member(f"{rng.choice(FIRST_NAMES_M)} {surname}", rng.randint(20, 26), "男",
                    rng.choice(OCCUPATIONS + ["研究生"]), ["开朗", "熬夜"], "低",
                    {"wake_time": "09:00", "sleep_time": "01:00", "exercise": "无",
                     "hobbies": ["游戏"]},
                    ["手机", "电脑"]),
            _member(f"{rng.choice(FIRST_NAMES_F)} {surname}", rng.randint(20, 27), "女",
                    rng.choice(OCCUPATIONS + ["研究生"]), ["文静", "爱干净"], "中",
                    {"wake_time": "08:00", "sleep_time": "23:00", "exercise": "瑜伽",
                     "hobbies": ["读书"]},
                    ["手机", "电脑"]),
            _member(f"{rng.choice(FIRST_NAMES_M)} {surname}", rng.randint(22, 29), "男",
                    rng.choice(OCCUPATIONS), ["随和", "健身"], "中",
                    {"wake_time": "08:30", "sleep_time": "00:30", "exercise": "健身",
                     "hobbies": ["篮球"]},
                    ["手机"]),
        ],
    }


# ---------- 构建入口 ----------

def build_population(world_id, count, seed=42, household_types=None):
    """本地生成 count 户异质家庭，写入 worlds/<world_id>/3168/house_XXXX/。

    返回世界元信息（结构对齐 generate.py 的 world.json）。
    """
    if household_types is None:
        # 默认分布（census 校准：年轻社区 → 夫妇/有孩为主）
        household_types = ["young_couple", "family_with_kids", "single_living", "share_house"]

    rng = random.Random(seed)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_dir = os.path.join(project_root, "worlds", world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    os.makedirs(district_dir, exist_ok=True)

    households_meta = []
    for i in range(count):
        htype = household_types[i % len(household_types)]
        household = _build_template(htype, rng)

        house_id = f"house_{i + 1:04d}"
        house_dir = os.path.join(district_dir, house_id)
        os.makedirs(house_dir, exist_ok=True)

        with open(os.path.join(house_dir, "household.json"), "w", encoding="utf-8") as f:
            json.dump(household, f, ensure_ascii=False, indent=2)

        households_meta.append({
            "house_id": house_id,
            "type": htype,
            "members_count": len(household["members"]),
            "rooms_count": len(household["home"]["rooms"]),
        })
        print(f"  生成 {house_id}：{htype}（{len(household['members'])}人/{len(household['home']['rooms'])}房间）")

    # district 信息（对齐 census）
    district = {
        "postcode": CLAYTON_POSTCODE,
        "location": {"city": CLAYTON_CITY, "district": CLAYTON_DISTRICT,
                     "coordinates": {"lat": -37.916, "lon": 145.123}},
        "economic_level": "中",
    }
    with open(os.path.join(district_dir, "district.json"), "w", encoding="utf-8") as f:
        json.dump(district, f, ensure_ascii=False, indent=2)

    world_meta = {
        "world_id": world_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_prompt": f"本地确定性人口构建（seed={seed}，基于 Clayton 3168 census 校准）",
        "generator": "population.py",
        "district": {
            "postcode": CLAYTON_POSTCODE,
            "city": CLAYTON_CITY,
            "district": CLAYTON_DISTRICT,
            "economic_level": "中",
        },
        "households": households_meta,
    }
    with open(os.path.join(world_dir, "world.json"), "w", encoding="utf-8") as f:
        json.dump(world_meta, f, ensure_ascii=False, indent=2)

    return world_meta


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="本地人口构建（0 LLM 调用）")
    parser.add_argument("world_id", help="新世界ID，如 pop01")
    parser.add_argument("--count", type=int, default=4, help="家庭数量")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    print(f"人口构建：world={args.world_id}，{args.count} 户，种子 {args.seed}")
    build_population(args.world_id, args.count, args.seed)
    print(f"完成：worlds/{args.world_id}/ 已生成")
