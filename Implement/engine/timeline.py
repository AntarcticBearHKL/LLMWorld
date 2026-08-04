





import json

from . import utils


class TimeSlot:
    def __init__(self, start_minutes, end_minutes, location, activity, desc=""):
        self.start = start_minutes
        self.end = end_minutes
        self.location = location
        self.activity = activity
        self.desc = desc

    def overlaps(self, other_start, other_end):
        return not (self.end <= other_start or self.start >= other_end)

    def to_dict(self):
        result = {
            "time": self._format_time_range(),
            "location": self.location,
            "activity": self.activity
        }
        if self.desc:
            result["desc"] = self.desc
        return result

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

    def load_from_activities(self, activities):

        self.slots = []
        for activity in activities:
            try:
                time_range = activity['time']
                location = activity.get('location', '')
                activity_desc = activity['activity']

                start_min, end_min = utils.parse_time_range(time_range)
                slot = TimeSlot(start_min, end_min, location, activity_desc)
                self.slots.append(slot)
            except Exception as e:
                print(f"[错误] 加载活动失败: {activity} - {e}")
                print("[跳过] 该活动")
                continue

        self.slots.sort(key=lambda s: s.start)

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
