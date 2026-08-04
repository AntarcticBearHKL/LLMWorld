"""政策干预模块：把政策信号渲染成注入智能体 prompt 的文本（论文 RQ2）。

支持三类政策（全部参数可配，缺省为空 = 无干预）：
1. tou    分时电价（峰/平/谷时段 + 费率）
2. subsidy 特定电器补贴（如低谷充电返现）
3. nudge  社会规范信息（邻居对比 + 节能呼吁）

设计原则：policy 只是"文本上下文"，不改变任何计算逻辑——
LLM 是否响应、如何响应，本身就是实验要观察的对象。
"""


class Policy:
    def __init__(self, policy_type, **kwargs):
        self.type = policy_type
        self.params = kwargs

    # ---------- 构建 ----------

    @classmethod
    def tou(cls, peak_hours=(16, 21), valley_hours=(22, 7),
            peak_rate=0.55, flat_rate=0.35, valley_rate=0.25):
        """分时电价：peak_hours=(起始,结束)，valley_hours 跨天用 (22,7)。"""
        return cls("tou", peak_hours=peak_hours, valley_hours=valley_hours,
                   peak_rate=peak_rate, flat_rate=flat_rate, valley_rate=valley_rate)

    @classmethod
    def subsidy(cls, appliance="电动汽车", off_peak_rate=0.18,
                valley_hours=(22, 7)):
        """低谷充电补贴：指定电器在谷时段充电享受更低价。"""
        return cls("subsidy", appliance=appliance, off_peak_rate=off_peak_rate,
                   valley_hours=valley_hours)

    @classmethod
    def nudge(cls, comparison_text="你的邻居平均每天用电 18 千瓦时"):
        """社会规范 nudge：邻居对比信息。"""
        return cls("nudge", comparison_text=comparison_text)

    # ---------- 渲染 ----------

    def render(self):
        """渲染成注入决策 prompt 的文本段；返回空串 = 无政策。"""
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

        return ""

    # ---------- 工具 ----------

    def describe(self):
        return f"{self.type}({self.params})"

    @classmethod
    def from_name(cls, name, **kwargs):
        """按名字创建（runner 命令行用）：tou / subsidy / nudge。"""
        factories = {"tou": cls.tou, "subsidy": cls.subsidy, "nudge": cls.nudge}
        if name not in factories:
            raise ValueError(f"未知政策类型: {name}（可用: tou/subsidy/nudge）")
        return factories[name](**kwargs)
