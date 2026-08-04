"""新闻台：外部世界信息通道（上帝模式 + agent 每日信息摄入）。

上帝（运行者）通过两种方式向世界注入信息：
1. worlds/<world_id>/events.json 剧本文件（推荐，模拟中每天重读，可随时编辑）
2. 命令行 --event "日期|标题|内容" 或代码 API world.news.add_event(...)

Agent 在模拟中通过两处获取新闻（prompt 注入）：
- 第一层宏观计划：早上获知今日新闻，结合性格影响全天安排
- 第四层用电决策：电价/能源类新闻直接影响电器使用

每个新闻条目包含：日期（发布）、时间（可获取时段）、标题、内容、来源、类型。
"""

import json
import os


class NewsItem:
    """一条世界新闻。date 为发布日期（YYYY-MM-DD），time 为该日可获取时刻（HH:MM）。"""

    def __init__(self, date, time, title, content, source="官方公告", news_type="一般"):
        self.date = date          # 发布日期 "2026-04-21"
        self.time = time          # 可获取时刻 "07:00"
        self.title = title
        self.content = content
        self.source = source      # 政府公告/新闻媒体/社交媒体...
        self.news_type = news_type  # 政策/经济/社会/环境...

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
            source=d.get("source", "官方公告"), news_type=d.get("type", "一般"),
        )


class NewsBoard:
    """新闻台：加载剧本、按日期过滤、渲染 prompt 文本。"""

    def __init__(self, events_file=None):
        self.items = []          # 全部新闻（按日期升序）
        self.events_file = events_file
        if events_file and os.path.exists(events_file):
            self.load_events(events_file)

    # ---------- 加载与上帝注入 ----------

    def load_events(self, path):
        """从 JSON 剧本文件加载新闻（上帝静态剧本）。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("events", []):
            self.add_event(NewsItem.from_dict(item))
        # 排序：日期+时间升序
        self.items.sort(key=lambda n: (n.date, n.time))

    def add_event(self, news_item):
        """运行时注入新闻（上帝 API）。"""
        self.items.append(news_item)
        self.items.sort(key=lambda n: (n.date, n.time))

    def add_inline_event(self, text):
        """命令行格式注入："2026-04-21|标题|内容[|来源]"。解析失败时抛出异常。"""
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            raise ValueError(f"事件格式应为 日期|标题|内容[|来源]，收到: {text}")
        self.add_event(NewsItem(date=parts[0], time="07:00",
                                title=parts[1], content=parts[2],
                                source=parts[3] if len(parts) > 3 else "官方公告"))

    # ---------- 查询与渲染 ----------

    def available_on(self, date_str):
        """某日可获取的新闻（发布日期 <= 当日）。"""
        return [n for n in self.items if n.date <= date_str]

    def render_for_prompt(self, date_str):
        """渲染成注入 prompt 的 markdown 文本；无新闻返回空串。"""
        items = self.available_on(date_str)
        if not items:
            return ""

        lines = ["## 今日外界信息（你会在今天获取到以下新闻）", ""]
        for n in items:
            header = f"- [{n.date} {n.time}]（{n.source}）{n.title}"
            lines.append(header)
            lines.append(f"  {n.content}")
        lines.append("")
        lines.append("请结合你的性格、职业与立场分析这些信息，思考它们对你的生活安排的影响。")
        return "\n".join(lines)

    def to_json(self):
        return json.dumps([n.to_dict() for n in self.items], ensure_ascii=False, indent=2)
