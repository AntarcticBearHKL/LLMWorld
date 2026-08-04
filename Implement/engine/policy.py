











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
    def subsidy(cls, appliance="电动汽车", off_peak_rate=0.18,
                valley_hours=(22, 7)):

        return cls("subsidy", appliance=appliance, off_peak_rate=off_peak_rate,
                   valley_hours=valley_hours)

    @classmethod
    def nudge(cls, comparison_text="你的邻居平均每天用电 18 千瓦时"):

        return cls("nudge", comparison_text=comparison_text)

    @classmethod
    def nudge_loss(cls, comparison_text="你的邻居平均每天用电 18 千瓦时"):




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
                f"## 当前电价（分时电价）\n"
                f"- 峰时段 {peak_start:02d}:00-{peak_end:02d}:00：{p} 澳元/kWh\n"
                f"- 平时段：{f} 澳元/kWh\n"
                f"- 谷时段 {valley_start:02d}:00-{valley_end:02d}:00：{v} 澳元/kWh\n\n"
                f"省钱提示：大功率电器（洗衣机、电动汽车充电、热水器、空调）尽量安排在谷时段；"
                f"峰时段尽量减少大功率设备使用。"
            )

        if self.type == "subsidy":
            appliance = self.params["appliance"]
            rate = self.params["off_peak_rate"]
            valley_start, valley_end = self.params["valley_hours"]
            return (
                f"## 低谷充电补贴\n"
                f"- {appliance} 在谷时段 {valley_start}:00-{valley_end}:00 充电享受优惠价"
                f" {rate} 澳元/kWh\n"
                f"- 省钱提示：尽量在谷时段给 {appliance} 充电。"
            )

        if self.type == "nudge":
            return (
                f"## 社会规范信息\n"
                f"- {self.params['comparison_text']}。\n"
                f"- 你的家庭用电量已通过智能电表与社区对比，请尽量节约用电。"
            )

        if self.type == "nudge_loss":
            return (
                f"## 社会规范信息（损失警示）\n"
                f"- {self.params['comparison_text']}。\n"
                f"- 若家庭用电量不下降，社区将无法达成节能目标，"
                f"你的家庭将被标记为高耗能户，并失去每月 5 澳元的社区节能返利。\n"
                f"- 请务必避免这种损失，立刻减少不必要的用电。"
            )

        if self.type == "peak_demand":
            rate = self.params["rate_per_kw"]
            start, end = self.params["window"]
            return (
                f"## 需量电价（峰值收费）\n"
                f"- 每天 {start:02d}:00-{end:02d}:00 中，家庭全天功率最高的"
                f" 60 分钟将按 {rate} 澳元/kW 额外收费（月度结算）。\n"
                f"- 避免让多个大功率电器（空调、洗衣机、电磁炉、"
                f"电动汽车充电）在同一小时叠加使用；错峰开启可大幅降低账单。"
            )

        if self.type == "ev_delay":
            max_delay = self.params["max_delay_hours"]
            incentive = self.params["incentive_per_hour"]
            flat = self.params["flat_rate"]
            discount = min(flat, max_delay * incentive)
            delayed_rate = round(flat - discount, 2)
            return (
                f"## 电动汽车充电延迟激励（灵活充电菜单）\n"
                f"- 立即充电（今晚{flat:.2f} 澳元/kWh）：最早完成，价格最高。\n"
                f"- 延迟充电菜单：选择“最晚完成充电时间”越晚，电价越低——"
                f"每延迟 1 小时电价降 {incentive:.2f} 澳元/kWh，"
                f"最多延迟 {max_delay} 小时（电价降至 {delayed_rate:.2f} 澳元/kWh）。\n"
                f"- 系统会在深夜谷段自动安排充电，保证在承诺时限前充满。"
            )

        if "+" in self.type:
            subs = self.params["policies"]
            names = " + ".join(s.type for s in subs)
            body = "\n\n".join(s.render() for s in subs)
            return f"## 当前政策组合（{names}）\n\n{body}"
        return ""



    def describe(self):
        return f"{self.type}({self.params})"

    @classmethod
    def from_name(cls, name, **kwargs):

        factories = {"tou": cls.tou, "subsidy": cls.subsidy,
                     "nudge": cls.nudge, "nudge_loss": cls.nudge_loss,
                     "peak_demand": cls.peak_demand, "ev_delay": cls.ev_delay}
        if "," in name:
            return cls.combine(name, **kwargs)
        if name not in factories:
            raise ValueError(f"未知政策类型: {name}"
                             "（可用: tou/subsidy/nudge/nudge_loss/peak_demand/ev_delay 或逗号组合）")
        return factories[name](**kwargs)
