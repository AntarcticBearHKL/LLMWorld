











class HouseholdMemory:
    def __init__(self):
        self.days = []
        self.last = None
        self.news_memory = []

    def load_days(self, days):

        self.days = list(days)
        self.last = days[-1] if days else None

    def load_news_memory(self, news_memory):

        self.news_memory = list(news_memory or [])

    def add_news(self, items, keep=None):




        if keep is None:
            import config
            keep = config.NEWS_MEMORY_KEEP
        for item in items:
            date = item.date if hasattr(item, "date") else item[0]
            title = item.title if hasattr(item, "title") else item[1]
            entry = {"date": date, "title": title}
            if entry not in self.news_memory:
                self.news_memory.append(entry)
        self.news_memory = self.news_memory[-keep:]

    def get_news_memory_state(self):
        return list(self.news_memory)



    def update_from_day(self, day_result):

        summary = self._build_summary(day_result)
        self.days.append(summary)
        self.last = summary
        return summary



    def _build_summary(self, day_result):
        planner = day_result["planner"]


        member_summaries = {}
        for name, timeline in planner.timelines.items():
            member_summaries[name] = self._summarize_member(timeline)


        energy = day_result.get("energy_summary", {})
        electricity = self._summarize_electricity(day_result, energy)

        return {
            "date": day_result.get("date", ""),
            "members": member_summaries,
            "electricity": electricity,
        }

    def _summarize_member(self, timeline):
        slots = timeline.slots

        wake_time = None
        sleep_time = None
        activities = []

        for slot in slots:
            activity = slot.activity or ""
            is_sleep = ("sleep" in activity.lower())

            if not is_sleep and wake_time is None:
                wake_time = self._fmt(slot.start)
            if is_sleep:
                sleep_time = self._fmt(slot.end)

            if not is_sleep and len(activities) < 8:
                activities.append(f"{self._fmt(slot.start)}-{self._fmt(slot.end)} {slot.location} {activity}")

        if not activities and slots:

            s = slots[0]
            activities.append(f"{self._fmt(s.start)}-{self._fmt(s.end)} {s.location} {s.activity}")

        return {
            "activities": activities,
            "wake_time": wake_time,
            "sleep_time": sleep_time,
        }

    def _summarize_electricity(self, day_result, energy_summary):
        total = energy_summary.get("total_energy_kwh", 0)
        baseline = energy_summary.get("baseline_kwh", 0)
        decision = energy_summary.get("decision_kwh", 0)


        peak_time = None
        peak_watts = None
        calculator = day_result.get("energy_calculator")
        if calculator is not None and hasattr(calculator, "household_load_watts"):
            loads = calculator.household_load_watts
            if loads:
                peak_minute = max(range(len(loads)), key=lambda m: loads[m])
                peak_watts = round(loads[peak_minute])
                peak_time = f"{peak_minute // 60:02d}:{peak_minute % 60:02d}"


        top_appliances = []
        for app in energy_summary.get("appliances", [])[:3]:
            top_appliances.append(f"{app['name']} {app['total_energy_kwh']:.1f} kWh")

        return {
            "total_kwh": round(total, 2),
            "baseline_kwh": round(baseline, 2),
            "decision_kwh": round(decision, 2),
            "peak_time": peak_time,
            "peak_watts": peak_watts,
            "top_appliances": top_appliances,
        }



    def get_prompt_context(self):

        parts = []
        if self.last:
            lines = []
            for name, m in self.last["members"].items():
                lines.append(f"{name}'s activities yesterday:")
                for act in m["activities"]:
                    lines.append(f"  - {act}")
                rhythm = []
                if m["wake_time"]:
                    rhythm.append(f"Wake up {m['wake_time']}")
                if m["sleep_time"]:
                    rhythm.append(f"Sleep {m['sleep_time']}")
                if rhythm:
                    lines.append(f"  Routine: {', '.join(rhythm)}")
                lines.append("")

            elec = self.last["electricity"]
            elec_line = f"Household electricity yesterday ({self.last['date']}): total {elec['total_kwh']} kWh"
            if elec["peak_time"]:
                elec_line += f", peak {elec['peak_time']} ({elec['peak_watts']} W)"
            lines.append(elec_line)
            if elec["top_appliances"]:
                lines.append(f"Main consumers: {', '.join(elec['top_appliances'])}")

            parts.append("## Yesterday's memory (to help maintain habit continuity; yesterday's events affect today's planning)\n"
                         + "\n".join(lines))


        if self.news_memory:
            lines = ["## Recent external information review (highlights of recently seen news)"]
            for entry in self.news_memory:
                lines.append(f"- [{entry['date']}] {entry['title']}")
            parts.append("\n".join(lines))

        return "\n\n".join(parts)



    @staticmethod
    def _fmt(minutes):
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
