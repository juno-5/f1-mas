"""MAS Agent Runner — ThreadPoolExecutor + xapi inference API.

Uses xapi /inference/chat endpoint which proxies through FAS Gateway (port 18789).
Token management, usage tracking, and rate limiting handled automatically by FAS Gateway.

Supports tool-use: when agents are given tools, the runner executes a multi-turn loop
(LLM → tool_calls → execute → feed results → LLM → ... → final text).
"""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future

import httpx

from . import mas_config as cfg
from . import mas_state as state
from .mas_constitution import filter_output

_pool: ThreadPoolExecutor | None = None

# Global inference concurrency limiter — prevents xapi overload when multiple
# requests burst simultaneously.  Each slot = 1 concurrent inference call
# (batch or individual).
# Cycle #51: backpressure mechanism for burst protection.
_inference_semaphore: threading.Semaphore | None = None
_inference_sem_size: int = 0
_inference_sem_lock = threading.Lock()


def _get_inference_semaphore() -> threading.Semaphore:
    """Return global inference semaphore (lazy init, thread-safe).

    max_concurrent_inferences (default 3): how many concurrent inference calls
    (batch or individual) can run at once across all requests.
    """
    global _inference_semaphore, _inference_sem_size
    target = cfg.get("max_concurrent_inferences", 3)
    with _inference_sem_lock:
        if _inference_semaphore is None or _inference_sem_size != target:
            _inference_semaphore = threading.Semaphore(target)
            _inference_sem_size = target
        return _inference_semaphore

# Shared httpx client — connection pooling for xapi calls
_http: httpx.Client | None = None


def _get_http() -> httpx.Client:
    """Return shared httpx.Client with connection pooling (keep-alive reuse)."""
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=5.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
    return _http


# Model short name → full model ID
_MODEL_MAP = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}

_RATE_LIMIT_PATTERNS = [
    "hit your limit",
    "rate limit",
    "too many requests",
    "resets ",         # "resets 5am (UTC)"
    "Not logged in",   # token revoked/expired
]

# Complex task indicators — queries matching these use sonnet instead of haiku
# Strong complexity signals: single match → sonnet
_SONNET_STRONG = [
    "심층", "상세", "종합", "아키텍처", "architecture",
    "deep dive", "comprehensive", "in-depth", "pros and cons",
]
# Weak complexity signals: need 2+ matches for sonnet
_SONNET_WEAK = [
    "분석", "전략", "기획", "설계", "리뷰", "비교",
    "analyze", "strategy", "plan", "review", "compare", "detailed",
]


def select_model(query: str, has_tools: bool = False) -> str:
    """Auto-select model based on query complexity.

    Returns 'haiku' for simple tasks, 'sonnet' for complex ones.
    Requires auto_model_enabled=true in config; otherwise returns config default.

    Scoring: strong signal (1+) → sonnet, weak signals (2+) → sonnet,
    long query (>200 chars) with any weak signal → sonnet, else → haiku.
    """
    if not cfg.get("auto_model_enabled", False):
        return cfg.get("claude_model", "sonnet")

    # Tool-use requires more capable model (multi-turn reasoning)
    if has_tools:
        return "sonnet"

    query_lower = query.lower()

    # Strong indicators: single match → sonnet
    if any(ind in query_lower for ind in _SONNET_STRONG):
        return "sonnet"

    # Weak indicators: count matches
    weak_count = sum(1 for ind in _SONNET_WEAK if ind in query_lower)

    # 2+ weak signals → sonnet (multi-faceted task)
    if weak_count >= 2:
        return "sonnet"

    # Long query with any weak signal → sonnet (detailed request)
    if weak_count >= 1 and len(query) > 200:
        return "sonnet"

    # Default: haiku (single weak signal or no signals)
    return "haiku"


def _get_pool() -> ThreadPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ThreadPoolExecutor(
            max_workers=cfg.get("thread_pool_workers", 5),
            thread_name_prefix="mas-agent",
        )
    return _pool


def _is_rate_limit_error(error_msg: str) -> bool:
    """Detect if an error indicates token rate-limiting or expiry."""
    lower = error_msg.lower()
    return any(p.lower() in lower for p in _RATE_LIMIT_PATTERNS)


def _select_inference_endpoint(has_tools: bool = False) -> str:
    """Select inference endpoint based on config.

    Returns "chat" (Gateway) or "raw" (direct Anthropic API).
    Tool-use always requires "chat" (Gateway handles tool execution context).
    """
    if has_tools:
        return "chat"
    mode = cfg.get("inference_mode", "gateway")
    if mode == "direct":
        return "raw"
    return "chat"


