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

# 深度思考开关（基准测试：开启约慢 90 倍，3分钟 vs 2秒，JSON 质量无差异）
# 默认关闭以保证大规模模拟可行；需要更高决策质量时置 True（单点实验用）
THINKING = False
REASONING_EFFORT = "medium"   # low / medium / high（仅 THINKING=True 时生效）

# 并发与重试（用户硬性要求：同时并发不得超过 10）
MAX_WORKERS = 10
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 120

# ---------- 模拟默认值 ----------
DEFAULT_START_DATE = "2026年4月21日"
DEFAULT_DAYS = 5
DEFAULT_SEASON = "春天"
DEFAULT_WEATHER = "晴天"
DEFAULT_TEMPERATURE = 20
DEFAULT_SEED = 42

# ---------- 数据 ----------
CLAYTON_POSTCODE = "3168"
