











class Policy:
    def __init__(self, policy_type, **kwargs):
        self.type = policy_type
        self.params = kwargs



    @classmethod
    def tou(cls, peak_hours=(16, 21), valley_hours=(22, 7),
            peak_rate=0.55, flat_rate=0.35, valley_rate=0.25):

        return cls("tou", peak_hours=peak_hours, valley_hours=valley_hours,
                   peak_rate=peak_rate, flat_rate=flat_rate, valley_rate=valley_rate)

    @classmethod
    def subsidy(cls, appliance="Electric Vehicle", off_peak_rate=0.18,
                valley_hours=(22, 7)):

        return cls("subsidy", appliance=appliance, off_peak_rate=off_peak_rate,
                   valley_hours=valley_hours)

    @classmethod
    def nudge(cls, comparison_text="Your neighbours use 18 kWh of electricity per day on average"):

        return cls("nudge", comparison_text=comparison_text)

    @classmethod
    def nudge_loss(cls, comparison_text="Your neighbours use 18 kWh of electricity per day on average"):




        return cls("nudge_loss", comparison_text=comparison_text)

    @classmethod
    def peak_demand(cls, rate_per_kw=12.0, window=(0, 24)):

        return cls("peak_demand", rate_per_kw=rate_per_kw, window=window)

    @classmethod
    def ev_delay(cls, max_delay_hours=8, incentive_per_hour=0.02,
                 charging_window=(23, 7), flat_rate=0.55):

        return cls("ev_delay", max_delay_hours=max_delay_hours,
                   incentive_per_hour=incentive_per_hour,
                   charging_window=charging_window, flat_rate=flat_rate)

    @classmethod
    def night_setback(cls, reduce_hours=(23, 6), target_temp="16-18°C",
                      saving_note="can save 5-10% on heating electricity bills"):

        return cls("night_setback", reduce_hours=reduce_hours,
                   target_temp=target_temp, saving_note=saving_note)

    @classmethod
    def in_home_display(cls, feedback_text="The in-home smart meter display shows current power and electricity cost in real time"):

        return cls("in_home_display", feedback_text=feedback_text)



    @classmethod
    def combine(cls, names, **kwargs):
        parts = [name.strip() for name in names.split(",") if name.strip()]
        policies = [cls.from_name(name) for name in parts]
        return cls("+".join(parts), policies=policies)


    def render(self):

        if self.type == "tou":
            peak_start, peak_end = self.params["peak_hours"]
            valley_start, valley_end = self.params["valley_hours"]
            p, f, v = (self.params["peak_rate"], self.params["flat_rate"],
                       self.params["valley_rate"])
            return (
                f"## Current electricity tariff (time-of-use)\n"
                f"- Peak hours {peak_start:02d}:00-{peak_end:02d}:00: {p} AUD/kWh\n"
                f"- Standard hours: {f} AUD/kWh\n"
                f"- Valley hours {valley_start:02d}:00-{valley_end:02d}:00: {v} AUD/kWh\n\n"
                f"Money-saving tip: schedule high-power appliances (washing machine, EV charging, "
                f"water heater, air conditioner) during valley hours; "
                f"minimise use of high-power devices during peak hours."
            )

        if self.type == "subsidy":
            appliance = self.params["appliance"]
            rate = self.params["off_peak_rate"]
            valley_start, valley_end = self.params["valley_hours"]
            return (
                f"## Off-peak charging subsidy\n"
                f"- Charging the {appliance} during valley hours {valley_start}:00-{valley_end}:00 "
                f"qualifies for the discounted rate of {rate} AUD/kWh\n"
                f"- Money-saving tip: charge the {appliance} during valley hours when possible."
            )

        if self.type == "nudge":
            return (
                f"## Social norm information\n"
                f"- {self.params['comparison_text']}.\n"
                f"- Your household electricity usage is compared with the community via the smart meter; "
                f"please try to save electricity."
            )

        if self.type == "nudge_loss":
            return (
                f"## Social norm information (loss framing)\n"
                f"- {self.params['comparison_text']}.\n"
                f"- If your household electricity usage does not decrease, the community will not reach "
                f"its energy-saving target, your household will be flagged as a high-consumption household, "
                f"and you will lose the monthly AUD 5 community energy-saving rebate.\n"
                f"- Please avoid this loss and immediately reduce unnecessary electricity use."
            )

        if self.type == "peak_demand":
            rate = self.params["rate_per_kw"]
            start, end = self.params["window"]
            return (
                f"## Demand tariff (peak charging)\n"
                f"- Between {start:02d}:00-{end:02d}:00 each day, the 60 minutes with the highest "
                f"household power draw will be charged an additional {rate} AUD/kW (settled monthly).\n"
                f"- Avoid running multiple high-power appliances (air conditioner, washing machine, "
                f"induction cooker, EV charging) in the same hour; staggering them can significantly "
                f"lower your bill."
            )

        if self.type == "ev_delay":
            max_delay = self.params["max_delay_hours"]
            incentive = self.params["incentive_per_hour"]
            flat = self.params["flat_rate"]
            discount = min(flat, max_delay * incentive)
            delayed_rate = round(flat - discount, 2)
            return (
                f"## EV charging delay incentive (flexible charging menu)\n"
                f"- Charge now ({flat:.2f} AUD/kWh): finished earliest, highest price.\n"
                f"- Delay menu: the later you choose the 'latest charging completion time', the lower the "
                f"price — each 1-hour delay reduces the price by {incentive:.2f} AUD/kWh, "
                f"up to {max_delay} hours delay (price drops to {delayed_rate:.2f} AUD/kWh).\n"
                f"- The system automatically schedules charging late at night during valley hours, "
                f"guaranteeing a full charge by the promised deadline."
            )

        if "+" in self.type:
            subs = self.params["policies"]
            names = " + ".join(s.type for s in subs)
            body = "\n\n".join(s.render() for s in subs)
            return f"## Current policy combination ({names})\n\n{body}"

        if self.type == "night_setback":
            start, end = self.params["reduce_hours"]
            target = self.params["target_temp"]
            note = self.params["saving_note"]
            return (
                f"## Night setback suggestion (heating energy saving)\n"
                f"- Between {start:02d}:00-{end:02d}:00 at night and whenever everyone is away, "
                f"lower the heater to {target}.\n"
                f"- Use thick blankets instead of a high room temperature when sleeping; turn off or lower "
                f"the heater before leaving home, avoiding wasted heating of an empty house.\n"
                f"- {note}, one of the most important energy-saving behaviours for home heating."
            )

        if self.type == "in_home_display":
            return (
                f"## Smart meter real-time feedback\n"
                f"- {self.params['feedback_text']}, viewable at any time:\n"
                f"  1. Current instantaneous power and hourly electricity cost;\n"
                f"  2. Daily electricity usage trend comparison over the last 7 days;\n"
                f"  3. Instant cost reminders when high-power appliances are switched on.\n"
                f"- The display updates in real time when you turn on high-power appliances; "
                f"please pay attention and avoid waste."
            )
        return ""



    def describe(self):
        return f"{self.type}({self.params})"

    @classmethod
    def from_name(cls, name, **kwargs):

        factories = {"tou": cls.tou, "subsidy": cls.subsidy,
                     "nudge": cls.nudge, "nudge_loss": cls.nudge_loss,
                     "peak_demand": cls.peak_demand, "ev_delay": cls.ev_delay,
                     "night_setback": cls.night_setback,
                     "in_home_display": cls.in_home_display}
        if "," in name:
            return cls.combine(name, **kwargs)
        if name not in factories:
            raise ValueError(f"Unknown policy type: {name}"
                             " (available: tou/subsidy/nudge/nudge_loss/peak_demand/ev_delay/night_setback/in_home_display or comma-separated combinations)")
        return factories[name](**kwargs)
