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
    path = os.path.join(project_root, "worlds", world_id, "state.json")
    if not os.path.exists(path):
        return None
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
    for fmt in ("%Y年%m月%d日", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {date_str}")


def validate_start_date(world_id, date_str):
    last_date = get_world_last_date(world_id)
    requested = parse_world_date(date_str) if date_str else None
    if last_date:
        last = datetime.strptime(last_date, "%Y年%m月%d日")
        expected = (last + timedelta(days=1)).strftime("%Y年%m月%d日")
        if requested is None:
            return expected
        if requested.strftime("%Y年%m月%d日") == expected:
            return requested.strftime("%Y年%m月%d日")
        raise ValueError(
            f"世界 {world_id} 已模拟至 {last_date}，只能继续模拟："
            f"日期须留空（自动续跑）或等于 {expected}（下一天）。"
            f"不允许覆盖/回退/跳日；想重新开始请使用新的世界 ID")
    return requested.strftime("%Y年%m月%d日") if requested else None


class World:
    def __init__(self, home, world_id=None, postcode=None, house_id=None, start_date=None):
        self.home = home
        self.world_id = world_id
        self.postcode = postcode
        self.house_id = house_id


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
            d = datetime.strptime(last_date, "%Y年%m月%d日") + timedelta(days=1)
            return d.strftime("%Y年%m月%d日")
        except Exception as e:
            print(f"[状态] 读取世界状态失败（将从默认日期开始）: {e}")
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

    def simulate_day(self, season="夏天", weather="晴天", temperature=28, verbose=True,
                     policy_context="", policy_name="baseline", community_notice=""):
        if verbose:
            print(f"\n{'='*60}")
            print(f"开始模拟：{self.time.get_full_date_string()}")
            print(f"{'='*60}\n")
        
        date_str = self.time.date.strftime('%Y%m%d')

        date_iso = self.time.date.strftime('%Y-%m-%d')
        new_news = self.news.get_new_for(date_iso)
        news_text = self.news.render_items(new_news)
        self._news_delivered = new_news
        planner = Planner(self.home, world_id=self.world_id, postcode=self.postcode, 
                         house_id=self.house_id, date_str=date_str,
                         memory_context=self.memory.get_prompt_context(),
                         policy_name=policy_name,
                         news_context=news_text)
        self.current_planner = planner        
        if verbose:
            print("第一步：生成宏观计划...")
        planner.generate_plans(self.time, community_notice=community_notice)
        
        if verbose:
            print("第二步：渐进式协调生成完整时间线...")
        planner.coordinate_timelines_progressively()
        
        if verbose:
            print("第三步：丰富行为描述...")
        planner.enrich_activities(season=season, weather=weather, temperature=temperature)
        
        if verbose:
            print("第四步：执行用电模拟...")
        executor = Executor(self.home, planner, policy_context=policy_context,
                            news_context=news_text)
        self.current_executor = executor
        executor.execute_all_segments(season=season, weather=weather, temperature=temperature)
        
        if verbose:
            print("第五步：计算用电信息...")
        energy_calculator = EnergyCalculator(self.home, planner.log_dir)
        energy_calculator.calculate_all_energy()
        energy_summary = energy_calculator.get_summary()
        
        if verbose:
            print(f"第五步完成：总用电量 {energy_summary['total_energy_kwh']} kWh")
            print(f"用电信息已保存到：{energy_calculator.energy_info_dir}")
        
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
            print(f"\n{self.time.get_full_date_string()} 模拟完成！")
            print(f"日志目录：{planner.log_dir}\n")
        
        return day_result
    
    def simulate_days(self, num_days, season="夏天", weather="晴天", temperature=28, verbose=True):
        results = []
        
        for day in range(num_days):
            if verbose:
                print(f"\n{'#'*60}")
                print(f"第 {day + 1}/{num_days} 天")
                print(f"{'#'*60}")
            
            result = self.simulate_day(season=season, weather=weather, temperature=temperature, verbose=verbose)
            results.append(result)
            
            if day < num_days - 1:
                self.time.next_day()
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"完成 {num_days} 天模拟")
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
        print("\n模拟统计：")
        print(f"  世界ID：{self.world_id}")
        print(f"  总天数：{len(self.history)}")
        
        tokens = self.get_total_tokens()
        print(f"\nToken 使用统计：")
        print(f"  未命中缓存 Token: {tokens['prompt_cache_miss']}")
        print(f"  命中缓存 Token: {tokens['prompt_cache_hit']}")
        print(f"  输出 Token: {tokens['completion']}")
        print(f"  总计: {tokens['total']}")
        
        print(f"\n模拟日期列表：")
        for i, day in enumerate(self.history, 1):
            print(f"  {i}. {day['date']} ({day['day_type']}) - {day['log_dir']}")
    
    def print_summary(self):
        self._print_summary()