def call_xapi_inference(prompt: str, model: str = None, timeout: int = None,
                        user: str = "mas:agent", max_tokens: int = 8192,
                        force_direct: bool = False) -> dict:
    """Call LLM via xapi — Gateway (/chat) or direct Anthropic (/raw).

    When inference_mode="direct" in config (or force_direct=True), uses /inference/raw
    which bypasses Gateway entirely → 96% token reduction for MAS inference.

    Returns {"text": str, "model": str, "error": str|None,
             "usage": {"input": int, "output": int, "cacheRead": int, "cacheWrite": int},
             "cost_usd": float}.
    """
    if model is None:
        model = cfg.get("claude_model", "sonnet")
    full_model = _MODEL_MAP.get(model, model)

    if timeout is None:
        timeout = cfg.get("agent_timeout_seconds", 120)

    xapi_url = cfg.get("xapi_url", "http://localhost:7750")
    empty_usage = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}

    endpoint = "raw" if force_direct else _select_inference_endpoint()

    max_retries = cfg.get("inference_max_retries", 3)
    last_error = ""
    for attempt in range(max_retries):
        try:
            resp = _get_http().post(
                f"{xapi_url}/inference/{endpoint}",
                json={
                    "model": full_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "user": user,
                    "max_tokens": max_tokens,
                },
                timeout=timeout,
            )

            if resp.status_code in (502, 503) and attempt < max_retries - 1:
                wait = 5 * (attempt + 1)  # 5s, 10s, 15s
                print(f"[agent-runner] xapi {resp.status_code}, retrying in {wait}s (attempt {attempt + 1}/{max_retries})...", flush=True)
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                error = resp.text[:300]
                return {"text": "", "model": full_model, "error": f"xapi {resp.status_code}: {error}",
                        "usage": empty_usage, "cost_usd": 0.0}

            data = resp.json()
            raw_usage = data.get("usage", {})
            # Cache tokens: try Anthropic format first, then OpenAI prompt_tokens_details
            cache_read = raw_usage.get("cache_read_input_tokens", 0)
            cache_write = raw_usage.get("cache_creation_input_tokens", 0)
            if not cache_read:
                details = raw_usage.get("prompt_tokens_details", {}) or {}
                cache_read = details.get("cached_tokens", 0)
                cache_write = cache_write or details.get("cache_creation_tokens", 0)
            usage = {
                "input": raw_usage.get("input_tokens", raw_usage.get("prompt_tokens", 0)),
                "output": raw_usage.get("output_tokens", raw_usage.get("completion_tokens", 0)),
                "cacheRead": cache_read,
                "cacheWrite": cache_write,
            }

            return {
                "text": data.get("content", ""),
                "model": data.get("model", full_model),
                "error": None,
                "usage": usage,
                "cost_usd": data.get("cost_usd", 0.0),
            }

        except httpx.TimeoutException:
            return {"text": "", "model": full_model, "error": f"timeout after {timeout}s",
                    "usage": empty_usage, "cost_usd": 0.0}
        except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f"[agent-runner] xapi connect error, retrying in {wait}s (attempt {attempt + 1}/{max_retries})...", flush=True)
                time.sleep(wait)
                continue
            return {"text": "", "model": full_model, "error": f"xapi unreachable at {xapi_url} (after {max_retries} attempts)",
                    "usage": empty_usage, "cost_usd": 0.0}
        except Exception as e:
            return {"text": "", "model": full_model, "error": str(e),
                    "usage": empty_usage, "cost_usd": 0.0}
    return {"text": "", "model": full_model, "error": last_error,
            "usage": empty_usage, "cost_usd": 0.0}


import re

_TOOL_CALL_RE = re.compile(
    r"<tool_call>\s*(\{.*?\})\s*</tool_call>",
    re.DOTALL,
)


def _build_tool_instructions(tools: list[dict]) -> str:
    """Build text-based tool instructions from OpenAI tool definitions."""
    lines = [
        "\n\n---",
        "## Available Tools",
        "You have access to the following tools. To use a tool, output EXACTLY this format:",
        "",
        "<tool_call>",
        '{"name": "tool_name", "arguments": {"arg1": "value1"}}',
        "</tool_call>",
        "",
        "You may call multiple tools. After each <tool_call>, stop and wait for the result.",
        "The result will appear in a <tool_result> block. Then continue your response.",
        "If you don't need any tools, respond normally WITHOUT any <tool_call> tags.",
        "",
    ]
    for t in tools:
        fn = t.get("function", {})
        name = fn.get("name", "")
        desc = fn.get("description", "")
        params = fn.get("parameters", {}).get("properties", {})
        required = fn.get("parameters", {}).get("required", [])

        param_strs = []
        for pname, pdef in params.items():
            ptype = pdef.get("type", "string")
            pdesc = pdef.get("description", "")
            req = " (required)" if pname in required else ""
            param_strs.append(f"    - {pname}: {ptype}{req} — {pdesc}")

        lines.append(f"### {name}")
        lines.append(f"{desc}")
        if param_strs:
            lines.append("  Parameters:")
            lines.extend(param_strs)
        else:
            lines.append("  No parameters.")
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


