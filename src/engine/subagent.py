import os
import subprocess
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from dotenv import load_dotenv
from threading import BoundedSemaphore, Lock
from uuid import uuid4

import config
import matilda_auth

load_dotenv()

DEEPSEEK_APIKEY = os.getenv('DEEPSEEK_APIKEY', '') or config.DEEPSEEK_APIKEY
DEFAULT_MODEL_DEEPSEEK = config.MODEL
DEFAULT_TEMPERATURE = config.TEMPERATURE
DEFAULT_MAX_TOKENS = config.MAX_TOKENS

REQUEST_TIMEOUT_SECONDS = config.REQUEST_TIMEOUT_SECONDS
LLM_MAX_CONCURRENCY = config.LLM_MAX_CONCURRENCY


class LLMCallError(RuntimeError):
    def __init__(self, message, *, retryable=False, code=None):
        super().__init__(message)
        self.retryable = retryable
        self.code = code


_TRACE_LOCK = Lock()


def _append_llm_trace(entry):
    path = os.getenv("LLM_TRACE_FILE", "").strip()
    if not path:
        return
    try:
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        record = {
            "trace_version": 1,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            **entry,
        }
        with _TRACE_LOCK:
            with open(path, "a", encoding="utf-8") as trace_file:
                trace_file.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[Trace warning] could not append LLM trace: {exc}")


