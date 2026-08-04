from .home import Home
from .planner import Planner
from .executor import Executor
from .energy_calculator import EnergyCalculator
from .subagent import SubAgent
from .environment import Time
from .memory import HouseholdMemory
import random
from datetime import datetime

class World:
    def __init__(self, home, world_id=None, postcode=None, house_id=None, start_date=None):
        self.home = home
        self.time = Time(start_date) if start_date else Time()
        self.history = []
        self.current_planner = None
        self.current_executor = None
        self.world_id = world_id
        self.postcode = postcode
        self.house_id = house_id
        self.memory = HouseholdMemory()   # 跨天记忆：昨天的行为影响今天的计划
    
    def simulate_day(self, season="夏天", weather="晴天", temperature=28, verbose=True,
                     policy_context=""):
        if verbose:
            print(f"\n{'='*60}")
            print(f"开始模拟：{self.time.get_full_date_string()}")
            print(f"{'='*60}\n")
        
        date_str = self.time.date.strftime('%Y%m%d')
        planner = Planner(self.home, world_id=self.world_id, postcode=self.postcode, 
                         house_id=self.house_id, date_str=date_str,
                         memory_context=self.memory.get_prompt_context())
        self.current_planner = planner
        
        if verbose:
            print("第一步：生成宏观计划...")
        planner.generate_plans(self.time)
        
        if verbose:
            print("第二步：渐进式协调生成完整时间线...")
        planner.coordinate_timelines_progressively()
        
        if verbose:
            print("第三步：丰富行为描述...")
        planner.enrich_activities(season=season, weather=weather, temperature=temperature)
        
        if verbose:
            print("第四步：执行用电模拟...")
        executor = Executor(self.home, planner, policy_context=policy_context)
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

        # 每天结束后更新跨天记忆（昨天的行为 → 明天的上下文）
        self.memory.update_from_day(day_result)

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
