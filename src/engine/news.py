import json
import os


class NewsItem:


    def __init__(self, date, time, title, content, source="Official announcement", news_type="General"):
        self.date = date
        self.time = time
        self.title = title
        self.content = content
        self.source = source
        self.news_type = news_type

    def to_dict(self):
        return {
            "date": self.date, "time": self.time, "title": self.title,
            "content": self.content, "source": self.source, "type": self.news_type,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            date=d.get("date", ""), time=d.get("time", "07:00"),
            title=d.get("title", ""), content=d.get("content", ""),
            source=d.get("source", "Official announcement"), news_type=d.get("type", "General"),
        )


class NewsBoard:





    def __init__(self, events_file=None, delivered_ids=None):
        self.items = []
        self.events_file = events_file
        self.delivered_ids = set(delivered_ids or [])
        if events_file and os.path.exists(events_file):
            self.load_events(events_file)



    def load_events(self, path):

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("events", []):
            self.add_event(NewsItem.from_dict(item))

        self.items.sort(key=lambda n: (n.date, n.time))

    def add_event(self, news_item):

        self.items.append(news_item)
        self.items.sort(key=lambda n: (n.date, n.time))

    def add_inline_event(self, text):

        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            raise ValueError(f"Event format should be date|title|content[|source], received: {text}")
        self.add_event(NewsItem(date=parts[0], time="07:00",
                                title=parts[1], content=parts[2],
                                source=parts[3] if len(parts) > 3 else "Official announcement"))



    @staticmethod
    def _news_id(item):

        return f"{item.date}_{item.time}_{item.title}"

    def get_new_for(self, date_str):




        new_items = []
        for item in self.items:
            nid = self._news_id(item)
            if nid in self.delivered_ids:
                continue
            if item.date <= date_str:
                new_items.append(item)
                self.delivered_ids.add(nid)
        return new_items

    def delivered_on(self, date_str):

        return [item for item in self.items if item.date == date_str
                and self._news_id(item) in self.delivered_ids]

    def to_state(self):

        return {"delivered_ids": sorted(self.delivered_ids)}

    def restore_state(self, state):

        if state:
            self.delivered_ids = set(state.get("delivered_ids", []))



    def available_on(self, date_str):

        return [n for n in self.items if n.date <= date_str]

    def render_for_prompt(self, date_str):

        items = self.get_new_for(date_str)
        return self.render_items(items)

    def render_items(self, items):

        if not items:
            return ""
        lines = ["## External information today (you will receive the following news today)", ""]
        for n in items:
            header = f"- [{n.date} {n.time}] ({n.source}) {n.title}"
            lines.append(header)
            lines.append(f"  {n.content}")
        lines.append("")
        lines.append("Please analyze this information in light of your personality, occupation and stance, "
                     "and consider how it affects your daily arrangements.")
        return "\n".join(lines)

    def to_json(self):
        return json.dumps([n.to_dict() for n in self.items], ensure_ascii=False, indent=2)
