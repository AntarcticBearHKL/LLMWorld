from datetime import datetime, timedelta
import json

class Time:
    def __init__(self, date_str=None, day_type=None):
        if date_str:
            self.date = datetime.strptime(date_str, "%Y年%m月%d日")
        else:
            self.date = datetime.now()
        
        self.day_type = day_type or self._auto_detect_day_type()
        
        self.holidays = {}
        self.special_events = {}
    
    def _auto_detect_day_type(self):
        weekday = self.date.weekday()
        if weekday < 5:
            return "工作日"
        else:
            return "周末"
    
    def next_day(self):
        self.date = self.date + timedelta(days=1)
        self.day_type = self._auto_detect_day_type()
        return self
    
    def prev_day(self):
        self.date = self.date - timedelta(days=1)
        self.day_type = self._auto_detect_day_type()
        return self
    
    def set_day_type(self, day_type):
        self.day_type = day_type
        return self
    
    def add_holiday(self, date_str, holiday_name, description=""):
        date_key = datetime.strptime(date_str, "%Y年%m月%d日").strftime("%Y-%m-%d")
        self.holidays[date_key] = {
            "name": holiday_name,
            "description": description
        }
        return self
    
    def add_special_event(self, date_str, event_name, description=""):
        date_key = datetime.strptime(date_str, "%Y年%m月%d日").strftime("%Y-%m-%d")
        self.special_events[date_key] = {
            "name": event_name,
            "description": description
        }
        return self
    
    def is_holiday(self):
        date_key = self.date.strftime("%Y-%m-%d")
        return date_key in self.holidays
    
    def get_holiday_info(self):
        date_key = self.date.strftime("%Y-%m-%d")
        return self.holidays.get(date_key, None)
    
    def get_special_event_info(self):
        date_key = self.date.strftime("%Y-%m-%d")
        return self.special_events.get(date_key, None)
    
    def get_date_string(self):
        return self.date.strftime("%Y年%m月%d日")
    
    def get_weekday_chinese(self):
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[self.date.weekday()]
    
    def get_full_date_string(self):
        return f"{self.get_date_string()}（{self.get_weekday_chinese()}）"
    
    def get_context_info(self):
        info = {
            "date": self.get_date_string(),
            "weekday": self.get_weekday_chinese(),
            "day_type": self.day_type,
            "full_date": self.get_full_date_string()
        }
        
        if self.is_holiday():
            holiday_info = self.get_holiday_info()
            info["is_holiday"] = True
            info["holiday_name"] = holiday_info["name"]
            if holiday_info["description"]:
                info["holiday_description"] = holiday_info["description"]
        else:
            info["is_holiday"] = False
        
        special_event = self.get_special_event_info()
        if special_event:
            info["has_special_event"] = True
            info["special_event_name"] = special_event["name"]
            if special_event["description"]:
                info["special_event_description"] = special_event["description"]
        else:
            info["has_special_event"] = False
        
        return info
    
    def get_prompt_string(self):
        context = self.get_context_info()
        
        prompt_parts = [
            f"日期：{context['full_date']}（{context['day_type']}）"
        ]
        
        if context["is_holiday"]:
            prompt_parts.append(f"节假日：{context['holiday_name']}")
            if "holiday_description" in context:
                prompt_parts.append(f"说明：{context['holiday_description']}")
        
        if context["has_special_event"]:
            prompt_parts.append(f"特殊事件：{context['special_event_name']}")
            if "special_event_description" in context:
                prompt_parts.append(f"说明：{context['special_event_description']}")
        
        return "\n".join(prompt_parts)
    
    def to_dict(self):
        return self.get_context_info()
    
    def to_json(self):
        return json.dumps(self.get_context_info(), ensure_ascii=False, indent=2)
    
    def __str__(self):
        return self.get_full_date_string()
    
    def __repr__(self):
        return f"Time(date='{self.get_date_string()}', day_type='{self.day_type}')"