def call_xapi_with_tools(
    prompt: str,
    tools: list[dict],
    model: str = None,
    timeout: int = None,
    user: str = "mas:agent",
    max_tool_rounds: int = 5,
) -> dict:
    """Call LLM with text-based tool-use loop (ReAct pattern).

    Uses existing xapi/Gateway infrastructure. Tools are described as text in the
    prompt. When the LLM outputs <tool_call> blocks, we parse them, execute the
    tools locally, inject <tool_result> blocks, and re-call until the LLM gives
    a final answer without tool calls.

    Returns same format as call_xapi_inference.
    """
    from .mas_tools import execute_tool as exec_tool

    if model is None:
        model = cfg.get("claude_model", "sonnet")

    if timeout is None:
        timeout = cfg.get("agent_timeout_seconds", 120)

    # Inject tool descriptions into the prompt
    tool_instructions = _build_tool_instructions(tools)
    augmented_prompt = prompt + tool_instructions

    total_usage = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
    total_cost = 0.0
    conversation = augmented_prompt

    for round_i in range(max_tool_rounds + 1):
        result = call_xapi_inference(conversation, model=model, timeout=timeout, user=user)

        if result.get("error"):
            result["usage"] = _merge_usage(total_usage, result.get("usage", {}))
            result["cost_usd"] = total_cost + result.get("cost_usd", 0.0)
            return result

        # Accumulate usage
        ru = result.get("usage", {})
        total_usage["input"] += ru.get("input", 0)
        total_usage["output"] += ru.get("output", 0)
        total_usage["cacheRead"] += ru.get("cacheRead", 0)
        total_usage["cacheWrite"] += ru.get("cacheWrite", 0)
        total_cost += result.get("cost_usd", 0.0)

        text = result.get("text", "")

        # Parse tool calls from text
        tool_calls = _TOOL_CALL_RE.findall(text)

        if not tool_calls:
            # No tool calls → final response
            return {
                "text": text,
                "model": result.get("model", ""),
                "error": None,
                "usage": total_usage,
                "cost_usd": total_cost,
            }

        # Execute tool calls
        print(f"[agent-runner] Tool round {round_i + 1}: "
              f"{len(tool_calls)} call(s)", flush=True)

        tool_results = []
        for tc_json in tool_calls:
            try:
                tc = json.loads(tc_json)
                tool_name = tc.get("name", "")
                tool_args = tc.get("arguments", {})
            except (json.JSONDecodeError, TypeError):
                tool_results.append("<tool_result>\n{\"error\": \"Invalid tool call JSON\"}\n</tool_result>")
                continue

            print(f"[agent-runner]   -> {tool_name}"
                  f"({json.dumps(tool_args, ensure_ascii=False)[:100]})",
                  flush=True)
            tool_result = exec_tool(tool_name, tool_args)
            print(f"[agent-runner]   <- {len(tool_result)} chars", flush=True)

            tool_results.append(
                f"<tool_result name=\"{tool_name}\">\n{tool_result}\n</tool_result>"
            )

        # Build continuation prompt: original + assistant response + tool results
        # Strip tool_call blocks from assistant text for cleaner context
        clean_text = _TOOL_CALL_RE.sub("", text).strip()
        continuation = (
            f"{conversation}\n\n"
            f"## Assistant Response\n{clean_text}\n\n"
            f"## Tool Results\n" + "\n\n".join(tool_results) + "\n\n"
            f"Continue your response using the tool results above. "
            f"Do NOT repeat the tool calls."
        )
        conversation = continuation

    # Max rounds exceeded — return last text
    clean_text = _TOOL_CALL_RE.sub("", text).strip() if 'text' in dir() else ""
    return {"text": clean_text, "model": result.get("model", "") if 'result' in dir() else "",
            "error": f"max tool rounds ({max_tool_rounds}) exceeded",
            "usage": total_usage, "cost_usd": total_cost}


