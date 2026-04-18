import requests
import json
import os
from dotenv import load_dotenv
from threading import Thread, Lock
from queue import Queue
from typing import Callable, Any, Dict, List

load_dotenv()

DEEPSEEK_APIKEY = os.getenv('DEEPSEEK_APIKEY', '')
GLM_APIKEY = os.getenv('GLM_APIKEY', '')
DEFAULT_MODEL_DEEPSEEK = 'deepseek-chat'
DEFAULT_MODEL_REASONER = 'deepseek-reasoner'
DEFAULT_MODEL_GLM = 'glm-4.7'
DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 8192

class SubAgent:
    _lock = Lock()
    _total_prompt_cache_hit_tokens = 0
    _total_prompt_cache_miss_tokens = 0
    _total_completion_tokens = 0
    
    @staticmethod
    def _update_tokens(cache_hit, cache_miss, completion):
        with SubAgent._lock:
            SubAgent._total_prompt_cache_hit_tokens += cache_hit
            SubAgent._total_prompt_cache_miss_tokens += cache_miss
            SubAgent._total_completion_tokens += completion
    
    @staticmethod
    def get_tokens():
        with SubAgent._lock:
            return (
                SubAgent._total_prompt_cache_miss_tokens,
                SubAgent._total_prompt_cache_hit_tokens,
                SubAgent._total_completion_tokens
            )
    
    @staticmethod
    def reset_tokens():
        with SubAgent._lock:
            SubAgent._total_prompt_cache_hit_tokens = 0
            SubAgent._total_prompt_cache_miss_tokens = 0
            SubAgent._total_completion_tokens = 0
    
    @staticmethod
    def call_glm(prompt: str, json_mode: bool = False, thinking: bool = False, api_key: str = None, model: str = None) -> str:
        api_key = api_key or GLM_APIKEY
        if not api_key:
            raise ValueError("GLM API key not found. Please set GLM_APIKEY environment variable.")
        
        model = model or DEFAULT_MODEL_GLM
        base_url = "https://open.bigmodel.cn/api/paas/v4"
        
        try:
            headers = {
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": 65536
            }
            
            if thinking:
                data["thinking"] = {"type": "enabled"}
            
            response = requests.post(base_url + "/chat/completions", headers=headers, json=data)
            
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
            
            if "usage" in result:
                cache_hit = result["usage"].get("prompt_cache_hit_tokens", 0)
                cache_miss = result["usage"].get("prompt_cache_miss_tokens", 0)
                completion = result["usage"].get("completion_tokens", 0)
                SubAgent._update_tokens(cache_hit, cache_miss, completion)
            
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
    
    @staticmethod
    def call_deepseek(prompt: str, json_mode: bool = False, thinking: bool = False, api_key: str = None, model: str = None) -> str:
        api_key = api_key or DEEPSEEK_APIKEY
        if not api_key:
            raise ValueError("DeepSeek API key not found. Please set DEEPSEEK_APIKEY environment variable.")
        
        if thinking:
            model = DEFAULT_MODEL_REASONER
        else:
            model = model or DEFAULT_MODEL_DEEPSEEK
        
        base_url = "https://api.deepseek.com/v1"
        
        try:
            headers = {
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS
            }
            
            if json_mode and not thinking:
                data["response_format"] = {"type": "json_object"}
            
            response = requests.post(base_url + "/chat/completions", headers=headers, json=data)
            
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
            
            if "usage" in result:
                cache_hit = result["usage"].get("prompt_cache_hit_tokens", 0)
                cache_miss = result["usage"].get("prompt_cache_miss_tokens", 0)
                completion = result["usage"].get("completion_tokens", 0)
                SubAgent._update_tokens(cache_hit, cache_miss, completion)
            
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
    
    @staticmethod
    def _worker(prompt: str, result_queue: Queue, json_mode: bool, thinking: bool,
               api_key: str, model: str, index: int):
        result = SubAgent.call_deepseek(prompt, json_mode, thinking, api_key, model)
        result_queue.put((index, result))
    
    @staticmethod
    def parallel_call(prompts: List[str], json_mode: bool = False, thinking: bool = False,
                     api_key: str = None, model: str = None) -> List[str]:
        if not prompts:
            return []
        
        result_queue = Queue()
        threads = []
        
        for idx, prompt in enumerate(prompts):
            thread = Thread(target=SubAgent._worker, 
                          args=(prompt, result_queue, json_mode, thinking, api_key, model, idx))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        results = [None] * len(prompts)
        while not result_queue.empty():
            idx, result = result_queue.get()
            results[idx] = result
        
        return results
    
    @staticmethod
    def single_call(prompt: str, json_mode: bool = False, thinking: bool = False,
                   api_key: str = None, model: str = None) -> str:
        return SubAgent.call_deepseek(prompt, json_mode, thinking, api_key, model)
