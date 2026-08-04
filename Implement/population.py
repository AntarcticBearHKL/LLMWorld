"""人口构建器 v2：Big Five 人格驱动 + 8 类垂直家庭 + 属性关联（census 校准）。

依据（计划22 文献调研）：
- Big Five 人格 → LLM 智能体行为（PsyAgent arXiv:2601.06158；2604.12250）
- 成员间属性关联（2508.09964）：夫妻年龄差 ≤5、孩子年龄=父母-25~35
- 住宅-家庭联合（2605.17031）：年龄→职业→收入→住房→电器 关联链
- fringe 群体显式配额（2501.16080）：独居老人/单亲/学生不缺席
- Clayton 本地化（2112.12071）：Monash 大学区 → 国际学生类型

census 校准锚点（Data/clayton_3168_*.csv）：中位年龄 28、中位月供 2000、住宅 7150。
"""

import json
import os
import random
from datetime import datetime

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "墨尔本"
CLAYTON_DISTRICT = "Clayton"

# ---------- 多文化姓名池（Clayton 真实多元社区）----------

FIRST_NAMES_M = ["David", "Jack", "Lucas", "Ethan", "James", "Daniel", "Ryan", "Ben",
                 "Arjun", "Rohan", "Minh", "Tuan", "Liam", "Noah", "William"]
FIRST_NAMES_F = ["Alice", "Sophia", "Emma", "Olivia", "Chloe", "Grace", "Mia", "Lily",
                 "Priya", "Ananya", "Linh", "Hana", "Ava", "Ella", "Zoe"]
SURNAMES = ["Chen", "Wang", "Li", "Zhang", "Smith", "Nguyen", "Patel", "Brown",
            "Tran", "Singh", "Kumar", "Wilson", "Gao", "Liu", "Taylor", "Pham"]
KID_NAMES = ["Liam", "Noah", "Emma", "Olivia", "Ava", "Mia", "Ethan", "Lucas",
             "Arjun", "Minh", "Hana", "Zoe"]

# ---------- 职业与收入（按年龄段/收入档关联）----------

OCCUPATIONS_PROFESSIONAL = ["软件工程师", "数据分析师", "会计", "律师", "医生", "大学教授",
                            "银行经理", "建筑师", "药剂师"]
OCCUPATIONS_MIDDLE = ["护士", "教师", "销售经理", "电工", "厨师", "机械师",
                      "超市主管", "建筑监理", "司机", "行政助理"]
OCCUPATIONS_SERVICE = ["超市收银员", "清洁工", "服务员", "仓库工人", "快递员", "园林工"]
STUDENT_LEVELS = ["研究生", "博士生", "本科生"]

INCOME_BY_OCCUPATION = {
    "高": OCCUPATIONS_PROFESSIONAL,
    "中": OCCUPATIONS_MIDDLE,
    "低": OCCUPATIONS_SERVICE,
}

# ---------- Big Five 人格模型 ----------

BIG_FIVE_ZH = {
    "openness": "开放性",
    "conscientiousness": "尽责性",
    "extraversion": "外向性",
    "agreeableness": "宜人性",
    "neuroticism": "神经质",
}

BIG_FIVE_TEXT = {
    "openness": {
        "high": "好奇心强、乐于尝试新鲜事物",
        "low": "习惯熟悉的生活方式，不太尝试新鲜事物",
    },
    "conscientiousness": {
        "high": "条理分明、作息规律、做事细致",
        "low": "随性随意，生活节奏松散",
    },
    "extraversion": {
        "high": "喜欢社交聚会，经常外出活动",
        "low": "安静内敛，更多时间待在家里",
    },
    "agreeableness": {
        "high": "重视邻里关系，容易接受他人建议",
        "low": "独立固执，不太受他人影响",
    },
    "neuroticism": {
        "high": "容易焦虑，对价格波动和新闻事件反应敏感",
        "low": "心态稳定，遇事不慌",
    },
}

TRAITS_BY_LEVEL = {
    "openness": {"high": "好奇", "low": "传统"},
    "conscientiousness": {"high": "有条理", "low": "随性"},
    "extraversion": {"high": "开朗", "low": "安静"},
    "agreeableness": {"high": "随和", "low": "固执"},
    "neuroticism": {"high": "敏感", "low": "沉稳"},
}


def sample_big_five(rng, bias=None):
    """采样 Big Five 五维分数（1-10）。bias 可给某维加倾向（如父母尽责性偏高）。"""
    bias = bias or {}
    scores = {}
    for dim in BIG_FIVE_ZH:
        b = bias.get(dim, 0)
        scores[dim] = max(1, min(10, rng.randint(1, 10) + b))
    return scores


