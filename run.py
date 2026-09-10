import argparse
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
import generate_world as gw
from engine import policy as engine_policy, news, social
from steps.world import s1_household_types, s2_persona_align, s3_household_build, s4_world_assemble
from steps.simulate import s1_macro_plan, s2_coordinate, s3_enrich, s4_appliance_decision, day_state

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WORLDS_DIR = os.path.join(PROJECT_ROOT, "output", "worlds")


def apply_sampling_overrides(temperature=None, thinking=None, reasoning_effort=None):
    applied = {}
    if temperature is not None:
        config.TEMPERATURE = float(temperature)
        applied["temperature"] = config.TEMPERATURE
    if thinking is not None:
        config.THINKING = bool(thinking)
        applied["thinking"] = config.THINKING
    if reasoning_effort is not None:
        config.REASONING_EFFORT = str(reasoning_effort)
        applied["reasoning_effort"] = config.REASONING_EFFORT
    return applied


def _peer_nudge_text(world_id, date, prev_date, env):
    try:
        from analyze import dataset
        profile = dataset.population_profile(world_id, "baseline", prev_date, env=env)
        totals = [house.get("total_energy_kwh") for house in profile.get("per_house", [])]
    except Exception as exc:
        print(f"[PeerNudge] skipped for {date}: {exc}")
        return ""
    text = social.render_peer_nudge(social.community_mean_kwh(totals))
    if text:
        print(f"[PeerNudge] {date}: {text}")
    return text


def auto_world_id():
    while True:
        cand = f"world_{random.randint(100000, 999999)}"
        if not os.path.isdir(os.path.join(WORLDS_DIR, cand)):
            return cand


def run_house(world_id, house, seed):
    print(f"\n########## HOUSE {house} ##########")
    ok, r = s2_persona_align.run_step(world_id, house, seed)
    if not ok:
        print(f"[Abort] house {house} s2 failed: {r}")
        return False
    ok, r = s3_household_build.run_step(world_id, house, seed)
    if not ok:
        print(f"[Abort] house {house} s3 failed: {r}")
        return False
    ok, r = s4_world_assemble.run_step(world_id, house, seed)
    if not ok:
        print(f"[Abort] house {house} s4 failed: {r}")
        return False
    return True


def run_world(world_id, count, seed, workers=4, world_config=None):
    print(f"\n########## WORLD {world_id} (count={count}, workers={workers}, config={world_config or 'default'}) ##########")
    ok, r = s1_household_types.run_step(world_id, count, seed, world_config)
    if not ok:
        print(f"[Abort] s1 failed: {r}")
        return 1
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda h: run_house(world_id, h, seed), range(count)))
    if not all(results):
        print("[Warn] some households failed")
    print(f"\n########## WORLD {world_id} DONE ##########")
    return 0 if all(results) else 1


def get_member_names(world_id, house="house_0001"):
    home = s1_macro_plan.load_home(world_id, house)
    if home is None:
        return []
    members = list(home.members.values()) if isinstance(home.members, dict) else home.members
    return [m.name for m in members]


