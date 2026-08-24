from .home import Home
from .planner import Planner
from .executor import Executor
from .energy_calculator import EnergyCalculator
from .subagent import SubAgent
from .environment import Time
from .memory import HouseholdMemory
from .news import NewsBoard
import random
import os
import json
from datetime import datetime, timedelta

import config


def get_world_last_date(world_id):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    world_dir = os.path.join(project_root, "worlds", world_id)
    path = os.path.join(world_dir, "state.json")
    if not os.path.exists(path):
        # Parallel households: take the max date from state_<house>.json
        dates = []
        for name in sorted(os.listdir(world_dir)) if os.path.isdir(world_dir) else []:
            if name.startswith("state_") and name.endswith(".json"):
                try:
                    with open(os.path.join(world_dir, name), "r", encoding="utf-8") as f:
                        d = json.load(f).get("date")
                    if d:
                        dates.append(d)
                except Exception:
                    continue
        return max(dates) if dates else None
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("date") or None
    except Exception:
        return None


def parse_world_date(date_str):
    if not date_str:
        return None
    text = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def validate_start_date(world_id, date_str):
    last_date = get_world_last_date(world_id)
    requested = parse_world_date(date_str) if date_str else None
    if last_date:
        last = datetime.strptime(last_date, "%Y-%m-%d")
        expected = (last + timedelta(days=1)).strftime("%Y-%m-%d")
        if requested is None:
            return expected
        if requested.strftime("%Y-%m-%d") == expected:
            return requested.strftime("%Y-%m-%d")
        raise ValueError(
            f"World {world_id} already simulated until {last_date}; can only continue from there: "
            f"date must be left empty (auto-resume) or equal to {expected} (the next day). "
            f"Overwriting/rolling back/skipping days is not allowed; to restart, use a new world ID")
    return requested.strftime("%Y-%m-%d") if requested else None