def big_five_to_text(bf):
    """五维分数 → 中文行为描述（喂给 LLM prompt）。"""
    parts = []
    for dim, zh in BIG_FIVE_ZH.items():
        v = bf[dim]
        level = "high" if v >= 7 else ("low" if v <= 4 else None)
        if level:
            parts.append(f"{zh}{'高' if level == 'high' else '低'}：{BIG_FIVE_TEXT[dim][level]}")
    return "；".join(parts) if parts else "性格中庸，无明显倾向"


def big_five_to_traits(bf, rng):
    """五维 → 2-3 个中文性格词（兼容 personality.traits 字段）。"""
    traits = []
    for dim in BIG_FIVE_ZH:
        v = bf[dim]
        if v >= 7:
            traits.append(TRAITS_BY_LEVEL[dim]["high"])
        elif v <= 4:
            traits.append(TRAITS_BY_LEVEL[dim]["low"])
    rng.shuffle(traits)
    return traits[:3] if traits else ["随和"]


def big_five_to_news_sensitivity(bf):
    """神经质 → 对新闻/价格事件的敏感度（影响政策响应强度）。"""
    n = bf["neuroticism"]
    if n >= 7:
        return "高"
    if n >= 4:
        return "中"
    return "低"


# 注：energy_awareness（节能意识）字段已按用户 2026-08 指令移除——
# 生成阶段不得预设任何与用电行为直接相关的词条（避免"作弊"），
# 节能行为应完全由 LLM 在模拟中从人格/情境自发涌现。


# ---------- 成员生成 ----------

def _make_member(rng, name, gender, age, occupation, income_bracket,
                 big_five=None, wake=None, sleep=None, personal=None, role="成员"):
    """生成一名成员（Big Five 驱动人格字段；不含任何用电行为预设——去作弊化）。"""
    bf = big_five or sample_big_five(rng)
    traits = big_five_to_traits(bf, rng)

    # 作息习惯：由角色/尽责性/外向性推导 + 随机扰动
    if wake is None:
        if occupation == "退休":
            wake = rng.choice(["06:30", "07:00", "07:30"])
        elif occupation in ("本科生", "研究生", "博士生"):
            wake = rng.choice(["08:30", "09:00", "09:30"])
        else:
            wake = rng.choice(["06:45", "07:00", "07:15", "07:30"])
        if bf["extraversion"] >= 7 and occupation != "退休":
            wake = rng.choice(["06:45", "07:00"])   # 外向早起社交
        elif bf["conscientiousness"] >= 7:
            wake = rng.choice(["06:30", "06:45"])
    if sleep is None:
        sleep = rng.choice(["22:30", "23:00", "23:30", "00:00"])
        if occupation in ("本科生", "研究生", "博士生"):
            sleep = rng.choice(["00:00", "00:30", "01:00"])   # 学生熬夜
        elif bf["conscientiousness"] >= 7:
            sleep = rng.choice(["22:00", "22:30"])

    hobbies_pool = {
        "高": ["阅读", "园艺", "烘焙", "徒步", "摄影", "烹饪"],
        "中": ["看电影", "跑步", "钓鱼", "游戏", "健身"],
        "低": ["刷手机", "打游戏", "看直播"],
    }
    hobbies = rng.sample(hobbies_pool.get(income_bracket, hobbies_pool["中"]), 2)

    return {
        "name": name, "age": age, "gender": gender, "occupation": occupation,
        "work_schedule": {"start": "09:00", "end": "17:00", "remote": rng.random() < 0.25,
                          "work_days": [1, 2, 3, 4, 5]},
        "personality": {
            "traits": traits,
            "big_five": bf,                       # v2：五维人格分数
            "behavior_text": big_five_to_text(bf),  # v2：行为描述（注入 prompt，无用电预设）
            "news_sensitivity": big_five_to_news_sensitivity(bf),  # v2：新闻敏感度
        },
        "habits": {"wake_time": wake, "sleep_time": sleep,
                   "exercise": rng.choice(["每周跑步", "偶尔散步", "健身房", "无"]),
                   "hobbies": hobbies},
        "health": {"condition": "良好",
                   "temperature_preference": {"summer": rng.choice([24, 25, 26]),
                                              "winter": rng.choice([21, 22, 23])}},
        "personal_appliances": [{"type": t, "brand": "Generic", "power": None, "age": 0}
                                for t in (personal or ["手机", "电脑"])],
    }


