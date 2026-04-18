import json
import os
from datetime import datetime

POWER_MAP = {
    "电视": 150,
    "空调": 2000,
    "吸尘器": 1000,
    "灯": 40,
    "冰箱": 100,
    "电饭煲": 500,
    "微波炉": 1000,
    "电磁炉": 2000,
    "油烟机": 200,
    "台灯": 15,
    "手机充电器": 10,
    "电脑": 200,
    "热水器": 2000,
    "洗衣机": 500
}

class Recorder:
    def __init__(self, home, log_dir=None):
        self.home = home
        self.log_dir = log_dir
    
    def calculate_energy_from_status(self):
        appliance_energy = {}
        appliance_timeline = {}
        
        for room_name, room in self.home.rooms.items():
            for appliance in room.appliances:
                on_count = sum(appliance.status)
                power = POWER_MAP.get(appliance.name, 0)
                energy_kwh = (power * on_count * 10 / 60) / 1000
                
                key = f"{room_name}-{appliance.name}"
                appliance_energy[key] = {
                    "room": room_name,
                    "appliance": appliance.name,
                    "power": power,
                    "on_slots": on_count,
                    "total_minutes": on_count * 10,
                    "energy_kwh": round(energy_kwh, 3)
                }
                
                appliance_timeline[key] = appliance.status.copy()
        
        return appliance_energy, appliance_timeline
    
    def calculate_statistics(self):
        appliance_energy, _ = self.calculate_energy_from_status()
        
        total_energy = sum(item["energy_kwh"] for item in appliance_energy.values())
        
        by_room = {}
        by_appliance_type = {}
        
        for key, data in appliance_energy.items():
            room = data["room"]
            appliance = data["appliance"]
            energy = data["energy_kwh"]
            
            by_room[room] = by_room.get(room, 0) + energy
            by_appliance_type[appliance] = by_appliance_type.get(appliance, 0) + energy
        
        return {
            "total_energy": round(total_energy, 2),
            "by_room": {k: round(v, 2) for k, v in by_room.items()},
            "by_appliance": {k: round(v, 2) for k, v in by_appliance_type.items()},
            "details": appliance_energy
        }
    
    def generate_timeline_report(self):
        _, appliance_timeline = self.calculate_energy_from_status()
        
        timeline_report = []
        for key, status_list in appliance_timeline.items():
            room, appliance = key.split("-", 1)
            
            segments = []
            start_slot = None
            
            for slot in range(144):
                if status_list[slot]:
                    if start_slot is None:
                        start_slot = slot
                else:
                    if start_slot is not None:
                        segments.append((start_slot, slot - 1))
                        start_slot = None
            
            if start_slot is not None:
                segments.append((start_slot, 143))
            
            time_ranges = []
            for start, end in segments:
                start_hour = start // 6
                start_min = (start % 6) * 10
                end_hour = end // 6
                end_min = (end % 6) * 10 + 10
                
                if end_min == 60:
                    end_hour += 1
                    end_min = 0
                
                time_ranges.append(f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}")
            
            timeline_report.append({
                "room": room,
                "appliance": appliance,
                "time_ranges": time_ranges
            })
        
        return timeline_report
    
    def save_report(self, date, output_name="用电报告"):
        if self.log_dir:
            filepath = os.path.join(self.log_dir, f"{output_name}.md")
        else:
            os.makedirs("output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_name}_{timestamp}.md"
            filepath = os.path.join("output", filename)
        
        stats = self.calculate_statistics()
        timeline = self.generate_timeline_report()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {output_name}\n\n")
            f.write(f"日期: {date}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write(f"## 总用电量\n\n")
            f.write(f"**{stats['total_energy']} 度**\n\n")
            
            f.write(f"## 按房间统计\n\n")
            for room, energy in stats['by_room'].items():
                f.write(f"- {room}: {energy} 度\n")
            f.write("\n")
            
            f.write(f"## 按家电类型统计\n\n")
            for appliance, energy in stats['by_appliance'].items():
                f.write(f"- {appliance}: {energy} 度\n")
            f.write("\n")
            
            f.write(f"## 详细用电情况\n\n")
            for key, data in stats['details'].items():
                f.write(f"### {data['room']} - {data['appliance']}\n\n")
                f.write(f"- 功率: {data['power']}瓦\n")
                f.write(f"- 开启时长: {data['total_minutes']}分钟\n")
                f.write(f"- 用电量: {data['energy_kwh']}度\n\n")
            
            f.write(f"## 电器开关时间线\n\n")
            for item in timeline:
                f.write(f"### {item['room']} - {item['appliance']}\n\n")
                if item['time_ranges']:
                    for time_range in item['time_ranges']:
                        f.write(f"- {time_range}\n")
                else:
                    f.write("- 全天关闭\n")
                f.write("\n")
        
        print(f"报告已保存到: {filepath}")
        return filepath
    
    def save_json(self, date, output_name="用电数据"):
        if self.log_dir:
            filepath = os.path.join(self.log_dir, f"{output_name}.json")
        else:
            os.makedirs("output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_name}_{timestamp}.json"
            filepath = os.path.join("output", filename)
        
        stats = self.calculate_statistics()
        timeline = self.generate_timeline_report()
        
        data = {
            "date": date,
            "statistics": stats,
            "timeline": timeline
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filepath}")
        return filepath