class World:
    def __init__(self, home, world_id=None, postcode=None, house_id=None, start_date=None,
                 env_id=None):
        self.home = home
        self.world_id = world_id
        self.postcode = postcode
        self.house_id = house_id
        self.env_id = env_id  # simulation environment id (simulation/<world>_<time>/), None=legacy structure


        if start_date:
            self.time = Time(start_date)
        else:
            self.time = Time(self._resume_date() or config.DEFAULT_START_DATE)
        self.history = []
        self.current_planner = None
        self.current_executor = None
        self.memory = HouseholdMemory()
        self.memory.load_days(self._load_memory_days())
        self.news = self._load_news_board()

        self._restore_news_state()



    def _state_path(self):
        if not self.world_id:
            return None
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if self.house_id:
            # Parallel households: isolate per-house so concurrent runs do not overwrite the same state.json
            return os.path.join(project_root, "worlds", self.world_id,
                                f"state_{self.house_id}.json")
        return os.path.join(project_root, "worlds", self.world_id, "state.json")

    def _resume_date(self):

        path = self._state_path()
        if not path or not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            last_date = state.get("date")
            if not last_date:
                return None
            d = datetime.strptime(last_date, "%Y-%m-%d") + timedelta(days=1)
            return d.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"[status] Failed to read world state (will start from the default date): {e}")
            return None

    def _load_memory_days(self):

        path = self._state_path()
        if not path or not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            days = state.get("memory_days", [])

            if isinstance(days, dict):
                return days.get(self.house_id, [])
            return days if isinstance(days, list) else []
        except Exception:
            return []

    def _restore_news_state(self):

        path = self._state_path()
        if not path or not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            delivery = state.get("news_delivery")
            if isinstance(delivery, dict):
                self.news.restore_state(delivery)
            news_memory = state.get("news_memory")
            if isinstance(news_memory, dict):
                self.memory.load_news_memory(news_memory.get(self.house_id, []))
        except Exception:
            pass

    def save_state(self):





        path = self._state_path()
        if not path:
            return
        state = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                state = {}

        memory = state.get("memory_days")
        if not isinstance(memory, dict):
            memory = {}
        memory[self.house_id] = self.memory.days
        state["date"] = self.time.get_date_string()
        state["memory_days"] = memory


        news_memory = state.get("news_memory")
        if not isinstance(news_memory, dict):
            news_memory = {}
        news_memory[self.house_id] = self.memory.get_news_memory_state()
        state["news_memory"] = news_memory
        state["news_delivery"] = self.news.to_state()

        os.makedirs(os.path.dirname(path), exist_ok=True)

        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)



    def _load_news_board(self):

        if not self.world_id:
            return NewsBoard()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        events_file = os.path.join(project_root, "worlds", self.world_id, "events.json")
        return NewsBoard(events_file)

    def add_world_event(self, news_item):

        self.news.add_event(news_item)
        return self

    def simulate_day(self, season="Summer", weather="Sunny", temperature=28, verbose=True,
                     policy_context="", policy_name="baseline", community_notice=""):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Starting simulation: {self.time.get_full_date_string()}")
            print(f"{'='*60}\n")
        
        date_iso = self.time.date.strftime('%Y-%m-%d')
        new_news = self.news.get_new_for(date_iso)
        news_text = self.news.render_items(new_news)
        self._news_delivered = new_news
        planner = Planner(self.home, world_id=self.world_id, postcode=self.postcode, 
                         house_id=self.house_id, date_str=date_iso,
                         memory_context=self.memory.get_prompt_context(),
                         policy_name=policy_name,
                         news_context=news_text, env_id=self.env_id)
        self.current_planner = planner        
        if verbose:
            print("Step 1: Generating macro plan...")
        planner.generate_plans(self.time, community_notice=community_notice)
        
        if verbose:
            print("Step 2: Progressively coordinating the full timeline...")
        planner.coordinate_timelines_progressively()
        
        if verbose:
            print("Step 3: Enriching activity descriptions...")
        planner.enrich_activities(season=season, weather=weather, temperature=temperature)
        
        if verbose:
            print("Step 4: Running electricity simulation...")
        executor = Executor(self.home, planner, policy_context=policy_context,
                            news_context=news_text)
        self.current_executor = executor
        executor.execute_all_segments(season=season, weather=weather, temperature=temperature)
        
        if verbose:
            print("Step 5: Calculating electricity usage...")
        energy_calculator = EnergyCalculator(self.home, planner.log_dir)
        energy_calculator.calculate_all_energy()
        energy_summary = energy_calculator.get_summary()
        
        if verbose:
            print(f"Step 5 complete: total electricity {energy_summary['total_energy_kwh']} kWh")
            print(f"Electricity info saved to: {energy_calculator.energy_info_dir}")
        
        day_result = {
            "date": self.time.get_date_string(),
            "day_type": self.time.day_type,
            "time_context": self.time.get_context_info(),
            "season": season,
            "weather": weather,
            "temperature": temperature,
            "log_dir": planner.log_dir,
            "planner": planner,
            "executor": executor,
            "energy_calculator": energy_calculator,
            "energy_summary": energy_summary
        }
        
        self.history.append(day_result)


        self.memory.update_from_day(day_result)

        if getattr(self, "_news_delivered", None):
            self.memory.add_news(self._news_delivered)
            self._news_delivered = None
        self.save_state()

        if verbose:
            print(f"\n{self.time.get_full_date_string()} simulation complete!")
            print(f"Log directory: {planner.log_dir}\n")
        
        return day_result
    
    def simulate_days(self, num_days, season="Summer", weather="Sunny", temperature=28, verbose=True):
        results = []
        
        for day in range(num_days):
            if verbose:
                print(f"\n{'#'*60}")
                print(f"Day {day + 1}/{num_days}")
                print(f"{'#'*60}")
            
            result = self.simulate_day(season=season, weather=weather, temperature=temperature, verbose=verbose)
            results.append(result)
            
            if day < num_days - 1:
                self.time.next_day()
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Completed simulation of {num_days} days")
            print(f"{'='*60}")
            self._print_summary()
        
        return results
    
    def next_day(self):
        self.time.next_day()
        return self
    
    def prev_day(self):
        self.time.prev_day()
        return self
    
    def set_date(self, date_str):
        self.time = Time(date_str)
        return self
    
    def add_holiday(self, date_str, holiday_name, description=""):
        self.time.add_holiday(date_str, holiday_name, description)
        return self
    
    def add_special_event(self, date_str, event_name, description=""):
        self.time.add_special_event(date_str, event_name, description)
        return self
    
    def get_history(self):
        return self.history
    
    def get_total_tokens(self):
        miss, hit, output = SubAgent.get_tokens()
        return {
            "prompt_cache_miss": miss,
            "prompt_cache_hit": hit,
            "completion": output,
            "total": miss + hit + output
        }
    
    def reset_tokens(self):
        SubAgent.reset_tokens()
    
    def _print_summary(self):
        print("\nSimulation statistics:")
        print(f"  World ID: {self.world_id}")
        print(f"  Total days: {len(self.history)}")
        
        tokens = self.get_total_tokens()
        print(f"\nToken usage statistics:")
        print(f"  Cache miss tokens: {tokens['prompt_cache_miss']}")
        print(f"  Cache hit tokens: {tokens['prompt_cache_hit']}")
        print(f"  Output tokens: {tokens['completion']}")
        print(f"  Total: {tokens['total']}")
        
        print(f"\nSimulated dates:")
        for i, day in enumerate(self.history, 1):
            print(f"  {i}. {day['date']} ({day['day_type']}) - {day['log_dir']}")
    
    def print_summary(self):
        self._print_summary()
