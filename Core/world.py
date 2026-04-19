from .environment import Home
from .planner import Planner
from .executor import Executor
from .subagent import SubAgent
from .time import Time
import random

class World:
    def __init__(self, home, start_date=None, day_type=None):
        self.home = home
        self.time = Time(start_date, day_type) if start_date else Time()
        self.history = []
        self.current_planner = None
        self.current_executor = None
        self.run_id = self._generate_run_id()
    
    def _generate_run_id(self):
        return str(random.randint(100000, 999999))
    
    def simulate_day(self, season="夏天", weather="晴天", temperature=28, verbose=True):
        if verbose:
            print(f"\n{'='*60}")
            print(f"开始模拟：{self.time.get_full_date_string()}")
            print(f"{'='*60}\n")
        
        date_str = self.time.date.strftime('%Y%m%d')
        planner = Planner(self.home, run_id=self.run_id, date_str=date_str)
        self.current_planner = planner
        
        if verbose:
            print("第一步：生成宏观计划...")
        planner.generate_plans(self.time)
        
        if verbose:
            print("第一步完成：生成宏观计划可视化图表...")
        planner.visualize_plans("宏观计划")
        
        if verbose:
            print("第二步：识别协调场景...")
        planner.analyze_interactions()
        
        if verbose:
            print("第三步：代码强制插入协调时间段...")
        planner.adjust_timelines()
        
        if verbose:
            print("第四步：填充空余时间段...")
        planner.fill_empty_slots()
        
        if verbose:
            print("第五步：验证协调...")
        needs_readjust = planner.verify_coordinations()
        
        if needs_readjust:
            if verbose:
                print("发现协调问题，再次调整...")
            planner.adjust_timelines()
            planner.fill_empty_slots()
        
        if verbose:
            print("\n第六步：保存最终计划...")
        planner.save_final_plans()
        
        if verbose:
            print("第六步完成：生成最终计划可视化图表...")
        planner.visualize_plans("最终计划")
        
        if verbose:
            print("第七步：分解时间段...")
        planner.decompose_to_segments()
        
        if verbose:
            print("第八步：丰富行为描述...")
        planner.enrich_activities(season=season, weather=weather, temperature=temperature)
        
        if verbose:
            print("第九步：执行用电模拟...")
        executor = Executor(self.home, planner)
        self.current_executor = executor
        executor.execute_all_segments(season=season, weather=weather, temperature=temperature)
        
        day_result = {
            "date": self.time.get_date_string(),
            "day_type": self.time.day_type,
            "time_context": self.time.get_context_info(),
            "season": season,
            "weather": weather,
            "temperature": temperature,
            "log_dir": planner.log_dir,
            "planner": planner,
            "executor": executor
        }
        
        self.history.append(day_result)
        
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
    
    def set_date(self, date_str, day_type=None):
        self.time = Time(date_str, day_type)
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
        print(f"  运行ID：{self.run_id}")
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
