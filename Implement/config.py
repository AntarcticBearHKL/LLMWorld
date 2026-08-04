"""全局配置：所有可调参数集中在这里，改一处全项目生效。

规则：
- API Key 从 .env 读取（DEEPSEEK_APIKEY），本文件不存任何密钥
- 并发上限固定为 10（用户硬性要求），禁止调大
- 随机种子默认固定，保证实验可复现
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------- LLM ----------
DEEPSEEK_APIKEY = os.getenv("DEEPSEEK_APIKEY", "")
MODEL = "deepseek-v4-flash"
TEMPERATURE = 1.0
MAX_TOKENS = 64000

# 深度思考开关与强度（DeepSeek 官方文档 api-docs.deepseek.com/guides/thinking_mode）
# 官方取值：reasoning_effort 仅支持 low/high/max
# effort 映射表：deepseek-v4-flash 传 low → 实际 low（最低）；默认 high
# 用户 2026-08 指令：所有模拟思考强度调到最低 → "low"
# 注：思考模式下 temperature/top_p/presence_penalty/frequency_penalty 不生效（官方文档），
#     故 thinking=True 的请求不再发送 temperature
THINKING = False
REASONING_EFFORT = "low"   # low / high / max（官方枚举；flash 模型 low 映射为最低）

# 并发与重试（用户最新指令 2026-08：解除 API 并发限制——不设任何上限）
# 注意：世界级约束见 population.py（每世界最多 10 户）
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
# 请求超时 600s：DeepSeek 对超限速请求会排队（实测 5 并发中 2 个排队 4 分钟），
# 过短超时会误杀排队中的请求并触发重试雪崩
REQUEST_TIMEOUT_SECONDS = 600

# ---------- 模拟默认值 ----------
DEFAULT_START_DATE = "2026年4月21日"
DEFAULT_DAYS = 5
DEFAULT_SEASON = "春天"
DEFAULT_WEATHER = "晴天"
DEFAULT_TEMPERATURE = 20
DEFAULT_SEED = 42

# ---------- 数据 ----------
CLAYTON_POSTCODE = "3168"

# ---------- 环境信息（计划23：开放接口）----------
# 模式：real=真实天气API（无key/失败自动回退config）/ config=墨尔本气候表随机 / manual=手工配置
ENV_MODE = "config"

# 墨尔本气候校准表：四季 → 温度范围 + 天气概率分布（(天气, 权重)）
MELBOURNE_CLIMATE = {
    "夏天": {"temp_range": (24, 38), "weathers": [("晴天", 40), ("多云", 25), ("热浪", 15), ("阵雨", 20)]},
    "秋天": {"temp_range": (14, 25), "weathers": [("晴天", 35), ("多云", 30), ("阵雨", 25), ("大风", 10)]},
    "冬天": {"temp_range": (7, 16),  "weathers": [("多云", 35), ("阴天", 25), ("阵雨", 30), ("寒潮", 10)]},
    "春天": {"temp_range": (12, 23), "weathers": [("晴天", 40), ("多云", 30), ("阵雨", 25), ("大风", 5)]},
}

# manual 模式的手工配置文件（固定值或 [min,max] 范围）
ENV_MANUAL_FILE = "env_manual.json"

# ---------- 新闻记忆化（计划35）----------
# 跨天记忆里保留的新闻要点条数（滚动保留最近 N 条，摘要形式注入，不重复原文）
NEWS_MEMORY_KEEP = 5

# ---------- 决策真实性硬上限（计划7）----------
# 每电器每日最大使用分钟数：防止 LLM 产生不真实决策（如 EV 连续充电 12 小时）
# 超限部分会被截断并记入 validation_warnings（不静默）
APPLIANCE_DAILY_CAP_MINUTES = {
    "电动汽车": 4 * 60,   # 充满约需 3-4 小时
    "热水器": 45,         # 每次洗澡 15-30 分钟
    "空调": 6 * 60,       # 一天最多连续开 6 小时
    "洗衣机": 2 * 60,
    "吸尘器": 60,
    "电视": 8 * 60,
    "电脑": 10 * 60,
    "电磁炉": 2 * 60,
    "微波炉": 60,
    "电饭煲": 2 * 60,
    "手机": 4 * 60,
    "灯": 16 * 60,
    "台灯": 16 * 60,
    "油烟机": 2 * 60,
}
