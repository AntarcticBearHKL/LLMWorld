from datetime import datetime

from .news import NewsItem

TEMPLATES = {
    "heatwave": {
        "title": "气象局发布极端高温预警",
        "content": "维多利亚州遭遇热浪天气，未来三天最高气温将达 40°C 以上，电网负荷预计创夏季新高。",
        "source": "气象局",
        "type": "环境",
    },
    "cold_snap": {
        "title": "强冷空气来袭，寒潮预警",
        "content": "墨尔本遭遇寒潮，未来一周夜间气温将降至 2°C 以下，气象局提醒居民注意保暖。",
        "source": "气象局",
        "type": "环境",
    },
    "storm": {
        "title": "暴风雨预警：强降雨可能引发停电",
        "content": "气象局发布暴风雨预警，强风可能刮倒电线导致局部停电，电力公司建议居民提前备好应急设备。",
        "source": "气象局",
        "type": "环境",
    },
    "price_hike": {
        "title": "电力公司宣布下月起电费上调",
        "content": "维州主要电力零售商宣布下月起电费平均上调 8%，能源监管局表示将审查调价幅度。",
        "source": "新闻媒体",
        "type": "经济",
    },
    "energy_crisis": {
        "title": "国际能源价格暴涨，电力供应承压",
        "content": "受国际局势影响，天然气与煤炭价格大幅上涨，电力批发价走高，专家呼吁居民节约用电。",
        "source": "新闻媒体",
        "type": "经济",
    },
    "ac_tax": {
        "title": "政府宣布开征空调用电高峰附加税",
        "content": "州政府宣布为应对电网压力，对家用空调高峰时段用电征收 10% 附加税。",
        "source": "政府公告",
        "type": "政策",
    },
    "rebate": {
        "title": "社区节能返利计划推出",
        "content": "Clayton 社区推出节能返利：本月家庭用电量同比下降 10% 可获得 30 澳元返利。",
        "source": "社区公告",
        "type": "社会",
    },
    "blackout_risk": {
        "title": "电网公司发布限电风险警告",
        "content": "极端天气下电网负荷接近上限，电网公司警告高峰时段可能实施轮换限电，请居民错峰用电。",
        "source": "电网公司",
        "type": "经济",
    },
    "solar_incentive": {
        "title": "屋顶太阳能补贴新政公布",
        "content": "州政府公布屋顶太阳能安装补贴新政，符合条件的家庭可获最高 3000 澳元安装补贴。",
        "source": "政府公告",
        "type": "政策",
    },
    "lockdown": {
        "title": "疫情管控措施收紧",
        "content": "受新一波疫情影响，州政府宣布收紧管控，建议居民居家办公、减少非必要外出。",
        "source": "政府公告",
        "type": "社会",
    },
}


def build_template(name, date_str, time="07:00"):
    if name not in TEMPLATES:
        raise ValueError(f"未知新闻模板: {name}（可用: {'/'.join(sorted(TEMPLATES))}）")
    t = TEMPLATES[name]
    return NewsItem(date=date_str, time=time, title=t["title"], content=t["content"],
                    source=t["source"], news_type=t["type"])


def template_names():
    return sorted(TEMPLATES)