class SubAgent:
    _lock = Lock()
    _request_slots = BoundedSemaphore(LLM_MAX_CONCURRENCY)
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
    def call_deepseek(prompt, json_mode=False, thinking=False, api_key=None, model=None, json_schema=None):
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

        logical_call_id = uuid4().hex
        trace_started_at = datetime.now(timezone.utc).isoformat()
        trace_started = time.perf_counter()
        request_body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        def trace(response=None, result=None, error=None):
            _append_llm_trace({
                "provider": "deepseek",
                "logical_call_id": logical_call_id,
                "request_index": 1,
                "request_count": 1,
                "transport_mode": "openai_chat_completions",
                "prompt_chars": len(prompt),
                "prompt_segmented": False,
                "started_at": trace_started_at,
                "duration_seconds": round(time.perf_counter() - trace_started, 6),
                "request_body_bytes": len(request_body),
                "http_status": response.status_code if response is not None else None,
                "request": data,
                "response": result,
                "error": error,
            })

        SubAgent._request_slots.acquire()
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
            trace(error=f"{type(e).__name__}: {e}")
            raise LLMCallError(f"DeepSeek network error: {e}", retryable=True) from e
        finally:
            with SubAgent._lock:
                SubAgent._current_concurrent -= 1
            SubAgent._request_slots.release()

        if response.status_code != 200:
            trace(response=response, result={"raw_text": response.text})
            raise LLMCallError(
                f"DeepSeek API error {response.status_code}: {response.text[:500]}",
                retryable=response.status_code == 429 or response.status_code >= 500,
            )

        result = response.json()

        if "error" in result:
            trace(response=response, result=result, error=str(result["error"]))
            raise LLMCallError(f"DeepSeek returned an error: {result['error'].get('message', result['error'])}")

        if "choices" not in result or not result["choices"]:
            trace(response=response, result=result, error="no choices")
            raise LLMCallError("DeepSeek returned empty (no choices)")

        if "usage" in result:
            cache_hit = result["usage"].get("prompt_cache_hit_tokens", 0)
            cache_miss = result["usage"].get("prompt_cache_miss_tokens", 0)
            completion = result["usage"].get("completion_tokens", 0)
            SubAgent._update_tokens(cache_hit, cache_miss, completion)

        content = result["choices"][0]["message"]["content"].strip()
        from . import utils
        content = utils.clean_json_text(content)

        trace(response=response, result={
            "content": content,
            "usage": result.get("usage", {}),
            "model": result.get("model", model),
            "id": result.get("id"),
        })

        return {"content": content, "reasoning_content": "", "thinking": thinking}

    @staticmethod
    def call_matilda(prompt, json_mode=False, thinking=False, api_key=None, model=None, json_schema=None):
        """Black-box: prompt + json_schema -> LLM raw return content."""
        del api_key, model
        logical_call_id = uuid4().hex
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bridge_path = os.path.join(project_root, "matilda", "agent_bridge.mjs")
        try:
            access_token = matilda_auth.get_access_token()
        except matilda_auth.LLMCallError as exc:
            raise LLMCallError(f"Matilda authentication failed: {exc}", code="authentication") from exc
        request_data = {
            "baseUrl": config.MATILDA_API_BASE,
            "apiVersion": config.MATILDA_API_VERSION,
            "accessToken": access_token,
            "prompt": prompt,
            "jsonMode": bool(json_mode),
            "thinking": bool(thinking),
            "jsonSchema": json_schema,
        }
        trace_request = {key: value for key, value in request_data.items() if key != "accessToken"}
        started_at = datetime.now(timezone.utc).isoformat()
        started = time.perf_counter()
        payload = json.dumps(request_data, ensure_ascii=False, separators=(",", ":"))

        SubAgent._request_slots.acquire()
        with SubAgent._lock:
            SubAgent._current_concurrent += 1
            if SubAgent._current_concurrent > SubAgent._peak_concurrent:
                SubAgent._peak_concurrent = SubAgent._current_concurrent
        try:
            completed = subprocess.run(
                ["node", bridge_path],
                input=payload,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except OSError as exc:
            raise LLMCallError(f"Could not start Matilda Agent SDK bridge: {exc}", code="sdk_bridge_start") from exc
        except subprocess.TimeoutExpired as exc:
            raise LLMCallError(f"Matilda Agent SDK bridge timed out after {REQUEST_TIMEOUT_SECONDS}s", code="timeout") from exc
        finally:
            with SubAgent._lock:
                SubAgent._current_concurrent -= 1
            SubAgent._request_slots.release()

        try:
            bridge_result = json.loads(completed.stdout)
        except (json.JSONDecodeError, ValueError) as exc:
            error = completed.stderr.strip() or completed.stdout[:500]
            _append_llm_trace({
                "provider": "matilda", "logical_call_id": logical_call_id,
                "transport_mode": "official_agent_sdk", "prompt_chars": len(prompt),
                "started_at": started_at,
                "duration_seconds": round(time.perf_counter() - started, 6),
                "request": trace_request, "response": None,
                "error": f"Invalid bridge response: {error}",
            })
            raise LLMCallError(
                f"Matilda Agent SDK bridge returned invalid JSON: {error}",
                code="sdk_bridge_protocol",
            ) from exc

        _append_llm_trace({
            "provider": "matilda", "logical_call_id": logical_call_id,
            "transport_mode": "official_agent_sdk", "prompt_chars": len(prompt),
            "started_at": started_at,
            "duration_seconds": round(time.perf_counter() - started, 6),
            "request": trace_request, "response": bridge_result,
            "error": None if bridge_result.get("ok") else bridge_result.get("error"),
        })
        if not bridge_result.get("ok"):
            detail = bridge_result.get("error") or {}
            code = detail.get("code") or detail.get("name") or "unknown"
            raw = detail.get("raw")
            raw_note = f"; raw output: {raw[:500]}" if isinstance(raw, str) and raw else ""
            raise LLMCallError(
                f"Matilda Agent SDK error [{code}]: {detail.get('message', detail)}{raw_note}",
                retryable=False,
                code=code,
            )

        usage = bridge_result.get("usage") or {}
        SubAgent._update_tokens(0, 0, int(usage.get("output_tokens", 0) or 0))
        content = bridge_result.get("content")
        if not isinstance(content, str) or not content.strip():
            raise LLMCallError("Matilda Agent SDK returned empty output", code="empty_response")
        return {
            "content": content.strip(),
            "reasoning_content": "",
            "thinking": thinking,
            "object": bridge_result.get("object"),
        }

    @staticmethod
    def call_with_retry(prompt, json_mode=False, thinking=False, api_key=None, model=None, provider=None,
                        json_schema=None):
        provider = (provider or config.LLM_PROVIDER or "deepseek").lower()
        call_fn = SubAgent.call_matilda if provider == "matilda" else SubAgent.call_deepseek
        return call_fn(prompt, json_mode, thinking, api_key, model, json_schema)

    @staticmethod
    def parallel_call(prompts, json_mode=False, thinking=False, api_key=None, model=None, provider=None,
                      json_schema=None):
        if isinstance(prompts, str):
            raise TypeError("parallel_call expects an iterable of prompt strings; use single_call for one string")
        prompts = list(prompts)
        if not prompts:
            return []
        for index, prompt in enumerate(prompts):
            if not isinstance(prompt, str):
                raise TypeError(f"prompts[{index}] must be str, got {type(prompt).__name__}")

        results = [None] * len(prompts)

        def _run(index, prompt):
            try:
                result = SubAgent.call_with_retry(
                    prompt,
                    json_mode,
                    thinking,
                    api_key,
                    model,
                    provider,
                    json_schema=json_schema,
                )
                return index, result, None
            except LLMCallError as e:
                return index, None, e

        failures = []
        max_workers = min(len(prompts), LLM_MAX_CONCURRENCY)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(_run, index, prompt)
                for index, prompt in enumerate(prompts)
            ]
            for future in futures:
                index, result, error = future.result()
                results[index] = result
                if error is not None:
                    failures.append((index, error))

        if failures:
            index, error = min(failures, key=lambda item: item[0])
            raise LLMCallError(
                f"Parallel call failed: prompt index {index} -> {error}"
            )

        return results

    @staticmethod
    def single_call(prompt, json_mode=False, thinking=False, api_key=None, model=None, provider=None,
                    json_schema=None):
        return SubAgent.call_with_retry(prompt, json_mode, thinking, api_key, model, provider,
                                        json_schema=json_schema)
