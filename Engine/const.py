import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_APIKEY = os.getenv('DEEPSEEK_APIKEY', '')
GLM_APIKEY = os.getenv('GLM_APIKEY', '')
GLMF_APIKEY = os.getenv('GLMF_APIKEY', '')

DEFAULT_MODEL_DEEPSEEK = 'deepseek-chat'
DEFAULT_MODEL_GLM = 'glm-4.7'
DEFAULT_MODEL_GLMF = 'glm-5'

DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 8192
ENABLE_DEEP_THINKING = False