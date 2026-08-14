











import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import partial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import World, utils, SubAgent
from simulate import load_world, create_home_from_household
import config





def aggregate_population(house_results):

    total_profile = [0.0] * 1440
    per_house = []

    for house_id, day_result in house_results:
        calculator = day_result["energy_calculator"]
        profile = calculator.household_load_watts
        total_kwh = day_result["energy_summary"]["total_energy_kwh"]

        for m in range(1440):
            total_profile[m] += profile[m]

        peak_minute = max(range(1440), key=lambda m: profile[m])
        per_house.append({
            "house_id": house_id,
            "total_energy_kwh": round(total_kwh, 4),
            "peak_watts": round(profile[peak_minute], 2),
            "peak_time": f"{peak_minute // 60:02d}:{peak_minute % 60:02d}",
        })

    peak_minute = max(range(1440), key=lambda m: total_profile[m])
    kwhs = [h["total_energy_kwh"] for h in per_house]
    n = len(kwhs)
    mean = sum(kwhs) / n if n else 0
    std = (sum((k - mean) ** 2 for k in kwhs) / n) ** 0.5 if n else 0
    kwhs_sorted = sorted(kwhs)
    median = kwhs_sorted[n // 2] if n else 0

    return {
        "households": n,
        "total_energy_kwh": round(sum(kwhs), 4),
        "mean_household_kwh": round(mean, 4),
        "median_household_kwh": round(median, 4),
        "std_household_kwh": round(std, 4),
        "peak_watts": round(total_profile[peak_minute], 2),
        "peak_time": f"{peak_minute // 60:02d}:{peak_minute % 60:02d}",
        "load_profile_watts": [round(w, 2) for w in total_profile],
        "hourly_average_watts": [
            round(sum(total_profile[h * 60:(h + 1) * 60]) / 60.0, 2)
            for h in range(24)
        ],
        "per_house": per_house,
    }


def main_aggregate_only(args, project_root, pop_root):

    from simulate import load_world
    world_meta, district_info, households = load_world(args.world_id)
    postcode = district_info["postcode"]

    class _ProfileSource:
        def __init__(self, watts):
            self.household_load_watts = watts

    simulation_root = os.path.join(project_root, "simulation", args.world_id, postcode)
    house_results = []
    for info in households:
        house_id = info["house_id"]
        house_dir = os.path.join(simulation_root, house_id)
        if not os.path.isdir(house_dir):
            continue



        date_candidates = []
        for entry in os.listdir(house_dir):
            entry_path = os.path.join(house_dir, entry)
            if os.path.isdir(entry_path):
                sub = os.listdir(entry_path)
                if any(d.isdigit() and len(d) == 8 for d in sub):
                    date_candidates.extend(os.path.join(entry_path, d) for d in sub
                                           if d.isdigit() and len(d) == 8)
                elif entry.isdigit() and len(entry) == 8:
                    date_candidates.append(entry_path)
        if not date_candidates:
            continue
        date_candidates.sort()
        profile_path = os.path.join(date_candidates[-1], "用电信息",
                                    "house_load_profile_1440min.json")
        if not os.path.exists(profile_path):
            continue
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        house_results.append((house_id, {
            "energy_calculator": _ProfileSource(profile["load_profile_watts"]),
            "energy_summary": {"total_energy_kwh": profile["total_energy_kwh"]},
        }))

    if not house_results:
        print("没有找到任何已保存的模拟结果，请先运行模拟")
        sys.exit(1)

    population = aggregate_population(house_results)
    os.makedirs(pop_root, exist_ok=True)
    out_path = os.path.join(pop_root, "aggregate_only.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(population, f, ensure_ascii=False, indent=2)

    print(f"离线聚合完成（{len(house_results)} 户，0 token）")
    print(f"  人口总用电 {population['total_energy_kwh']} kWh"
          f"（户均 {population['mean_household_kwh']}，中位 {population['median_household_kwh']}，"
          f"标准差 {population['std_household_kwh']}）")
    print(f"  人口峰值 {population['peak_watts']} W @ {population['peak_time']}")
    for h in population["per_house"]:
        print(f"    - {h['house_id']}: {h['total_energy_kwh']} kWh, 峰值 {h['peak_watts']}W@{h['peak_time']}")
    print(f"  已保存: {out_path}")


def _policy_for_date(schedule, date_str):
    for start, end, name in schedule:
        if start and date_str < start:
            continue
        if end and date_str > end:
            continue
        return name
    return None


def neighbor_mean_kwh(prev_kwhs, house_id):
    others = [kwh for hid, kwh in prev_kwhs.items() if hid != house_id and kwh]
    if not others:
        return None
    return round(sum(others) / len(others), 1)


def run_one(item, args, selected, prev_kwhs, policy_schedule, location, scenario_name):
    """单户单日模拟，运行在独立子进程中（多进程并行）。

    参数必须全部可 pickle。返回 (house_id, day_result)；异常时 day_result 含 _error。
    """
    house_id, world = item
    try:
        household = next(h for h in selected if h["house_id"] == house_id)["household"]
        from engine.policy import Policy
        date_iso = world.time.date.strftime('%Y-%m-%d')
        season = household.get("season") or utils.season_for_date(date_iso)

        from engine.environment_interface import EnvironmentInterface
        if args.peer_nudge and prev_kwhs:  # 第 2 天起：用邻居前一天实际用电做对比
            mean = neighbor_mean_kwh(prev_kwhs, house_id)
            if mean is not None:
                nudge = Policy.nudge(
                    comparison_text=f"你的邻居平均每天用电 {mean} 千瓦时")
                cur_context = nudge.render()
                cur_policy = "peer_nudge"
            else:
                cur_context = ""
                cur_policy = "baseline"
        else:
            cur_policy = (_policy_for_date(policy_schedule, date_iso)
                          if policy_schedule else args.policy)
            cur_context = Policy.from_name(cur_policy).render() if cur_policy else ""
        env = EnvironmentInterface.get_weather(location, date_iso, season)
        day_result = world.simulate_day(
            season=season,
            weather=env["condition"],
            temperature=env["temperature"]["avg"],
            verbose=False,
            policy_context=cur_context,
            policy_name=scenario_name,
            community_notice=args.community_notice or "")
        day_result["_env"] = {"season": season, "condition": env["condition"],
                              "temperature": env["temperature"]["avg"],
                              "mode": env.get("mode", "?")}
        day_result["_policy"] = cur_policy or "baseline"
        day_result["_tokens"] = world.get_total_tokens()  # 子进程 token 累计，回传主进程汇总
        return house_id, day_result
    except Exception as e:
        return house_id, {"_error": f"{type(e).__name__}: {e}"}


def main():
    parser = argparse.ArgumentParser(description="人口级并行模拟（每户一个进程）")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--start", metavar="WORLD_ID",
                      help="用世界开始一个新的模拟环境（如 pop03）；可配 --date 指定开始日期，缺省用默认")
    mode.add_argument("--continue", dest="continue_env", metavar="ENV_ID",
                      help="续跑已有模拟环境（如 pop03_1505），从上次日期下一天继续")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--date", type=str, default=None,
                        help="开始日期(如 2026-04-21 或 2026年4月21日)。--start 时缺省=世界默认开始日期；--continue 时必须等于环境下一天")
    parser.add_argument("--house-start", type=int, default=0, help="起始家庭序号")
    parser.add_argument("--house-count", type=int, default=None, help="参与家庭数（默认全部）")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    parser.add_argument("--policy", default=None,
                        help="政策干预（RQ2）：tou 分时电价 / subsidy 低谷补贴 / nudge 社会规范 / nudge_loss 损失框架")
    parser.add_argument("--policy-schedule", action="append", default=None,
                        help="政策时间表(可多次)：开始,结束,政策名（结束留空=永久），如 2026-04-25,2026-04-28,tou")
    parser.add_argument("--event", action="append", default=None,
                        help="上帝注入的世界事件（可多次）：日期|标题|内容[|来源]，如 "
                        "'2026-04-21|政府宣布开征空调用电附加税|从今日起空调电价上调10个百分点|政府公告'")
    parser.add_argument("--event-template", action="append", default=None,
                        help="新闻模板注入（可多次）：日期|模板名，如 2026-01-15|heatwave")
    parser.add_argument("--scenario", default=None,
                        help="场景标签（聚合输出目录名，默认=政策名或 baseline）。"
                        "新闻实验请用自定义名如 war_news，避免与基线混淆")
    parser.add_argument("--no-events", action="store_true",
                        help="跳过 worlds/<id>/events.json 剧本（仅用命令行 --event）")
    parser.add_argument("--peer-nudge", action="store_true",
                        help="个性化 nudge：第 2 天起每户收到基于邻居前一天实际用电的社会规范文本（Ayres 2013）")
    parser.add_argument("--community-notice", default=None,
                        help="社区公告板文本（所有家庭同见，轻量社交网络入口，如 '本社区本周节能目标 5 个百分点'）")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="不跑 LLM，直接从已保存的 simulation 曲线文件离线聚合")
    args = parser.parse_args()

    utils.set_seed(args.seed)


    from simulation_env import (resolve_sim_date, continue_env_date, update_env_date,
                                env_from_id, zh_to_iso)
    if args.start:
        world_id = args.start
        if args.date and "-" in args.date:
            y, m, d = args.date.split("-")
            args.date = f"{int(y)}年{int(m)}月{int(d)}日"
        # 新建模拟环境；--date 缺省用世界默认开始日期
        env_id, args.date = resolve_sim_date(world_id, args.date)
    else:
        # 续跑已有环境：必须从 last_date + 1 继续（线性约束，--date 只能等于下一天）
        st = env_from_id(args.continue_env)
        world_id = st["world_id"]
        env_id = args.continue_env
        expected = continue_env_date(env_id)
        if args.date and zh_to_iso(args.date) != zh_to_iso(expected):
            print(f"[错误] 续跑环境 {env_id} 只能从 {expected} 继续（线性约束），收到 {args.date}")
            sys.exit(1)
        args.date = expected
    args.world_id = world_id
    print(f"模拟环境: {env_id}")
    print(f"开始日期: {args.date}（时间线校验通过）")


    policy_schedule = []  # 先初始化（scenario_name 计算会引用）
    scenario_name = args.scenario
    if not scenario_name:
        if args.peer_nudge:
            scenario_name = "peer_nudge"
        elif policy_schedule:
            scenario_name = "schedule"
        elif args.policy:
            scenario_name = args.policy.replace(",", "+")
        else:
            scenario_name = "baseline"


    inline_events = []
    if args.event:
        from engine.news import NewsItem
        for text in args.event:
            parts = [p.strip() for p in text.split("|")]
            if len(parts) < 3:
                print(f"[错误] 事件格式应为 日期|标题|内容[|来源]：{text}")
                sys.exit(1)
            inline_events.append(NewsItem(
                date=parts[0], time="07:00", title=parts[1], content=parts[2],
                source=parts[3] if len(parts) > 3 else "官方公告"))
        print(f"上帝注入新闻 {len(inline_events)} 条")

    if args.event_template:
        from engine.news_templates import build_template
        for text in args.event_template:
            parts = [p.strip() for p in text.split("|")]
            if len(parts) < 2:
                print(f"[错误] 模板注入格式应为 日期|模板名：{text}")
                sys.exit(1)
            try:
                inline_events.append(build_template(parts[1], parts[0]))
            except ValueError as e:
                print(f"[错误] {e}")
                sys.exit(1)
        print(f"新闻模板注入 {len(args.event_template)} 条")


    policy_context = ""
    policy_name = None
    if args.policy:
        from engine.policy import Policy
        policy = Policy.from_name(args.policy)
        policy_name = policy.describe()
        policy_context = policy.render()
        print(f"政策干预: {policy_name}")

    if args.policy_schedule:
        if args.policy:
            print("[错误] --policy 与 --policy-schedule 不能同时使用")
            sys.exit(1)
        from engine.policy import Policy
        for text in args.policy_schedule:
            parts = [p.strip() for p in text.split(",")]
            if len(parts) < 2 or not parts[0]:
                print(f"[错误] 政策时间表格式应为 开始,结束,政策名：{text}")
                sys.exit(1)
            name = parts[-1]
            end = parts[1] if len(parts) > 1 and parts[1] else ""
            policy_schedule.append((parts[0], end, name))
            Policy.from_name(name)
        print(f"政策时间表: {len(policy_schedule)} 段")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_root = os.path.join(project_root, "simulation", env_id, "population")

    if args.aggregate_only:
        main_aggregate_only(args, project_root, pop_root)
        return

    world_meta, district_info, households = load_world(args.world_id)
    selected = households[args.house_start:]
    if args.house_count:
        selected = selected[:args.house_count]

    print(f"人口模拟：{len(selected)} 户 × {args.days} 天（world {args.world_id}）")
    location = district_info["location"]
    postcode = district_info["postcode"]

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_root = os.path.join(project_root, "simulation", env_id, "population")


    worlds = {}
    homes = {}
    for info in selected:
        household = info["household"]
        home = create_home_from_household(household)
        homes[info["house_id"]] = home
        world = World(
            home, world_id=args.world_id, postcode=postcode,
            house_id=info["house_id"], start_date=args.date, env_id=env_id)

        if args.no_events:
            world.news.items = []

        for item in inline_events:
            world.news.add_event(item)
        worlds[info["house_id"]] = world

    prev_kwhs = {}
    total_tokens = {"prompt_cache_miss": 0, "prompt_cache_hit": 0, "completion": 0}
    # 多进程池：每户一个独立进程跑当天；跨天串行（peer_nudge 需要前一天聚合结果）
    with ProcessPoolExecutor(max_workers=min(len(worlds), 12)) as pool:
        for day in range(args.days):
            print(f"\n=== 第 {day + 1}/{args.days} 天 ===")

            house_results = list(pool.map(
                partial(run_one, args=args, selected=selected, prev_kwhs=prev_kwhs,
                        policy_schedule=policy_schedule, location=location,
                        scenario_name=scenario_name),
                worlds.items()))

            # 异常兜底：失败的家庭跳过，其余正常聚合
            failed = [(h, r) for h, r in house_results if "_error" in r]
            for h, r in failed:
                print(f"  [错误] {h} 当天模拟失败：{r['_error']}")
            house_results = [(h, r) for h, r in house_results if "_error" not in r]
            if not house_results:
                print("[错误] 全部家庭模拟失败，终止")
                break

            for _h, r in house_results:
                tk = r.get("_tokens") or {}
                for k in total_tokens:
                    total_tokens[k] += tk.get(k, 0)

            prev_kwhs = {h: r["energy_summary"]["total_energy_kwh"]
                         for h, r in house_results}


            population = aggregate_population(house_results)
            population["policy"] = scenario_name
            population["environment"] = {h: r.get("_env", {}) for h, r in house_results}
            policies = {h: r.get("_policy", "baseline") for h, r in house_results}
            population["day_policy"] = next(iter(policies.values()), "baseline")
    
            date_str = house_results[0][1]["date"].replace("年", "-").replace("月", "-").replace("日", "")
    
            policy_dir = scenario_name
            out_dir = os.path.join(pop_root, policy_dir, date_str)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, "population_profile_1440min.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(population, f, ensure_ascii=False, indent=2)
    
            print(f"  人口总用电 {population['total_energy_kwh']} kWh"
                  f"（户均 {population['mean_household_kwh']}，中位 {population['median_household_kwh']}，"
                  f"标准差 {population['std_household_kwh']}）")
            print(f"  人口峰值 {population['peak_watts']} W @ {population['peak_time']}")
            print(f"  已保存: {out_path}")
    
    
            for h in population["per_house"]:
                print(f"    - {h['house_id']}: {h['total_energy_kwh']} kWh, 峰值 {h['peak_watts']}W@{h['peak_time']}")
    
    
            for house_id, day_result in house_results:
                executor_obj = day_result["executor"]
                if executor_obj and executor_obj.validation_warnings:
                    print(f"  [警告] {house_id} {len(executor_obj.validation_warnings)} 条决策校验问题")
    
            if day < args.days - 1:
                for world in worlds.values():
                    world.next_day()
    
    # 环境日期推进到最后模拟的一天
    last_date = next(iter(worlds.values())).time.date.strftime('%Y-%m-%d')
    update_env_date(env_id, last_date)


    tokens = total_tokens  # 跨进程汇总（主进程 World 无 token）
    total = tokens["prompt_cache_miss"] + tokens["prompt_cache_hit"] + tokens["completion"]
    print(f"\n=== Token 账单（{args.days} 天 × {len(worlds)} 户，跨进程汇总）===")
    print(f"  缓存未命中 {tokens['prompt_cache_miss']} + 缓存命中 {tokens['prompt_cache_hit']} + 输出 {tokens['completion']} = {total}")
    print(f"  户均/天 ≈ {total / (args.days * len(worlds)):.0f} tokens")


    current, peak = SubAgent.get_concurrency_stats()
    print("\n=== 并发实测（观测，无限制）===")
    print(f"  历史峰值并发 {peak}")
    print("人口模拟完成")


if __name__ == "__main__":
    main()



