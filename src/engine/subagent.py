import os
import time
import json
import sys
import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from threading import Lock

import config
import matilda_auth

load_dotenv()

DEEPSEEK_APIKEY = os.getenv('DEEPSEEK_APIKEY', '') or config.DEEPSEEK_APIKEY
DEFAULT_MODEL_DEEPSEEK = config.MODEL
DEFAULT_TEMPERATURE = config.TEMPERATURE
DEFAULT_MAX_TOKENS = config.MAX_TOKENS


MAX_RETRIES = config.MAX_RETRIES
RETRY_BACKOFF_SECONDS = config.RETRY_BACKOFF_SECONDS
REQUEST_TIMEOUT_SECONDS = config.REQUEST_TIMEOUT_SECONDS


class LLMCallError(RuntimeError):
    pass


class SubAgent:
    _lock = Lock()
    _total_prompt_cache_hit_tokens = 0
    _total_prompt_cache_miss_tokens = 0
    _total_completion_tokens = 0
    _current_concurrent = 0
    _peak_concurrent = 0



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
    def get_concurrency_stats():

        with SubAgent._lock:
            return SubAgent._current_concurrent, SubAgent._peak_concurrent



    @staticmethod
    def call_deepseek(prompt, json_mode=False, thinking=False, api_key=None, model=None):

        api_key = api_key or DEEPSEEK_APIKEY
        if not api_key:
            raise LLMCallError("DeepSeek API key is not configured; please set DEEPSEEK_APIKEY in .env")

        model = model or DEFAULT_MODEL_DEEPSEEK
        base_url = "https://api.deepseek.com/v1"

        headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": DEFAULT_MAX_TOKENS
        }

        if thinking:



            data["thinking"] = {"type": "enabled"}
            data["reasoning_effort"] = config.REASONING_EFFORT
        else:
            data["temperature"] = DEFAULT_TEMPERATURE

        if json_mode and not thinking:
            data["response_format"] = {"type": "json_object"}


        with SubAgent._lock:
            SubAgent._current_concurrent += 1
            if SubAgent._current_concurrent > SubAgent._peak_concurrent:
                SubAgent._peak_concurrent = SubAgent._current_concurrent
        try:
            response = requests.post(
                base_url + "/chat/completions",
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT_SECONDS
            )
        except requests.exceptions.RequestException as e:
            raise LLMCallError(f"DeepSeek network error: {e}") from e
        finally:
            with SubAgent._lock:
                SubAgent._current_concurrent -= 1

        if response.status_code != 200:
            raise LLMCallError(f"DeepSeek API error {response.status_code}: {response.text[:500]}")

        result = response.json()

        if "error" in result:
            raise LLMCallError(f"DeepSeek returned an error: {result['error'].get('message', result['error'])}")

        if "choices" not in result or not result["choices"]:
            raise LLMCallError("DeepSeek returned empty (no choices)")

        if "usage" in result:
            cache_hit = result["usage"].get("prompt_cache_hit_tokens", 0)
            cache_miss = result["usage"].get("prompt_cache_miss_tokens", 0)
            completion = result["usage"].get("completion_tokens", 0)
            SubAgent._update_tokens(cache_hit, cache_miss, completion)

        content = result["choices"][0]["message"]["content"].strip()
        content = _clean_json_response(content)

        reasoning_content = ""
        if thinking and "reasoning_content" in result["choices"][0]["message"]:
            reasoning_content = result["choices"][0]["message"]["reasoning_content"]

        return {
            "content": content,
            "reasoning_content": reasoning_content,
            "thinking": thinking
        }

    @staticmethod
    def call_matilda(prompt, json_mode=False, thinking=False, api_key=None, model=None, json_schema=None):

        # Matilda uses OAuth 2.0 device-flow authentication, not a static API key;
        # the json_mode/thinking/api_key/model arguments only keep the signature consistent with call_deepseek.
        # Standard OpenAI-compatible endpoint: POST /api/v1/chat/completions with response_format.
        base_url = config.MATILDA_API_BASE

        data = {
            "model": "matilda",
            "messages": [{"role": "user", "content": prompt}],
        }
        if json_mode:
            # Structured output via the standard OpenAI response_format parameter:
            # json_schema mode applies server-side grammar-constrained decoding; the
            # output is guaranteed to be valid JSON conforming to the schema.
            if json_schema:
                data["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {"name": "structured_output", "schema": json_schema},
                }
            else:
                data["response_format"] = {"type": "json_object"}

        with SubAgent._lock:
            SubAgent._current_concurrent += 1
            if SubAgent._current_concurrent > SubAgent._peak_concurrent:
                SubAgent._peak_concurrent = SubAgent._current_concurrent

        response = None
        try:
            headers = {
                "Authorization": "Bearer " + matilda_auth.get_access_token(),
                "Content-Type": "application/json",
                "X-Matilda-API-Version": config.MATILDA_API_VERSION,
            }

            response = requests.post(
                base_url + "/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=(30, 120)
            )

            if response.status_code in (401, 403):
                # Token may be invalid/unauthorized: force a refresh and retry once
                matilda_auth.force_refresh()
                headers["Authorization"] = "Bearer " + matilda_auth.get_access_token()
                response = requests.post(
                    base_url + "/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=(30, 120)
                )

            if response.status_code != 200:
                text = response.text[:500]
                raise LLMCallError(f"Matilda API error {response.status_code}: {text}")

            result = response.json()
            if "error" in result:
                err = result["error"]
                raise LLMCallError(f"Matilda returned error: {err.get('message', err)}")
            choices = result.get("choices")
            if not choices or not choices[0].get("message", {}).get("content"):
                raise LLMCallError("Matilda returned empty response (no choices)")

            usage = result.get("usage") or {}
            completion = int(usage.get("completion_tokens", 0) or 0)
            SubAgent._update_tokens(0, 0, completion)

            content = choices[0]["message"]["content"].strip()
            content = _clean_json_response(content)

        except requests.exceptions.RequestException as e:
            raise LLMCallError(f"Matilda network error: {e}") from e
        except matilda_auth.LLMCallError as e:
            raise LLMCallError(str(e)) from e
        finally:
            with SubAgent._lock:
                SubAgent._current_concurrent -= 1

        return {
            "content": content,
            "reasoning_content": "",
            "thinking": thinking
        }

    @staticmethod
    def call_with_retry(prompt, json_mode=False, thinking=False, api_key=None, model=None, provider=None,
                        json_schema=None):

        provider = (provider or config.LLM_PROVIDER or "deepseek").lower()
        call_fn = SubAgent.call_matilda if provider == "matilda" else SubAgent.call_deepseek

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                if provider == "matilda":
                    return call_fn(prompt, json_mode, thinking, api_key, model, json_schema=json_schema)
                return call_fn(prompt, json_mode, thinking, api_key, model)
            except LLMCallError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF_SECONDS * (2 ** attempt)
                    print(f"[Retry] {provider} call failed (attempt {attempt + 1}): {e} -> retrying in {wait}s")
                    time.sleep(wait)
        raise LLMCallError(f"{provider} call failed (gave up after {MAX_RETRIES} retries): {last_error}")



    @staticmethod
    def parallel_call(prompts, json_mode=False, thinking=False, api_key=None, model=None, provider=None,
                      json_schema=None):




        if not prompts:
            return []

        results = [None] * len(prompts)
        failure = {}

        def _run(index, prompt):
            try:
                return index, SubAgent.call_with_retry(prompt, json_mode, thinking, api_key, model, provider,
                                                       json_schema=json_schema)
            except LLMCallError as e:
                failure["index"] = index
                failure["error"] = e
                return index, None

        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            futures = {
                executor.submit(_run, idx, prompt): idx
                for idx, prompt in enumerate(prompts)
            }
            for future in futures:
                index, result = future.result()
                results[index] = result

        if "error" in failure:
            raise LLMCallError(
                f"Parallel call failed: prompt index {failure['index']} -> {failure['error']}"
            )

        return results

    @staticmethod
    def single_call(prompt, json_mode=False, thinking=False, api_key=None, model=None, provider=None,
                    json_schema=None):

        return SubAgent.call_with_retry(prompt, json_mode, thinking, api_key, model, provider,
                                        json_schema=json_schema)


def _clean_json_response(text):

    from . import utils
    return utils.clean_json_text(text)