def _pick_occupation(rng, income_bracket):
    return rng.choice(INCOME_BY_OCCUPATION[income_bracket])


def _income_by_age(rng, age):
    """年龄 → 收入档（年轻人多数中低档，中年分布广，退休无收入标注）。"""
    if age >= 65:
        return "低"
    if age < 25:
        return rng.choice(["低", "中"])
    r = rng.random()
    if r < 0.3:
        return "高"
    if r < 0.75:
        return "中"
    return "低"


# ---------- 住宅生成（收入 → 面积 → 房间/电器）----------

def _home_by_income(rng, name, income_bracket, size_override=None):
    """收入档 → 住宅结构（关联链：收入→住房→电器）。

    去作弊化（用户 2026-08 指令）：不预设任何用电行为相关资产
    （如电动汽车）——所有电器均为中性物理配置，用电行为由模拟自发涌现。
    """
    sizes = {"高": rng.choice([120, 135, 150, 180]),
             "中": rng.choice([85, 95, 105, 115]),
             "低": rng.choice([55, 65, 75])}
    size = size_override or sizes[income_bracket]

    rooms = {}

    # 客厅：全收入档都有电视/灯；空调按收入
    living = ["电视", "灯"]
    if income_bracket != "低":
        living.append("空调")
    rooms["客厅"] = living

    # 厨房：冰箱必有；电饭煲/微波炉按收入
    kitchen = ["冰箱", "灯"]
    if income_bracket in ("中", "高"):
        kitchen += ["电饭煲", "微波炉"]
    if income_bracket == "高":
        kitchen += ["电磁炉", "油烟机"]
    else:
        kitchen += ["电磁炉"]
    rooms["厨房"] = kitchen

    # 卫生间：热水器/洗衣机
    rooms["卫生间"] = ["热水器", "洗衣机", "灯"]

    # 卧室数：按面积
    n_bedrooms = 1 if size <= 65 else (2 if size <= 105 else 3)
    for i in range(n_bedrooms):
        bed = ["灯", "台灯"]
        if income_bracket == "高" or (income_bracket == "中" and i == 0):
            bed.append("空调")
        rooms[f"卧室{i + 1}"] = bed

    home = {"name": name, "type": "联排别墅" if size <= 115 else "独立屋",
            "size": size, "rooms": []}
    for room_name, appliance_types in rooms.items():
        home["rooms"].append({
            "name": room_name, "size": 0,
            "appliances": [{"type": t, "brand": "Generic", "power": None, "age": 0}
                           for t in appliance_types],
        })
    return home


# ---------- 家庭模板（8 类，含成员关联规则）----------

