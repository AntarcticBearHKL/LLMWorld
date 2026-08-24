from datetime import datetime

from .news import NewsItem

TEMPLATES = {
    "heatwave": {
        "title": "Meteorological Bureau issues extreme heat warning",
        "content": "Victoria is hit by a heatwave; maximum temperatures are forecast to exceed 40°C over the next three days, "
                   "and the grid load is expected to set a new summer high.",
        "source": "Meteorological Bureau",
        "type": "Environment",
    },
    "cold_snap": {
        "title": "Strong cold air arrives, cold snap warning",
        "content": "Melbourne is hit by a cold snap; overnight temperatures will drop below 2°C over the next week, "
                   "and the Meteorological Bureau reminds residents to keep warm.",
        "source": "Meteorological Bureau",
        "type": "Environment",
    },
    "storm": {
        "title": "Storm warning: heavy rain may cause power outages",
        "content": "The Meteorological Bureau issues a storm warning; strong winds may knock down power lines and cause local outages, "
                   "and the power company advises residents to prepare emergency equipment in advance.",
        "source": "Meteorological Bureau",
        "type": "Environment",
    },
    "price_hike": {
        "title": "Power company announces electricity price increase from next month",
        "content": "Victoria's major electricity retailers announce an average 8% increase in electricity prices from next month, "
                   "and the energy regulator says it will review the scale of the increase.",
        "source": "News media",
        "type": "Economy",
    },
    "energy_crisis": {
        "title": "International energy prices surge, electricity supply under pressure",
        "content": "Affected by the international situation, natural gas and coal prices have risen sharply and wholesale electricity "
                   "prices are climbing; experts urge residents to conserve electricity.",
        "source": "News media",
        "type": "Economy",
    },
    "ac_tax": {
        "title": "Government announces surcharge on peak-hour AC electricity",
        "content": "The state government announces a 10% surcharge on household air-conditioning electricity used during peak hours "
                   "to ease grid pressure.",
        "source": "Government announcement",
        "type": "Policy",
    },
    "rebate": {
        "title": "Community energy-saving rebate program launched",
        "content": "The Clayton community launches an energy-saving rebate: households whose electricity use this month is down 10% "
                   "year-on-year can receive a 30 AUD rebate.",
        "source": "Community notice",
        "type": "Society",
    },
    "blackout_risk": {
        "title": "Grid company issues load-shedding risk warning",
        "content": "Under extreme weather the grid load is near its limit; the grid company warns that rotating blackouts may be "
                   "implemented during peak hours and asks residents to shift electricity use off-peak.",
        "source": "Grid company",
        "type": "Economy",
    },
    "solar_incentive": {
        "title": "New rooftop solar subsidy policy announced",
        "content": "The state government announces a new rooftop solar installation subsidy; eligible households can receive up to "
                   "3000 AUD in installation subsidies.",
        "source": "Government announcement",
        "type": "Policy",
    },
    "lockdown": {
        "title": "Pandemic control measures tightened",
        "content": "Affected by a new wave of the pandemic, the state government announces tightened controls and advises residents "
                   "to work from home and reduce unnecessary outings.",
        "source": "Government announcement",
        "type": "Society",
    },
}


def build_template(name, date_str, time="07:00"):
    if name not in TEMPLATES:
        raise ValueError(f"Unknown news template: {name} (available: {'/'.join(sorted(TEMPLATES))})")
    t = TEMPLATES[name]
    return NewsItem(date=date_str, time=time, title=t["title"], content=t["content"],
                    source=t["source"], news_type=t["type"])


def template_names():
    return sorted(TEMPLATES)