def _merge_usage(total: dict, new: dict) -> dict:
    """Merge usage dicts."""
    return {
        "input": total.get("input", 0) + new.get("input", 0),
        "output": total.get("output", 0) + new.get("output", 0),
        "cacheRead": total.get("cacheRead", 0) + new.get("cacheRead", 0),
        "cacheWrite": total.get("cacheWrite", 0) + new.get("cacheWrite", 0),
    }


def run_agent(
    request_id: str,
    agent_id: str,
    prompt: str,
    persona_id: str,
    callsign: str,
    tools: list[dict] | None = None,
    query: str = "",
) -> dict:
    """Execute a single agent via xapi inference.

    Args:
        tools: Optional OpenAI function-calling tool definitions. When provided,
            uses tool-use loop (LLM → tool_calls → execute → feed back → repeat).
        query: Original user query (for auto model selection).

    Returns {"text": str, "tokens_used": int, "model": str, "duration_ms": int}.
    """
    start = time.time()
    state.update_agent(request_id, agent_id,
                       status="running", started_at=start)

    model = select_model(query, has_tools=bool(tools)) if query else cfg.get("claude_model", "sonnet")
    # Include request_id in user field to ensure each MAS request gets a fresh
    # Gateway session (prevents session history accumulation across requests).
    # Use persona_id (always ASCII) instead of callsign to avoid HTTP header
    # encoding errors with non-ASCII names (Korean/Japanese personas).
    user_tag = f"mas:{request_id[:8]}:{persona_id}"

    if tools:
        print(f"[agent-runner] {callsign} calling xapi inference "
              f"with {len(tools)} tools...", flush=True)
        result = call_xapi_with_tools(prompt, tools, model=model, user=user_tag)
    else:
        print(f"[agent-runner] {callsign} calling xapi inference (model={model})...", flush=True)
        result = call_xapi_inference(prompt, model=model, user=user_tag)

    duration_ms = int((time.time() - start) * 1000)

    if result.get("error"):
        error_msg = result["error"]
        partial_text = filter_output(result.get("text", "")).strip()

        # If there's usable text despite the error (e.g. max tool rounds exceeded),
        # treat as partial success rather than discarding the work.
        if partial_text:
            usage = result.get("usage", {})
            tokens_used = usage.get("input", 0) + usage.get("output", 0)
            cost_usd = result.get("cost_usd", 0.0)
            print(f"[agent-runner] {callsign} partial ({duration_ms}ms, {len(partial_text)} chars, "
                  f"{tokens_used} tokens, ${cost_usd:.4f}) — {error_msg}", flush=True)
            state.update_agent(request_id, agent_id,
                               status="completed",
                               output=partial_text,
                               tokens_used=tokens_used,
                               model=model,
                               cost_usd=cost_usd)
            return {
                "text": partial_text,
                "tokens_used": tokens_used,
                "model": model,
                "duration_ms": duration_ms,
                "error": None,
            }

        print(f"[agent-runner] {callsign} error: {error_msg}", flush=True)

        if _is_rate_limit_error(error_msg):
            print(f"[agent-runner] Rate limit detected for {callsign}", flush=True)

        state.update_agent(request_id, agent_id,
                           status="failed", error=error_msg, model=model)
        return {
            "text": "",
            "tokens_used": 0,
            "model": model,
            "duration_ms": duration_ms,
            "error": error_msg,
        }

    text = filter_output(result["text"])
    usage = result.get("usage", {})
    tokens_used = usage.get("input", 0) + usage.get("output", 0)
    cost_usd = result.get("cost_usd", 0.0)

    if not text.strip():
        error_msg = "empty response from inference"
        print(f"[agent-runner] {callsign} empty response ({duration_ms}ms)", flush=True)
        state.update_agent(request_id, agent_id,
                           status="failed", error=error_msg, model=model)
        return {
            "text": "",
            "tokens_used": tokens_used,
            "model": model,
            "duration_ms": duration_ms,
            "error": error_msg,
        }

    print(f"[agent-runner] {callsign} completed ({duration_ms}ms, {len(text)} chars, "
          f"{tokens_used} tokens, ${cost_usd:.4f})", flush=True)

    state.update_agent(request_id, agent_id,
                       status="completed",
                       output=text,
                       tokens_used=tokens_used,
                       model=model,
                       cost_usd=cost_usd)

    return {
        "text": text,
        "tokens_used": tokens_used,
        "model": model,
        "duration_ms": duration_ms,
        "usage": usage,
        "cost_usd": cost_usd,
    }