def _build_template(household_type, rng):
    """按家庭类型生成完整 household.json（Big Five 驱动 + 成员关联）。"""
    surname = rng.choice(SURNAMES)
    income = rng.choice(["低", "中", "中", "高"])   # 整体收入分布（census 中位 2000 月供 → 中档为主）

    if household_type == "young_couple":
        age_w = rng.randint(26, 33)
        age_m = age_w + rng.randint(0, 4)   # 关联规则：夫妻年龄差 ≤4
        bf_w = sample_big_five(rng, bias={"conscientiousness": rng.choice([0, 1, 2]),
                                          "openness": rng.choice([0, 1, 1])})
        bf_m = sample_big_five(rng, bias={"conscientiousness": rng.choice([0, 0, -1])})
        return {
            "type": "年轻夫妇/丁克家庭", "season": "春天",
            "home": _home_by_income(rng, "Clayton温馨联排", income),
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "女", age_w,
                             _pick_occupation(rng, income), income, big_five=bf_w,
                             personal=["手机", "电脑", "台灯"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "男", age_m,
                             _pick_occupation(rng, income), income, big_five=bf_m),
            ],
        }

    if household_type == "family_with_kids":
        age_m = rng.randint(32, 42)
        age_w = age_m + rng.randint(-3, 3)
        kid_age = age_m - rng.randint(24, 34)   # 关联规则：孩子年龄 = 父母-24~34
        kid_age = max(4, kid_age)
        bf_parents = sample_big_five(rng, bias={"conscientiousness": 2, "agreeableness": 1})
        bf_kid = sample_big_five(rng, bias={"extraversion": 2})
        home = _home_by_income(rng, "Clayton家庭住宅", "高" if rng.random() < 0.6 else "中")
        home["rooms"].append({"name": "儿童房", "size": 0,
                              "appliances": [{"type": "灯", "brand": "Generic", "power": None, "age": 0},
                                             {"type": "台灯", "brand": "Generic", "power": None, "age": 0}]})
        return {
            "type": "有孩家庭", "season": "春天", "home": home,
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "女", age_w,
                             _pick_occupation(rng, "高" if income == "高" else "中"),
                             "高" if income == "高" else "中", big_five=bf_parents,
                             personal=["手机", "电脑"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "男", age_m,
                             _pick_occupation(rng, "高" if income == "高" else "中"),
                             "高" if income == "高" else "中", big_five=bf_parents),
                _make_member(rng, f"{rng.choice(KID_NAMES)} {surname}", rng.choice(["男", "女"]),
                             kid_age, "小学生", "低", big_five=bf_kid,
                             wake="07:00", sleep="21:00", personal=["手机"]),
            ],
        }

    if household_type == "single_living":
        age = rng.randint(22, 30) if rng.random() < 0.6 else rng.randint(62, 78)
        occ = _pick_occupation(rng, _income_by_age(rng, age)) if age < 60 else "退休"
        return {
            "type": "独居", "season": "春天",
            "home": _home_by_income(rng, "Clayton一居室", _income_by_age(rng, age)),
            "members": [_make_member(rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {surname}",
                                     rng.choice(["男", "女"]), age, occ,
                                     "低" if age >= 60 else "中")],
        }

    if household_type == "share_house":
        members = []
        for i in range(3):
            age = rng.randint(20, 29)
            bf = sample_big_five(rng, bias={"extraversion": 1, "conscientiousness": -1})
            members.append(_make_member(
                rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {rng.choice(SURNAMES)}",
                rng.choice(["男", "女"]), age, _pick_occupation(rng, "中"), "中",
                big_five=bf, wake=rng.choice(["08:30", "09:00"]),
                sleep=rng.choice(["00:00", "00:30", "01:00"])))
        return {
            "type": "合租", "season": "春天",
            "home": _home_by_income(rng, "Clayton合租公寓", "中"),
            "members": members,
        }

    if household_type == "international_student":
        # Clayton 特色：Monash 大学区国际学生（census 中位年龄 28 佐证）
        members = []
        for i in range(rng.choice([2, 3])):
            age = rng.randint(19, 27)
            country = rng.choice(["中国", "印度", "越南", "马来西亚", "印尼"])
            bf = sample_big_five(rng, bias={"openness": 2, "conscientiousness": 1})
            members.append(_make_member(
                rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {rng.choice(SURNAMES)}",
                rng.choice(["男", "女"]), age, rng.choice(STUDENT_LEVELS), "低",
                big_five=bf, wake=rng.choice(["09:00", "09:30", "10:00"]),
                sleep=rng.choice(["00:30", "01:00", "01:30"]),
                personal=["手机", "电脑", "台灯"]))
        return {
            "type": "国际学生合租", "season": "春天",
            "home": _home_by_income(rng, "Clayton学生公寓", "低"),
            "members": members,
        }

    if household_type == "multigenerational":
        # 关联规则：三代同堂，父母年龄夹在祖父母与孩子之间
        grandpa = rng.randint(62, 76)
        grandma = grandpa + rng.randint(-3, 2)
        parent_age = grandpa - rng.randint(24, 32)
        kid_age = parent_age - rng.randint(24, 34)
        kid_age = max(5, kid_age)
        return {
            "type": "多代同堂", "season": "春天",
            "home": _home_by_income(rng, "Clayton三代之家", "中", size_override=rng.choice([120, 140])),
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "男", grandpa, "退休", "低",
                             wake="06:30", sleep="21:30",
                             personal=["手机"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "女", grandma, "退休", "低",
                             wake="06:30", sleep="21:30",
                             personal=["手机"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {surname}",
                             rng.choice(["男", "女"]), parent_age, _pick_occupation(rng, "中"), "中"),
                _make_member(rng, f"{rng.choice(KID_NAMES)} {surname}", rng.choice(["男", "女"]),
                             kid_age, "小学生", "低", wake="07:00", sleep="21:00",
                             personal=["手机"]),
            ],
        }

    if household_type == "single_parent":
        age = rng.randint(29, 45)
        kid_age = age - rng.randint(22, 32)
        kid_age = max(4, kid_age)
        bf = sample_big_five(rng, bias={"conscientiousness": 1})
        return {
            "type": "单亲家庭", "season": "春天",
            "home": _home_by_income(rng, "Clayton单亲之家", "中"),
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F + FIRST_NAMES_M)} {surname}",
                             rng.choice(["女", "男"]), age, _pick_occupation(rng, "中"), "中",
                             big_five=bf, personal=["手机", "电脑"]),
                _make_member(rng, f"{rng.choice(KID_NAMES)} {surname}", rng.choice(["男", "女"]),
                             kid_age, "小学生", "低", wake="07:00", sleep="21:00",
                             personal=["手机"]),
            ],
        }

    # retired_couple
    age_m = rng.randint(66, 80)
    age_w = age_m + rng.randint(-3, 3)
    return {
        "type": "退休夫妇", "season": "春天",
        "home": _home_by_income(rng, "Clayton养老宅", "低", size_override=rng.choice([65, 75, 85])),
        "members": [
            _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "男", age_m, "退休", "低",
                         wake="06:30", sleep="21:00", personal=["手机"]),
            _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "女", age_w, "退休", "低",
                         wake="06:30", sleep="21:00", personal=["手机"]),
        ],
    }


