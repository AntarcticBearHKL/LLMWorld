import os
import re
import sys
import urllib.request

PAPERS = [
    ("2310.20367", "A Machine Learning-Based Framework for Clustering Residential Electricity Load Profiles to Enhance Demand Response Programs", "Michalakopoulos et al.", 2023, "计划40"),
    ("1409.1043", "Variability of Behaviour in Electricity Load Profile Clustering: Who Does Things at the Same Time Each Day", "Dent et al.", 2014, "计划40/45"),
    ("2210.03524", "Variability in Electricity Consumption by Category of Consumer: The Impact on Electricity Load Profiles", "Gunkel et al.", 2022, "计划40/43/48/51"),
    ("1607.00595", "Residential Demand Response Targeting Using Machine Learning with Observational Data", "Zhou et al.", 2016, "计划41/45"),
    ("2102.11027", "Investigating Underlying Drivers of Variability in Residential Energy Usage Patterns with Daily Load Shape Clustering of Smart Meter Data", "Jin et al.", 2021, "计划41/42/55"),
    ("2105.11952", "Long-term Value of Flexibility from Flexible Assets in Building Operation", "Thorvaldsen et al.", 2021, "计划43/47/48"),
    ("2509.10713", "Demand Charge Management: Prototype Design and Testing", "Escarrega et al.", 2025, "计划43"),
    ("2112.04559", "Achieving Reliable Coordination of Residential Plug-in Electric Vehicle Charging: A Pilot Study", "Alexeenko & Bitar", 2023, "计划43/47"),
    ("2607.25447", "CoRenew: A Large Language Model Agent-Based Policy Simulation Platform for Multifamily Residential Redevelopment", "Zhang et al.", 2026, "计划44/53"),
    ("2511.07204", "Evaluating Online Moderation via LLM-Powered Counterfactual Simulations", "Fidone et al.", 2025, "计划46/50/55/56/59"),
    ("2607.26588", "Eco3S: Complex Socio-Economic System Simulation via Agent-Based Models", "Wei et al.", 2026, "计划51"),
    ("2306.02473", "Anomaly Detection Techniques in Smart Grid Systems: A Review", "Banik et al.", 2023, "计划62"),
    ("1702.03767", "Is Big Data Sufficient for a Reliable Detection of Non-Technical Losses", "Glauner et al.", 2017, "计划62"),
    ("2604.03344", "Towards Intelligent Energy Security: A Unified Spatio-Temporal and Graph Learning Framework for Scalable Electricity Theft Detection in Smart Grids", "Olowookere et al.", 2026, "计划62"),
    ("2607.17437", "Empirical Grounding Improves the Realism of LLM Agents Simulating Human Behavior During Disruptions", "Xia et al.", 2026, "计划64"),
    ("2508.09964", "Deep and Diverse Population Synthesis for Multi-Person Households", None, None, "计划22"),
    ("2605.17031", "Joint Synthetic Housing-Household Inventory", None, None, "计划22"),
    ("2501.16080", "WGAN Spatial Populations", None, None, "计划22"),
    ("2302.09193", "Copula-Based Synthetic Population Generation", None, None, "计划22"),
    ("1904.07998", "SynC: Synthetic Data Generation with Copulas", None, None, "计划22"),
    ("2603.22558", "Maximum Entropy-Based Synthetic Population Generation", None, None, "计划22"),
    ("2112.12071", "AToM: Melbourne Synthetic Population and Activity Patterns", None, None, "计划22"),
    ("2601.06158", "PsyAgent: Big Five Personality-Driven LLM Agent", None, None, "计划22"),
    ("2603.21358", "Personality Student Agents: Big Five and Human Alignment", None, None, "计划22"),
    ("2604.12250", "LLM Social Particle Swarm: Personality Heterogeneity in Behavior", None, None, "计划22"),
    ("2512.19933", "PRISM: Personalized Cognitive Strategies for Consistent Behavior", None, None, "计划22"),
    ("2501.08985", "Personality-Driven LLM Agents", None, None, "计划22"),
    ("2306.11566", "Uniform Taxation of Electricity: Incentives for Flexibility and Cost Redistribution among Household Categories", "Gunkel et al.", 2023, "计划71"),
    ("2512.16949", "Identifying and Understanding Obstacles to Heating Sobriety and Thermal Comfort in Collective Housing", "Cabezas-Rivière et al.", 2025, "计划75"),
    ("1505.01311", "An Open Solution to Provide Personalized Feedback for Building Energy Management", "Monacchi et al.", 2015, "计划83"),
]


def clean_title(title):
    text = title.replace(":", " - ")
    text = re.sub(r'[\\/*?"<>|]', " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[. ]+$", "", text)
    return text[:200]


def main():
    ref_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RefPaper")
    os.makedirs(ref_dir, exist_ok=True)
    index_lines = ["# RefPaper —— arXiv 论文本地存档", "",
                   "| 标题 | 作者 | 年份 | arXiv ID | 引用位置 | 文件 |",
                   "|---|---|---|---|---|---|"]
    ok = 0
    fail = []
    for arxiv_id, title, author, year, ref in PAPERS:
        filename = clean_title(title) + ".pdf"
        filepath = os.path.join(ref_dir, filename)
        author_text = author or "-"
        year_text = str(year) if year else "-"
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            ok += 1
            index_lines.append(f"| {title} | {author_text} | {year_text} | arXiv:{arxiv_id} | {ref} | {filename} |")
            continue
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r, open(filepath, "wb") as f:
                f.write(r.read())
            size = os.path.getsize(filepath)
            if size < 10000:
                os.remove(filepath)
                raise RuntimeError("太小，可能非 PDF")
            ok += 1
            print(f"下载成功: {arxiv_id} -> {filename} ({size // 1024}KB)")
            index_lines.append(f"| {title} | {author_text} | {year_text} | arXiv:{arxiv_id} | {ref} | {filename} |")
        except Exception as e:
            fail.append((arxiv_id, str(e)))
            print(f"下载失败: {arxiv_id} {e}")
    with open(os.path.join(ref_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines) + "\n")
    print(f"\n完成: 成功 {ok}/{len(PAPERS)}")
    if fail:
        print("失败项:")
        for aid, err in fail:
            print(f"  {aid}: {err}")


if __name__ == "__main__":
    main()
