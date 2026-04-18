import json
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

class TimeSlot:
    def __init__(self, start_minutes, end_minutes, location, activity):
        self.start = start_minutes
        self.end = end_minutes
        self.location = location
        self.activity = activity
    
    def overlaps(self, other_start, other_end):
        return not (self.end <= other_start or self.start >= other_end)
    
    def to_dict(self):
        return {
            "time": self._format_time_range(),
            "location": self.location,
            "activity": self.activity
        }
    
    def _format_time_range(self):
        start_hour = self.start // 60
        start_min = self.start % 60
        end_hour = self.end // 60
        end_min = self.end % 60
        return f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}"

class Timeline:
    def __init__(self, member_name):
        self.member_name = member_name
        self.slots = []
        self.colors = {}
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#AAB7B8',
            '#52BE80', '#EC7063', '#AF7AC5', '#5DADE2', '#48C9B0',
            '#F4D03F', '#EB984E', '#DC7633', '#A569BD', '#5499C7'
        ]
        self.color_index = 0
    
    def _parse_time(self, time_str):
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    
    def _parse_time_range(self, time_range):
        start, end = time_range.split('-')
        start_min = self._parse_time(start.strip())
        end_min = self._parse_time(end.strip())
        if end_min <= start_min:
            end_min += 1440
        return start_min, end_min
    
    def load_from_activities(self, activities):
        self.slots = []
        for activity in activities:
            time_range = activity['time']
            location = activity.get('location', '')
            activity_desc = activity['activity']
            
            start_min, end_min = self._parse_time_range(time_range)
            slot = TimeSlot(start_min, end_min, location, activity_desc)
            self.slots.append(slot)
        
        self.slots.sort(key=lambda s: s.start)
    
    def insert_slot(self, time_range, location, activity, force=True):
        start_min, end_min = self._parse_time_range(time_range)
        
        if force:
            self._remove_overlapping_slots(start_min, end_min)
        
        new_slot = TimeSlot(start_min, end_min, location, activity)
        self.slots.append(new_slot)
        self.slots.sort(key=lambda s: s.start)
    
    def update_slot(self, time_range, location, activity):
        start_min, end_min = self._parse_time_range(time_range)
        self._remove_overlapping_slots(start_min, end_min)
        new_slot = TimeSlot(start_min, end_min, location, activity)
        self.slots.append(new_slot)
        self.slots.sort(key=lambda s: s.start)
    
    def _remove_overlapping_slots(self, start_min, end_min):
        new_slots = []
        for slot in self.slots:
            if not slot.overlaps(start_min, end_min):
                new_slots.append(slot)
            else:
                if slot.start < start_min:
                    new_slots.append(TimeSlot(slot.start, start_min, slot.location, slot.activity))
                if slot.end > end_min:
                    new_slots.append(TimeSlot(end_min, slot.end, slot.location, slot.activity))
        
        self.slots = new_slots
    
    def get_empty_slots(self):
        if not self.slots:
            return [(0, 1440)]
        
        empty_slots = []
        self.slots.sort(key=lambda s: s.start)
        
        if self.slots[0].start > 0:
            empty_slots.append((0, self.slots[0].start))
        
        for i in range(len(self.slots) - 1):
            gap_start = self.slots[i].end
            gap_end = self.slots[i + 1].start
            if gap_end > gap_start:
                empty_slots.append((gap_start, gap_end))
        
        if self.slots[-1].end < 1440:
            empty_slots.append((self.slots[-1].end, 1440))
        
        return empty_slots
    
    def get_empty_slots_formatted(self):
        empty_slots = self.get_empty_slots()
        formatted = []
        for start, end in empty_slots:
            start_hour = start // 60
            start_min = start % 60
            end_hour = end // 60
            end_min = end % 60
            formatted.append(f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}")
        return formatted
    
    def to_json(self):
        activities = [slot.to_dict() for slot in self.slots]
        return json.dumps({
            "member": self.member_name,
            "activities": activities
        }, ensure_ascii=False, indent=2)
    
    def to_dict(self):
        return {
            "member": self.member_name,
            "activities": [slot.to_dict() for slot in self.slots]
        }
    
    def _get_color_for_activity(self, activity):
        if activity not in self.colors:
            self.colors[activity] = self.color_palette[self.color_index % len(self.color_palette)]
            self.color_index += 1
        return self.colors[activity]
    
    def visualize(self, ax, y_pos):
        for slot in self.slots:
            duration = slot.end - slot.start
            color = self._get_color_for_activity(slot.activity)
            
            ax.barh(y_pos, duration, left=slot.start, height=0.8, 
                   color=color, edgecolor='white', linewidth=1)
            
            if slot.location:
                label_text = f"{slot.location}\n{slot.activity}"
            else:
                label_text = slot.activity
            
            if duration >= 10:
                ax.text(slot.start + duration/2, y_pos, label_text,
                       ha='center', va='center', fontsize=6, 
                       color='white', weight='bold')
            elif duration >= 5:
                short_label = slot.activity[:3] if len(slot.activity) > 3 else slot.activity
                ax.text(slot.start + duration/2, y_pos, short_label,
                       ha='center', va='center', fontsize=5, 
                       color='white', weight='bold', rotation=90)
            elif duration >= 1:
                short_label = slot.activity[0]
                ax.text(slot.start + duration/2, y_pos, short_label,
                       ha='center', va='center', fontsize=4, 
                       color='white', weight='bold')

def visualize_timelines(timelines, output_path, title="家庭成员时间线"):
    num_members = len(timelines)
    fig, ax = plt.subplots(figsize=(30, num_members * 2))
    
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    member_names = [t.member_name for t in timelines]
    
    for idx, timeline in enumerate(timelines):
        y_pos = num_members - idx - 1
        timeline.visualize(ax, y_pos)
    
    ax.set_yticks(range(num_members))
    ax.set_yticklabels([member_names[num_members - i - 1] for i in range(num_members)], fontsize=12)
    
    ax.set_xlim(0, 1440)
    ax.set_xticks(range(0, 1441, 60))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(25)], fontsize=10)
    
    ax.set_xlabel('时间', fontsize=14, weight='bold')
    ax.set_ylabel('家庭成员', fontsize=14, weight='bold')
    ax.set_title(title, fontsize=18, weight='bold', pad=20)
    
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"可视化图表已保存: {output_path}")
    plt.close()
