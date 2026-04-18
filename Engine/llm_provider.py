import requests
import json
from .const import (
    DEEPSEEK_APIKEY,
    GLM_APIKEY,
    GLMF_APIKEY,
    DEFAULT_MODEL_DEEPSEEK,
    DEFAULT_MODEL_GLM,
    DEFAULT_MODEL_GLMF,
    DEFAULT_TEMPERATURE, 
    DEFAULT_MAX_TOKENS,
    ENABLE_DEEP_THINKING
)

class DeepSeekProvider:
    def __init__(self, api_key=None, model=None, json_mode=False):
        self.api_key = api_key or DEEPSEEK_APIKEY
        if not self.api_key:
            raise ValueError("DeepSeek API key not found. Please set DEEPSEEK_APIKEY environment variable.")
        self.model = model or DEFAULT_MODEL_DEEPSEEK
        self.base_url = "https://api.deepseek.com/v1"
        self.json_mode = json_mode
    
    def generate(self, prompt):
        try:
            headers = {
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS
            }
            
            if self.json_mode:
                data["response_format"] = {"type": "json_object"}
            
            response = requests.post(self.base_url + "/chat/completions", headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = "DeepSeek API Error " + str(response.status_code) + ": " + response.text
                print("[DeepSeek Error] " + error_msg)
                return error_msg
            
            result = response.json()
            
            if "error" in result:
                error_msg = "DeepSeek Error: " + result['error']['message']
                print("[DeepSeek Error] " + error_msg)
                return error_msg
            
            if "choices" not in result or not result["choices"]:
                error_msg = "DeepSeek Error: No choices in response. Full response: " + str(result)
                print("[DeepSeek Error] " + error_msg)
                return error_msg
            
            content = result["choices"][0]["message"]["content"].strip()
            return content
        except requests.exceptions.RequestException as e:
            error_msg = "Network Error: " + str(e)
            print("[DeepSeek Network Error] " + error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = "JSON Error: " + str(e)
            print("[DeepSeek JSON Error] " + error_msg)
            return error_msg
        except Exception as e:
            error_msg = "DeepSeek Error: " + str(e)
            print("[DeepSeek Exception] " + error_msg)
            return error_msg

class GLMProvider:
    def __init__(self, api_key=None, model=None, enable_deep_thinking=None, json_mode=False):
        self.api_key = api_key or GLM_APIKEY
        if not self.api_key:
            raise ValueError("GLM API key not found. Please set GLM_APIKEY environment variable.")
        self.model = model or DEFAULT_MODEL_GLM
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.enable_deep_thinking = enable_deep_thinking if enable_deep_thinking is not None else ENABLE_DEEP_THINKING
        self.json_mode = json_mode
    
    def generate(self, prompt, messages=None):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.api_key
            }
            
            if messages is None:
                messages = [{"role": "user", "content": prompt}]
            
            data = {
                "model": self.model,
                "messages": messages,
            }
            
            if self.enable_deep_thinking:
                data["thinking"] = {"type": "enabled"}
            
            if self.json_mode:
                data["response_format"] = {"type": "json_object"}
            
            response = requests.post(
                self.base_url + "/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_msg = "GLM API Error " + str(response.status_code) + ": " + response.text
                print("[GLM Error] " + error_msg)
                return error_msg
            
            result = response.json()
            
            if "error" in result:
                error_msg = "GLM Error: " + result['error']['message']
                print("[GLM Error] " + error_msg)
                return error_msg
            
            if "choices" not in result or not result["choices"]:
                error_msg = "GLM Error: No choices in response. Full response: " + str(result)
                print("[GLM Error] " + error_msg)
                return error_msg
            
            content = result["choices"][0]["message"]["content"].strip()
            return content
        except requests.exceptions.RequestException as e:
            error_msg = "Network Error: " + str(e)
            print("[GLM Network Error] " + error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = "JSON Error: " + str(e)
            print("[GLM JSON Error] " + error_msg)
            return error_msg
        except Exception as e:
            error_msg = "GLM Error: " + str(e)
            print("[GLM Exception] " + error_msg)
            return error_msg

class GLMFProvider:
    def __init__(self, api_key=None, model=None, enable_deep_thinking=None, json_mode=False):
        self.api_key = api_key or GLMF_APIKEY
        if not self.api_key:
            raise ValueError("GLMF API key not found. Please set GLMF_APIKEY environment variable.")
        self.model = model or DEFAULT_MODEL_GLMF
        self.base_url = "https://api.z.ai/api/paas/v4"
        self.enable_deep_thinking = enable_deep_thinking if enable_deep_thinking is not None else ENABLE_DEEP_THINKING
        self.json_mode = json_mode
    
    def generate(self, prompt, messages=None):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.api_key,
                "Accept-Language": "en-US,en"
            }
            
            if messages is None:
                messages = [{"role": "user", "content": prompt}]
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": DEFAULT_TEMPERATURE
            }
            
            if self.enable_deep_thinking:
                data["thinking"] = {"type": "enabled"}
            
            if self.json_mode:
                data["response_format"] = {"type": "json_object"}
            
            response = requests.post(
                self.base_url + "/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_msg = "GLMF API Error " + str(response.status_code) + ": " + response.text
                print("[GLMF Error] " + error_msg)
                return error_msg
            
            result = response.json()
            
            if "error" in result:
                error_msg = "GLMF Error: " + result['error']['message']
                print("[GLMF Error] " + error_msg)
                return error_msg
            
            if "choices" not in result or not result["choices"]:
                error_msg = "GLMF Error: No choices in response. Full response: " + str(result)
                print("[GLMF Error] " + error_msg)
                return error_msg
            
            content = result["choices"][0]["message"]["content"].strip()
            return content
        except requests.exceptions.RequestException as e:
            error_msg = "Network Error: " + str(e)
            print("[GLMF Network Error] " + error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = "JSON Error: " + str(e)
            print("[GLMF JSON Error] " + error_msg)
            return error_msg
        except Exception as e:
            error_msg = "GLMF Error: " + str(e)
            print("[GLMF Exception] " + error_msg)
            return error_msg