def _run_agents_batch(
    request_id: str,
    agents: list[dict],
) -> list[dict]:
    """Run agents via xapi /inference/batch — single HTTP call, xapi handles parallelism."""
    xapi_url = cfg.get("xapi_url", "http://localhost:7750")
    timeout = cfg.get("agent_timeout_seconds", 120)
    agent_max_tokens = cfg.get("agent_max_tokens", 8192)
    empty_usage = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}

    # Per-agent model selection
    agent_models = []
    for a in agents:
        query = a.get("query", "")
        has_tools = bool(a.get("tools"))
        a_model = select_model(query, has_tools) if query else cfg.get("claude_model", "sonnet")
        agent_models.append(a_model)

    # Mark all agents as running
    for i, a in enumerate(agents):
        state.update_agent(request_id, a["agent_id"],
                           status="running", started_at=time.time())
        print(f"[agent-runner] {a['callsign']} calling xapi batch (model={agent_models[i]})...", flush=True)

    # Build batch request — include request_id in user for fresh Gateway sessions
    batch_requests = []
    for i, a in enumerate(agents):
        full_model = _MODEL_MAP.get(agent_models[i], agent_models[i])
        batch_requests.append({
            "model": full_model,
            "messages": [{"role": "user", "content": a["prompt"]}],
            "user": f"mas:{request_id[:8]}:{a['persona_id']}",
            "max_tokens": agent_max_tokens,
        })

    def _fail_all(error_msg: str) -> list[dict]:
        """Mark all agents as failed and return error results."""
        print(f"[agent-runner] Batch failed: {error_msg}", flush=True)
        return [
            (state.update_agent(request_id, a["agent_id"],
                                status="failed", error=error_msg, model=agent_models[i]),
             {"text": "", "tokens_used": 0, "model": agent_models[i],
              "duration_ms": 0, "error": error_msg})[1]
            for i, a in enumerate(agents)
        ]

    # Acquire inference semaphore — backpressure when too many concurrent calls
    sem = _get_inference_semaphore()
    sem_timeout = timeout + 60  # generous: wait up to agent_timeout + 60s for a slot
    if not sem.acquire(timeout=sem_timeout):
        return _fail_all(f"inference queue full (waited {sem_timeout}s)")
    print(f"[agent-runner] [{request_id[:8]}] Batch acquired inference slot "
          f"({len(agents)} agents)", flush=True)

    max_retries = cfg.get("inference_max_retries", 3)
    start = time.time()
    resp = None
    try:  # try/finally ensures semaphore is always released
        for attempt in range(max_retries):
            try:
                resp = _get_http().post(
                    f"{xapi_url}/inference/batch",
                    json={"requests": batch_requests},
                    timeout=timeout + 30,  # extra margin for batch overhead
                )
                if resp.status_code in (502, 503) and attempt < max_retries - 1:
                    wait = 5 * (attempt + 1)
                    print(f"[agent-runner] Batch xapi {resp.status_code}, retrying in {wait}s (attempt {attempt + 1}/{max_retries})...", flush=True)
                    time.sleep(wait)
                    continue
                break
            except (httpx.ConnectError, httpx.RemoteProtocolError):
                if attempt < max_retries - 1:
                    wait = 5 * (attempt + 1)
                    print(f"[agent-runner] Batch connect error, retrying in {wait}s (attempt {attempt + 1}/{max_retries})...", flush=True)
                    time.sleep(wait)
                    continue
                # Raise so caller can fallback to ThreadPool (individual calls may succeed)
                raise RuntimeError(f"xapi unreachable at {xapi_url} (after {max_retries} attempts)")
            except Exception as e:
                # Systemic failure (timeout, etc.) — raise for ThreadPool fallback
                raise RuntimeError(str(e)) from e

        if resp.status_code != 200:
            raise RuntimeError(f"xapi batch {resp.status_code}: {resp.text[:300]}")

        batch_data = resp.json()
        batch_results = batch_data.get("results", [])
        total_ms = int((time.time() - start) * 1000)

        results = []
        for i, a in enumerate(agents):
            model = agent_models[i]
            item = batch_results[i] if i < len(batch_results) else {}
            error = item.get("error")
            duration_ms = int(item.get("duration_ms", 0))

            if error:
                print(f"[agent-runner] {a['callsign']} error: {error}", flush=True)
                if _is_rate_limit_error(error):
                    print(f"[agent-runner] Rate limit detected for {a['callsign']}", flush=True)
                state.update_agent(request_id, a["agent_id"],
                                   status="failed", error=error, model=model)
                results.append({"text": "", "tokens_used": 0, "model": model,
                                "duration_ms": duration_ms, "error": error})
                continue

            text = filter_output(item.get("content", ""))
            raw_usage = item.get("usage", {})
            b_cache_read = raw_usage.get("cache_read_input_tokens", 0)
            b_cache_write = raw_usage.get("cache_creation_input_tokens", 0)
            if not b_cache_read:
                b_details = raw_usage.get("prompt_tokens_details", {}) or {}
                b_cache_read = b_details.get("cached_tokens", 0)
                b_cache_write = b_cache_write or b_details.get("cache_creation_tokens", 0)
            usage = {
                "input": raw_usage.get("input_tokens", raw_usage.get("prompt_tokens", 0)),
                "output": raw_usage.get("output_tokens", raw_usage.get("completion_tokens", 0)),
                "cacheRead": b_cache_read,
                "cacheWrite": b_cache_write,
            }
            tokens_used = usage.get("input", 0) + usage.get("output", 0)
            cost_usd = item.get("cost_usd", 0.0)

            if not text.strip():
                empty_err = "empty response from inference"
                print(f"[agent-runner] {a['callsign']} empty response ({duration_ms}ms)", flush=True)
                state.update_agent(request_id, a["agent_id"],
                                   status="failed", error=empty_err, model=model)
                results.append({"text": "", "tokens_used": tokens_used, "model": model,
                                "duration_ms": duration_ms, "error": empty_err})
                continue

            print(f"[agent-runner] {a['callsign']} completed ({duration_ms}ms, {len(text)} chars, "
                  f"{tokens_used} tokens, ${cost_usd:.4f}, model={model})", flush=True)

            state.update_agent(request_id, a["agent_id"],
                               status="completed",
                               output=text,
                               tokens_used=tokens_used,
                               model=model,
                               cost_usd=cost_usd)

            results.append({
                "text": text,
                "tokens_used": tokens_used,
                "model": model,
                "duration_ms": duration_ms,
                "usage": usage,
                "cost_usd": cost_usd,
            })

        print(f"[agent-runner] Batch completed: {len(agents)} agents in {total_ms}ms", flush=True)
        return results
    finally:
        sem.release()
        print(f"[agent-runner] [{request_id[:8]}] Released inference slot", flush=True)


