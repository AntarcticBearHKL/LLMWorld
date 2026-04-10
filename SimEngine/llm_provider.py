import requests
import json
from .const import (
    DEEPSEEK_APIKEY, 
    DEFAULT_MODEL_DEEPSEEK, 
    DEFAULT_TEMPERATURE, 
    DEFAULT_MAX_TOKENS
)

class DeepSeekProvider:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or DEEPSEEK_APIKEY
        if not self.api_key:
            raise ValueError("DeepSeek API key not found. Please set DEEPSEEK_APIKEY environment variable.")
        self.model = model or DEFAULT_MODEL_DEEPSEEK
        self.base_url = "https://api.deepseek.com/v1"
    
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
            response = requests.post(self.base_url + "/chat/completions", headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = "DeepSeek API Error " + str(response.status_code) + ": " + response.text
                print("[DeepSeek Error] " + error_msg)
                return error_msg
            
            result = response.json()
            print("[DeepSeek Response] " + str(result))
            
            if "error" in result:
                error_msg = "DeepSeek Error: " + result['error']['message']
                print("[DeepSeek Error] " + error_msg)
                return error_msg
            
            if "choices" not in result or not result["choices"]:
                error_msg = "DeepSeek Error: No choices in response. Full response: " + str(result)
                print("[DeepSeek Error] " + error_msg)
                return error_msg
            
            content = result["choices"][0]["message"]["content"].strip()
            print("[DeepSeek Success] Generated: " + content)
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