# ---------- 家庭类型配额（census 校准 + fringe 保障）----------

HOUSEHOLD_QUOTAS = [
    ("young_couple", 25),
    ("family_with_kids", 20),
    ("share_house", 15),
    ("single_living", 15),
    ("international_student", 10),
    ("multigenerational", 5),
    ("single_parent", 5),
    ("retired_couple", 5),
]


def _quota_distribution(count, rng):
    """按配额百分比分配 count 户的类型。

    fringe 保障（呼应 2501.16080 的警告）：户数 ≥ 类型数时，每类至少 1 户，
    保证独居老人/单亲/学生等边缘群体不缺席；剩余按权重分配。
    """
    n_types = len(HOUSEHOLD_QUOTAS)
    counts = {t: 0 for t, _ in HOUSEHOLD_QUOTAS}
    if count >= n_types:
        for t, _ in HOUSEHOLD_QUOTAS:
            counts[t] = 1
    remaining = count - sum(counts.values())
    if remaining > 0:
        wheel = [t for t, w in HOUSEHOLD_QUOTAS for _ in range(w)]
        rng.shuffle(wheel)
        for t in wheel[:remaining]:
            counts[t] += 1
    return counts


# ---------- 构建入口 ----------

def _dedupe_names(household):
    """保证同一家庭内成员姓名唯一（agent 身份键要求）。"""
    seen = set()
    for m in household["members"]:
        name = m["name"]
        if name in seen:
            i = 2
            while f"{name} {i}" in seen:
                i += 1
            m["name"] = f"{name} {i}"
        seen.add(m["name"])


def build_population(world_id, count, seed=42, household_types=None):
    """本地生成 count 户异质家庭（Big Five v2），写入 worlds/<world_id>/3168/house_XXXX/。

    世界级约束（用户 2026-08 指令）：每个世界最多 10 户。
    """
    if count > 10:
        raise ValueError(f"每世界最多 10 户（收到 {count}）。请拆分多个世界。")

    rng = random.Random(seed)

    if household_types is None:
        type_counts = _quota_distribution(count, rng)
        household_types = [t for t, n in type_counts.items() for _ in range(n)]
        rng.shuffle(household_types)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_dir = os.path.join(project_root, "worlds", world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    os.makedirs(district_dir, exist_ok=True)

    households_meta = []
    for i in range(count):
        htype = household_types[i % len(household_types)]
        household = _build_template(htype, rng)
        _dedupe_names(household)   # 家庭内姓名唯一

        house_id = f"house_{i + 1:04d}"
        house_dir = os.path.join(district_dir, house_id)
        os.makedirs(house_dir, exist_ok=True)

        with open(os.path.join(house_dir, "household.json"), "w", encoding="utf-8") as f:
            json.dump(household, f, ensure_ascii=False, indent=2)

        households_meta.append({
            "house_id": house_id,
            "type": household["type"],
            "members_count": len(household["members"]),
            "rooms_count": len(household["home"]["rooms"]),
        })
        print(f"  生成 {house_id}：{household['type']}（{len(household['members'])}人/"
              f"{len(household['home']['rooms'])}房间）")

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
        "user_prompt": f"人口构建 v2（seed={seed}，Big Five 人格 + 8 类家庭 + census 校准）",
        "generator": "population.py v2",
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
    parser = argparse.ArgumentParser(description="本地人口构建 v2（0 LLM 调用）")
    parser.add_argument("world_id", help="新世界ID，如 pop03")
    parser.add_argument("--count", type=int, default=12, help="家庭数量")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    print(f"人口构建 v2：world={args.world_id}，{args.count} 户，种子 {args.seed}")
    build_population(args.world_id, args.count, args.seed)
    print(f"完成：worlds/{args.world_id}/ 已生成")