def get_worker_nodes(count: int = 1) -> list[dict]:
    """Request worker node allocation from NAS allocator."""
    nas_url = cfg.get("nas_url", "http://localhost:7730")
    tag = cfg.get("worker_tag", "worker")
    try:
        resp = _get_http().get(
            f"{nas_url}/nodes/allocate",
            params={"count": count, "tag": tag},
            timeout=5.0,
        )
        if resp.status_code == 200:
            return resp.json().get("nodes", [])
    except Exception as e:
        print(f"[agent-runner] Worker allocation failed: {e}", flush=True)
    return []


def run_agent_on_worker(
    request_id: str,
    agent_id: str,
    prompt: str,
    persona_id: str,
    callsign: str,
    worker: dict,
    query: str = "",
) -> dict:
    """Execute a single agent on a remote worker node.

    worker: {"node_id", "ip_address", "worker_port", ...} from NAS allocator.
    The worker runs inference + tool-use loop locally on the node PC.
    """
    from .mas_tools import WORKER_LOCAL_TOOLS

    start = time.time()
    state.update_agent(request_id, agent_id,
                       status="running", started_at=start)

    worker_ip = worker["ip_address"]
    worker_port = worker.get("worker_port", 7731)
    worker_timeout = cfg.get("worker_timeout", 180)
    model = select_model(query) if query else cfg.get("claude_model", "sonnet")
    full_model = _MODEL_MAP.get(model, model)
    xapi_url = cfg.get("xapi_url", "http://localhost:7750")

    print(f"[agent-runner] {callsign} → worker {worker['node_id']} "
          f"({worker_ip}:{worker_port})", flush=True)

    try:
        resp = _get_http().post(
            f"http://{worker_ip}:{worker_port}/worker/task",
            json={
                "prompt": prompt,
                "model": full_model,
                "tools": WORKER_LOCAL_TOOLS,
                "xapi_url": xapi_url,
                "api_key": cfg.get("xapi_api_key", ""),
                "user": f"mas:{request_id[:8]}:{persona_id}",
                "max_tokens": cfg.get("agent_max_tokens", 8192),
                "max_tool_rounds": 10,
                "timeout": worker_timeout,
            },
            timeout=worker_timeout + 30,
        )
    except Exception as e:
        error_msg = f"worker unreachable {worker_ip}:{worker_port}: {e}"
        print(f"[agent-runner] {callsign} error: {error_msg}", flush=True)
        state.update_agent(request_id, agent_id,
                           status="failed", error=error_msg, model=model)
        return {"text": "", "tokens_used": 0, "model": model,
                "duration_ms": int((time.time() - start) * 1000), "error": error_msg}

    duration_ms = int((time.time() - start) * 1000)

    if resp.status_code != 200:
        error_msg = f"worker {resp.status_code}: {resp.text[:300]}"
        state.update_agent(request_id, agent_id,
                           status="failed", error=error_msg, model=model)
        return {"text": "", "tokens_used": 0, "model": model,
                "duration_ms": duration_ms, "error": error_msg}

    data = resp.json()
    if data.get("error"):
        error_msg = data["error"]
        print(f"[agent-runner] {callsign} worker error: {error_msg}", flush=True)
        state.update_agent(request_id, agent_id,
                           status="failed", error=error_msg, model=model)
        return {"text": "", "tokens_used": data.get("tokens_used", 0), "model": model,
                "duration_ms": duration_ms, "error": error_msg}

    text = filter_output(data.get("text", ""))
    tokens_used = data.get("tokens_used", 0)
    cost_usd = data.get("cost_usd", 0.0)
    usage = data.get("usage", {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0})

    print(f"[agent-runner] {callsign} worker completed ({duration_ms}ms, {len(text)} chars, "
          f"{tokens_used} tokens, ${cost_usd:.4f}, tools={data.get('tool_calls_count', 0)})",
          flush=True)

    state.update_agent(request_id, agent_id,
                       status="completed", output=text,
                       tokens_used=tokens_used, model=model, cost_usd=cost_usd)

    return {
        "text": text,
        "tokens_used": tokens_used,
        "model": model,
        "duration_ms": duration_ms,
        "usage": usage,
        "cost_usd": cost_usd,
    }


