import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
import numpy as np
from datetime import datetime, timedelta

class Visualizer:
    def __init__(self, planner):
        self.planner = planner
        self.colors = {}
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#AAB7B8',
            '#52BE80', '#EC7063', '#AF7AC5', '#5DADE2', '#48C9B0',
            '#F4D03F', '#EB984E', '#DC7633', '#A569BD', '#5499C7'
        ]
        self.color_index = 0
    
    def _get_color_for_activity(self, activity):
        if activity not in self.colors:
            self.colors[activity] = self.color_palette[self.color_index % len(self.color_palette)]
            self.color_index += 1
        return self.colors[activity]
    
    def _time_to_minutes(self, time_str):
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    
    def _parse_time_range(self, time_range):
        start, end = time_range.split('-')
        start_min = self._time_to_minutes(start)
        end_min = self._time_to_minutes(end)
        
        if end_min <= start_min:
            end_min += 1440
        
        return start_min, end_min
    
    def visualize_macro_plans(self, output_path=None):
        if not self.planner.macro_plans:
            print("没有宏观计划数据")
            return
        
        self.colors = {}
        self.color_index = 0
        
        members = list(self.planner.macro_plans.keys())
        num_members = len(members)
        
        fig, ax = plt.subplots(figsize=(30, num_members * 2))
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        for idx, member in enumerate(members):
            plan = self.planner.macro_plans[member]
            activities = plan.get('activities', [])
            
            y_pos = num_members - idx - 1
            
            for activity in activities:
                time_range = activity['time']
                activity_desc = activity['activity']
                location = activity.get('location', '')
                
                start_min, end_min = self._parse_time_range(time_range)
                duration = end_min - start_min
                
                color = self._get_color_for_activity(activity_desc)
                
                bar = ax.barh(y_pos, duration, left=start_min, height=0.8, 
                             color=color, edgecolor='white', linewidth=1)
                
                if location:
                    label_text = f"{location}\n{activity_desc}"
                else:
                    label_text = activity_desc
                
                if duration >= 10:
                    ax.text(start_min + duration/2, y_pos, label_text,
                           ha='center', va='center', fontsize=6, 
                           color='white', weight='bold')
                elif duration >= 5:
                    short_label = activity_desc[:3] if len(activity_desc) > 3 else activity_desc
                    ax.text(start_min + duration/2, y_pos, short_label,
                           ha='center', va='center', fontsize=5, 
                           color='white', weight='bold', rotation=90)
                elif duration >= 1:
                    short_label = activity_desc[0]
                    ax.text(start_min + duration/2, y_pos, short_label,
                           ha='center', va='center', fontsize=4, 
                           color='white', weight='bold')
        
        ax.set_yticks(range(num_members))
        ax.set_yticklabels([members[num_members - i - 1] for i in range(num_members)], fontsize=12)
        
        ax.set_xlim(0, 1440)
        ax.set_xticks(range(0, 1441, 60))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(25)], fontsize=10)
        
        ax.set_xlabel('时间', fontsize=14, weight='bold')
        ax.set_ylabel('家庭成员', fontsize=14, weight='bold')
        ax.set_title('家庭成员一天行程安排', fontsize=18, weight='bold', pad=20)
        
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"可视化图表已保存: {output_path}")
        else:
            output_path = f"{self.planner.log_dir}/宏观计划可视化.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"可视化图表已保存: {output_path}")
        
        plt.close()
    
    def visualize_decomposed_plans(self, output_path=None):
        if not self.planner.decomposed_plans:
            print("没有分解计划数据")
            return
        
        self.colors = {}
        self.color_index = 0
        
        members = list(self.planner.decomposed_plans.keys())
        num_members = len(members)
        
        fig, ax = plt.subplots(figsize=(30, num_members * 2))
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        for idx, member in enumerate(members):
            plan = self.planner.decomposed_plans[member]
            activities = plan.get('activities', [])
            
            y_pos = num_members - idx - 1
            
            for activity in activities:
                time_range = activity['time']
                activity_desc = activity['activity']
                location = activity.get('location', '')
                
                start_min, end_min = self._parse_time_range(time_range)
                duration = end_min - start_min
                
                color = self._get_color_for_activity(activity_desc)
                
                bar = ax.barh(y_pos, duration, left=start_min, height=0.8, 
                             color=color, edgecolor='white', linewidth=1)
                
                if location:
                    label_text = f"{location}\n{activity_desc}"
                else:
                    label_text = activity_desc
                
                if duration >= 10:
                    ax.text(start_min + duration/2, y_pos, label_text,
                           ha='center', va='center', fontsize=6, 
                           color='white', weight='bold')
                elif duration >= 5:
                    short_label = activity_desc[:3] if len(activity_desc) > 3 else activity_desc
                    ax.text(start_min + duration/2, y_pos, short_label,
                           ha='center', va='center', fontsize=5, 
                           color='white', weight='bold', rotation=90)
                elif duration >= 1:
                    short_label = activity_desc[0]
                    ax.text(start_min + duration/2, y_pos, short_label,
                           ha='center', va='center', fontsize=4, 
                           color='white', weight='bold')
        
        ax.set_yticks(range(num_members))
        ax.set_yticklabels([members[num_members - i - 1] for i in range(num_members)], fontsize=12)
        
        ax.set_xlim(0, 1440)
        ax.set_xticks(range(0, 1441, 60))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(25)], fontsize=10)
        
        ax.set_xlabel('时间', fontsize=14, weight='bold')
        ax.set_ylabel('家庭成员', fontsize=14, weight='bold')
        ax.set_title('家庭成员分解计划（含互动）', fontsize=18, weight='bold', pad=20)
        
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"分解计划可视化图表已保存: {output_path}")
        else:
            output_path = f"{self.planner.log_dir}/分解计划可视化.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"分解计划可视化图表已保存: {output_path}")
        
        plt.close()
