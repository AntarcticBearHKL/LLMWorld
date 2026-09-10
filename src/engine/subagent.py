import os
import copy
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from dotenv import load_dotenv
from threading import BoundedSemaphore, Lock
from uuid import uuid4

import config

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


_STRICT_DROP_KEYS = (
    "minItems", "maxItems", "uniqueItems", "minLength", "maxLength", "pattern",
    "format", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "multipleOf", "default", "title", "examples",
)


def _to_strict_schema(schema):
    """DeepSeek strict structured output requires additionalProperties=false and every
    property listed in required; unsupported validation keywords must be stripped."""
    if isinstance(schema, list):
        return [_to_strict_schema(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    out = copy.deepcopy(schema)
    for key in _STRICT_DROP_KEYS:
        out.pop(key, None)
    properties = out.get("properties")
    if out.get("type") == "object":
        out["additionalProperties"] = False
        if isinstance(properties, dict):
            out["required"] = list(properties.keys())
    if isinstance(properties, dict):
        out["properties"] = {key: _to_strict_schema(value) for key, value in properties.items()}
    if "items" in out:
        out["items"] = _to_strict_schema(out["items"])
    for key in ("anyOf", "oneOf", "allOf"):
        if isinstance(out.get(key), list):
            out[key] = [_to_strict_schema(item) for item in out[key]]
    return out


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
    def call_deepseek(prompt, json_mode=False, thinking=None, api_key=None, model=None, json_schema=None):
        if thinking is None:
            thinking = config.THINKING
        api_key = api_key or DEEPSEEK_APIKEY
        if not api_key:
            raise LLMCallError("DeepSeek API key is not configured; please set DEEPSEEK_APIKEY in .env")

        model = model or DEFAULT_MODEL_DEEPSEEK
        endpoint = config.DEEPSEEK_API_BASE.rstrip("/") + "/responses"
        use_schema = bool(json_mode and json_schema)

        headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "input": prompt,
            "max_output_tokens": DEFAULT_MAX_TOKENS
        }

        if thinking:
            data["reasoning"] = {"effort": config.REASONING_EFFORT}
        else:
            data["temperature"] = DEFAULT_TEMPERATURE

        if use_schema:
            data["text"] = {"format": {
                "type": "json_schema",
                "name": "response",
                "schema": _to_strict_schema(json_schema),
            }}
        elif json_mode:
            data["text"] = {"format": {"type": "json_object"}}

        logical_call_id = uuid4().hex
        trace_started_at = datetime.now(timezone.utc).isoformat()
        trace_started = time.perf_counter()
        trace_meta = {"request_index": 1, "request_count": 1}
        sent_prompt = prompt
        request_body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        def trace(response=None, result=None, error=None):
            _append_llm_trace({
                "provider": "deepseek",
                "logical_call_id": logical_call_id,
                "request_index": trace_meta["request_index"],
                "request_count": trace_meta["request_count"],
                "transport_mode": "openai_responses",
                "prompt_chars": len(sent_prompt),
                "prompt_segmented": False,
                "started_at": trace_started_at,
                "duration_seconds": round(time.perf_counter() - trace_started, 6),
                "request_body_bytes": len(request_body),
                "http_status": response.status_code if response is not None else None,
                "request": data,
                "response": result,
                "error": error,
            })

        def _post(body):
            SubAgent._request_slots.acquire()
            with SubAgent._lock:
                SubAgent._current_concurrent += 1
                if SubAgent._current_concurrent > SubAgent._peak_concurrent:
                    SubAgent._peak_concurrent = SubAgent._current_concurrent
            try:
                return requests.post(
                    endpoint,
                    headers=headers,
                    json=body,
                    timeout=REQUEST_TIMEOUT_SECONDS
                )
            finally:
                with SubAgent._lock:
                    SubAgent._current_concurrent -= 1
                SubAgent._request_slots.release()

        try:
            response = _post(data)
        except requests.exceptions.RequestException as e:
            trace(error=f"{type(e).__name__}: {e}")
            raise LLMCallError(f"DeepSeek network error: {e}", retryable=True) from e

        # Some accounts/models may reject json_schema; retry once with json_object and
        # the schema injected into the prompt so the pipeline never hard-breaks.
        if use_schema and response.status_code == 400:
            print("[Fallback] DeepSeek rejected json_schema (HTTP 400); retrying with json_object and the schema injected into the prompt")
            trace_meta["request_index"] = 2
            trace_meta["request_count"] = 2
            sent_prompt = (
                prompt
                + "\n\n## Output JSON Schema\n"
                + "Return a JSON object conforming EXACTLY to this schema (use the exact field names):\n"
                + json.dumps(json_schema, ensure_ascii=False)
            )
            data = {
                "model": model,
                "input": sent_prompt,
                "max_output_tokens": DEFAULT_MAX_TOKENS,
                "text": {"format": {"type": "json_object"}}
            }
            if thinking:
                data["reasoning"] = {"effort": config.REASONING_EFFORT}
            else:
                data["temperature"] = DEFAULT_TEMPERATURE
            request_body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            try:
                response = _post(data)
            except requests.exceptions.RequestException as e:
                trace(error=f"{type(e).__name__}: {e}")
                raise LLMCallError(f"DeepSeek network error: {e}", retryable=True) from e

        if response.status_code != 200:
            trace(response=response, result={"raw_text": response.text})
            raise LLMCallError(
                f"DeepSeek API error {response.status_code}: {response.text[:500]}",
                retryable=response.status_code == 429 or response.status_code >= 500,
            )

        result = response.json()

        if result.get("error"):
            error = result["error"]
            detail = error.get("message", error) if isinstance(error, dict) else error
            trace(response=response, result=result, error=str(detail))
            raise LLMCallError(f"DeepSeek returned an error: {detail}")

        if result.get("status") == "failed":
            detail = result.get("incomplete_details") or "status=failed"
            trace(response=response, result=result, error=str(detail))
            raise LLMCallError(f"DeepSeek Responses request failed: {detail}")

        content = ""
        reasoning = ""
        for item in result.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []) or []:
                    if part.get("type") == "output_text":
                        content += part.get("text", "")
            elif item.get("type") == "reasoning":
                for part in item.get("content", []) or []:
                    if part.get("type") == "reasoning_text":
                        reasoning += part.get("text", "")

        from . import utils
        content = utils.clean_json_text(content.strip())
        if not content:
            trace(response=response, result=result, error="empty output")
            raise LLMCallError("DeepSeek Responses returned empty output")

        usage = result.get("usage") or {}
        cached_tokens = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0
        input_tokens = usage.get("input_tokens", 0) or 0
        output_tokens = usage.get("output_tokens", 0) or 0
        SubAgent._update_tokens(cached_tokens, input_tokens - cached_tokens, output_tokens)

        trace(response=response, result={
            "content": content,
            "reasoning_content": reasoning,
            "usage": usage,
            "model": result.get("model", model),
            "id": result.get("id"),
        })

        return {"content": content, "reasoning_content": reasoning, "thinking": thinking}

    @staticmethod
    def call_with_retry(prompt, json_mode=False, thinking=None, api_key=None, model=None,
                        json_schema=None):
        return SubAgent.call_deepseek(prompt, json_mode, thinking, api_key, model, json_schema)

    @staticmethod
    def parallel_call(prompts, json_mode=False, thinking=None, api_key=None, model=None,
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
    def single_call(prompt, json_mode=False, thinking=None, api_key=None, model=None,
                    json_schema=None):
        return SubAgent.call_with_retry(prompt, json_mode, thinking, api_key, model,
                                        json_schema=json_schema)