def _run_agents_distributed(
    request_id: str,
    agents: list[dict],
    workers: list[dict],
) -> list[dict]:
    """Run agents distributed across worker nodes.

    Maps agents to workers (round-robin if more agents than workers).
    Agents without a worker fall back to local execution.
    """
    pool = _get_pool()
    futures: list[tuple[dict, Future]] = []

    for i, a in enumerate(agents):
        if i < len(workers):
            # Run on remote worker
            f = pool.submit(
                run_agent_on_worker,
                request_id, a["agent_id"], a["prompt"],
                a["persona_id"], a["callsign"], workers[i],
                a.get("query", ""),
            )
        else:
            # Fallback to local execution
            print(f"[agent-runner] {a['callsign']} → local (no worker available)", flush=True)
            f = pool.submit(
                run_agent,
                request_id, a["agent_id"], a["prompt"],
                a["persona_id"], a["callsign"], a.get("tools"),
                a.get("query", ""),
            )
        futures.append((a, f))

    results = []
    for a, f in futures:
        try:
            result = f.result(timeout=cfg.get("worker_timeout", 180) + 30)
        except Exception as e:
            result = {"text": "", "tokens_used": 0, "model": "", "duration_ms": 0,
                      "error": str(e)}
            state.update_agent(request_id, a["agent_id"],
                               status="failed", error=str(e))
        results.append(result)

    return results