def run_simulate(world_id, date, env, workers, member=None, policy_spec=None, s4_only=False,
                 houses=None, days=1, events=None, notices=None, policy_schedule=None,
                 peer_nudge=False):
    print(f"\n########## SIMULATE world={world_id} env={env} workers={workers} "
          f"policy={policy_spec or 'none'} s4_only={s4_only} days={days} houses={houses or 'all'} ##########")
    policy_text, policy_tag = engine_policy.parse_policy_arg(policy_spec)

    events = list(events or [])
    notices = list(notices or [])
    if events or notices:
        events_path = news.write_events_json(os.path.join(gw.WORLDS_DIR, world_id), events + notices)
        print(f"[Events] registered {len(events)} event(s) + {len(notices)} notice(s) -> {events_path}")

    if days < 1:
        print("[Abort] --days must be >= 1")
        return 1
    start = date or time.strftime("%Y-%m-%d")
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        print(f"[Abort] invalid --date '{start}' (expected YYYY-MM-DD)")
        return 1
    dates = [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    if isinstance(houses, str):
        house_list = [h.strip() for h in houses.split(",") if h.strip()]
    elif houses:
        house_list = list(houses)
    else:
        house_list = gw.list_houses(world_id)
    if not house_list:
        print(f"[Abort] no houses found for world {world_id} (looked under {gw.WORLDS_DIR})")
        return 1
    print(f"[Houses] {house_list}")
    print(f"[Dates] {dates}")

    failed = []
    for house in house_list:
        names = get_member_names(world_id, house)
        if not names:
            print(f"[WARN] no members found world={world_id} house={house}; skipping")
            failed.append((house, None))
            continue
        targets = [member] if member else names
        if member and str(member).isdigit():
            idx = int(member)
            if 0 <= idx < len(names):
                targets = [names[idx]]
            else:
                print(f"[WARN] member index {idx} out of range (0-{len(names)-1}) for house={house}; skipping")
                failed.append((house, None))
                continue
        unknown = [m for m in targets if m not in names]
        if unknown:
            print(f"[WARN] member(s) {unknown} not in {names} for house={house}; skipping")
            failed.append((house, None))
            continue

        for di, d in enumerate(dates):
            prev_date = dates[di - 1] if di > 0 else None
            print(f"\n########## SIMULATE world={world_id} house={house} date={d} env={env} "
                  f"workers={workers} policy={policy_spec or 'none'} s4_only={s4_only} ##########")
            print(f"[Members] {targets}")
            active_events = news.events_for_date(events, d, config.NEWS_MEMORY_KEEP)
            active_notices = news.events_for_date(notices, d, config.NEWS_MEMORY_KEEP)
            day_news = news.render_world_news(active_events)
            day_notice = news.render_world_news(active_notices)
            weather_effect = news.weather_override_for(active_events)
            if policy_schedule:
                day_spec = engine_policy.active_policy_spec(policy_schedule, d)
                day_policy_text, day_policy_tag = engine_policy.parse_policy_arg(day_spec)
                print(f"[Policy] {d}: {day_spec or 'none'}")
            else:
                day_policy_text, day_policy_tag = policy_text, policy_tag
            peer_text = _peer_nudge_text(world_id, d, prev_date, env) if (peer_nudge and prev_date) else ""
            s4_news = "\n\n".join(part for part in (day_news, peer_text) if part)
            if active_events or active_notices:
                print(f"[Signals] events={len(active_events)} notices={len(active_notices)} for {d}")

            if not s4_only:
                prev_states = {}
                if prev_date:
                    prev_dir = os.path.join(gw.SIMULATION_DIR, env or world_id, prev_date, house)
                    for m in targets:
                        prev_states[m] = day_state.load_day_state(prev_dir, m)
                    carried = [m for m in targets if prev_states.get(m)]
                    if carried:
                        print(f"[Continuity] carry-over from {prev_date}: {carried}")
                with ThreadPoolExecutor(max_workers=workers) as ex:
                    results = list(ex.map(
                        lambda m: s1_macro_plan.run_step(world_id, m, d, env, house=house,
                                                         prev_state=prev_states.get(m),
                                                         world_news=day_news,
                                                         community_notice=day_notice),
                        targets))
                if any(not r[0] for r in results):
                    print(f"[WARN] s1 failed for some members (house={house} date={d})")
                    failed.append((house, d))
                    continue

                results = [s2_coordinate.run_step(world_id, m, d, env, house=house) for m in targets]
                if any(not r[0] for r in results):
                    print(f"[WARN] s2 failed for some members (house={house} date={d})")
                    failed.append((house, d))
                    continue

                with ThreadPoolExecutor(max_workers=workers) as ex:
                    results = list(ex.map(lambda m: s3_enrich.run_step(world_id, m, d, env, house=house), targets))
                if any(not r[0] for r in results):
                    print(f"[WARN] s3 failed for some members (house={house} date={d})")
                    failed.append((house, d))
                    continue
            else:
                print("[s4_only] skipping s1/s2/s3; reusing existing timelines")

            with ThreadPoolExecutor(max_workers=workers) as ex:
                results = list(ex.map(
                    lambda m: s4_appliance_decision.run_step(
                        world_id, m, d, env, policy_text=day_policy_text, policy_tag=day_policy_tag,
                        house=house, world_news=s4_news, weather_override=weather_effect),
                    targets))
            if any(not r[0] for r in results):
                print(f"[WARN] s4 failed for some members (house={house} date={d})")
                failed.append((house, d))
                continue

            print(f"[Done] world={world_id} house={house} date={d} ({len(targets)} members)")

    if failed:
        print(f"\n########## SIMULATE FINISHED WITH {len(failed)} FAILURE(S) ##########")
        for house, d in failed:
            print(f"  [FAILED] house={house} date={d or '(setup)'}")
        return 1
    print(f"\n########## SIMULATE DONE ({len(house_list)} houses x {len(dates)} days) ##########")
    return 0


def main():
    parser = argparse.ArgumentParser(description="LLMWorld single entry")
    parser.add_argument("--mode", choices=["world", "simulate"], required=True)
    parser.add_argument("--world", default=None, help="world ID (auto if omitted)")
    parser.add_argument("--world-config", default=None, help="world config name under import/world/ (default Melbourne)")
    parser.add_argument("--count", type=int, default=1, help="world: number of household types")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    parser.add_argument("--date", default=None, help="simulate: start date")
    parser.add_argument("--days", type=int, default=1, help="simulate: number of consecutive days (default: 1)")
    parser.add_argument("--house", default=None, help="simulate: house id or comma-separated list (default: all houses)")
    parser.add_argument("--env", default=None, help="simulate: env id (default world id)")
    parser.add_argument("--workers", type=int, default=4, help="simulate: thread count")
    parser.add_argument("--member", default=None, help="simulate: only this member (name or index)")
    parser.add_argument("--policy", default=None, help="simulate: policy to inject (tou | tou_soft | tou:<peak>,<valley>[,<shoulder>])")
    parser.add_argument("--policy-schedule", action="append", default=None, help="simulate: 'start,end,policy' timeline entry (repeatable; empty end = open)")
    parser.add_argument("--s4-only", action="store_true", help="simulate: skip s1-s3, re-run appliance decisions only (policy comparison runs)")
    parser.add_argument("--event", action="append", default=None, help="simulate: custom event 'date|title|content' (repeatable)")
    parser.add_argument("--event-template", action="append", default=None, help="simulate: preset event 'date|template' (repeatable)")
    parser.add_argument("--community-notice", action="append", default=None, help="simulate: community notice 'date|title|content' (repeatable)")
    parser.add_argument("--temperature", type=float, default=None, help="override sampling temperature (used when thinking is off)")
    parser.add_argument("--no-thinking", action="store_true", help="disable model thinking/reasoning mode")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default=None, help="override reasoning effort")
    parser.add_argument("--peer-nudge", action="store_true", help="simulate: inject neighbour-comparison social nudge from the previous day's community mean")
    args = parser.parse_args()

    applied = apply_sampling_overrides(args.temperature, False if args.no_thinking else None,
                                       args.reasoning_effort)
    if applied:
        print(f"[Sampling] overrides: {applied}")

    world_id = args.world or auto_world_id()
    if args.mode == "world":
        return run_world(world_id, args.count, args.seed, args.workers, args.world_config)
    try:
        events = news.parse_events(args.event, args.event_template)
        notices = [news.parse_event_spec(spec) for spec in (args.community_notice or []) if spec]
        policy_schedule = engine_policy.parse_policy_schedule(args.policy_schedule)
    except ValueError as exc:
        print(f"[Abort] {exc}")
        return 1
    return run_simulate(world_id, args.date, args.env, args.workers, args.member,
                        args.policy, args.s4_only, args.house, args.days, events, notices,
                        policy_schedule, args.peer_nudge)


if __name__ == "__main__":
    sys.exit(main())