def run_agents_parallel(
    request_id: str,
    agents: list[dict],
) -> list[dict]:
    """Run multiple agents in parallel.

    Priority:
    1. Distributed execution on worker nodes (if enabled + workers available)
    2. xapi /inference/batch (single HTTP call, async parallelism)
    3. ThreadPoolExecutor fallback (individual calls, supports tool-use)

    agents: [{"agent_id": str, "prompt": str, "persona_id": str, "callsign": str,
              "tools": list|None}, ...]
    Returns list of results from run_agent.
    """
    # Distributed execution on worker nodes
    if cfg.get("distributed_execution", False):
        workers = get_worker_nodes(count=len(agents))
        if workers:
            print(f"[agent-runner] Distributed: {len(workers)} workers for "
                  f"{len(agents)} agents", flush=True)
            return _run_agents_distributed(request_id, agents, workers)
        elif not cfg.get("distributed_fallback", True):
            print(f"[agent-runner] No workers available and fallback disabled", flush=True)
        else:
            print(f"[agent-runner] No workers available, falling back to local", flush=True)

    # Tool-use agents require individual calls (batch doesn't support multi-turn)
    has_tools = any(a.get("tools") for a in agents)

    # Try batch endpoint first (single HTTP call → xapi asyncio.gather)
    # Skip batch in direct mode — batch always routes through Gateway.
    # ThreadPool with individual /inference/raw calls is cheaper (96% token reduction).
    use_batch = not has_tools and cfg.get("use_batch_inference", True)
    if use_batch and _select_inference_endpoint() == "raw":
        use_batch = False
        print(f"[agent-runner] Skipping batch (direct mode), using ThreadPool", flush=True)
    if use_batch:
        try:
            return _run_agents_batch(request_id, agents)
        except Exception as e:
            print(f"[agent-runner] Batch failed, falling back to ThreadPool: {e}", flush=True)

    if has_tools:
        print(f"[agent-runner] Using ThreadPool (agents have tools)", flush=True)

    # Fallback: ThreadPoolExecutor (individual calls, supports tool-use)
    # Acquire inference semaphore for ThreadPool path too
    sem = _get_inference_semaphore()
    tp_timeout = cfg.get("agent_timeout_seconds", 120) + 60
    if not sem.acquire(timeout=tp_timeout):
        print(f"[agent-runner] [{request_id[:8]}] ThreadPool inference queue full", flush=True)
        return [{"text": "", "tokens_used": 0, "model": "", "duration_ms": 0,
                 "error": f"inference queue full (waited {tp_timeout}s)"}
                for _ in agents]
    print(f"[agent-runner] [{request_id[:8]}] ThreadPool acquired inference slot "
          f"({len(agents)} agents)", flush=True)

    try:
        pool = _get_pool()
        futures: list[tuple[dict, Future]] = []

        for a in agents:
            f = pool.submit(
                run_agent,
                request_id,
                a["agent_id"],
                a["prompt"],
                a["persona_id"],
                a["callsign"],
                a.get("tools"),
                a.get("query", ""),
            )
            futures.append((a, f))

        results = []
        for a, f in futures:
            try:
                result = f.result(timeout=cfg.get("agent_timeout_seconds", 120) + 10)
            except Exception as e:
                result = {"text": "", "tokens_used": 0, "model": "", "duration_ms": 0,
                          "error": str(e)}
                state.update_agent(request_id, a["agent_id"],
                                   status="failed", error=str(e))
            results.append(result)

        return results
    finally:
        sem.release()
        print(f"[agent-runner] [{request_id[:8]}] ThreadPool released inference slot", flush=True)


def run_synthesis(request_id: str, prompt: str) -> dict:
    """Run synthesis via xapi inference (no persona).

    Registers as a pseudo-agent in state so cost/tokens are tracked.
    """
    start = time.time()

    # Register synthesis as a tracked agent
    agent_id = state.add_agent(request_id, "_synthesis", "MAS-Synth", "Synthesis")
    state.update_agent(request_id, agent_id, status="running", started_at=start)

    synth_model = cfg.get("synthesis_model", cfg.get("claude_model", "sonnet"))
    synth_timeout = cfg.get("synthesis_timeout_seconds", 300)
    synth_max_tokens = cfg.get("synthesis_max_tokens", 2048)

    synth_user = f"mas:{request_id[:8]}:synthesis"
    print(f"[agent-runner] MAS-Synth synthesizing (timeout={synth_timeout}s, max_tokens={synth_max_tokens})...", flush=True)
    result = call_xapi_inference(prompt, model=synth_model, timeout=synth_timeout,
                                 user=synth_user, max_tokens=synth_max_tokens)

    duration_ms = int((time.time() - start) * 1000)

    if result.get("error"):
        print(f"[agent-runner] MAS-Synth error: {result['error']}", flush=True)
        state.update_agent(request_id, agent_id,
                           status="failed", error=result["error"],
                           model=synth_model)
        return {"text": "", "tokens_used": 0, "error": result["error"]}

    text = filter_output(result["text"])
    usage = result.get("usage", {})
    tokens_used = usage.get("input", 0) + usage.get("output", 0)
    cost_usd = result.get("cost_usd", 0.0)

    print(f"[agent-runner] MAS-Synth completed ({duration_ms}ms, {len(text)} chars, "
          f"{tokens_used} tokens, ${cost_usd:.4f})", flush=True)

    state.update_agent(request_id, agent_id,
                       status="completed",
                       output="",  # don't duplicate synthesis text
                       tokens_used=tokens_used,
                       model=synth_model,
                       cost_usd=cost_usd)

    return {
        "text": text,
        "tokens_used": tokens_used,
        "model": synth_model,
        "duration_ms": duration_ms,
        "usage": usage,
        "cost_usd": cost_usd,
    }
