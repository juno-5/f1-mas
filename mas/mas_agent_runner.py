"""MAS Agent Runner — ThreadPoolExecutor + xapi inference API.

Uses xapi /inference/chat endpoint which proxies through FAS Gateway (port 18789).
Token management, usage tracking, and rate limiting handled automatically by FAS Gateway.
"""

import time
from concurrent.futures import ThreadPoolExecutor, Future

import httpx

from . import mas_config as cfg
from . import mas_state as state
from .mas_constitution import filter_output

_pool: ThreadPoolExecutor | None = None

# Shared httpx client — connection pooling for xapi calls
_http: httpx.Client | None = None


def _get_http() -> httpx.Client:
    """Return shared httpx.Client with connection pooling (keep-alive reuse)."""
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=10.0),
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


def call_xapi_inference(prompt: str, model: str = None, timeout: int = None, user: str = "mas:agent") -> dict:
    """Call LLM via xapi /inference/chat (replaces claude -p subprocess).

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

    try:
        resp = _get_http().post(
            f"{xapi_url}/inference/chat",
            json={
                "model": full_model,
                "messages": [{"role": "user", "content": prompt}],
                "user": user,
                "max_tokens": 4096,
            },
            timeout=timeout,
        )

        if resp.status_code != 200:
            error = resp.text[:300]
            return {"text": "", "model": full_model, "error": f"xapi {resp.status_code}: {error}",
                    "usage": empty_usage, "cost_usd": 0.0}

        data = resp.json()
        raw_usage = data.get("usage", {})
        usage = {
            "input": raw_usage.get("input_tokens", raw_usage.get("prompt_tokens", 0)),
            "output": raw_usage.get("output_tokens", raw_usage.get("completion_tokens", 0)),
            "cacheRead": raw_usage.get("cache_read_input_tokens", 0),
            "cacheWrite": raw_usage.get("cache_creation_input_tokens", 0),
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
    except httpx.ConnectError:
        return {"text": "", "model": full_model, "error": f"xapi unreachable at {xapi_url}",
                "usage": empty_usage, "cost_usd": 0.0}
    except Exception as e:
        return {"text": "", "model": full_model, "error": str(e),
                "usage": empty_usage, "cost_usd": 0.0}


def run_agent(
    request_id: str,
    agent_id: str,
    prompt: str,
    persona_id: str,
    callsign: str,
) -> dict:
    """Execute a single agent via xapi inference.

    Returns {"text": str, "tokens_used": int, "model": str, "duration_ms": int}.
    """
    start = time.time()
    state.update_agent(request_id, agent_id,
                       status="running", started_at=start)

    model = cfg.get("claude_model", "sonnet")

    print(f"[agent-runner] {callsign} calling xapi inference...", flush=True)
    result = call_xapi_inference(prompt, model=model, user=f"mas:{callsign}")

    duration_ms = int((time.time() - start) * 1000)

    if result.get("error"):
        error_msg = result["error"]
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
    tokens_used = sum(usage.values())
    cost_usd = result.get("cost_usd", 0.0)

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
    model = cfg.get("claude_model", "sonnet")
    full_model = _MODEL_MAP.get(model, model)
    xapi_url = cfg.get("xapi_url", "http://localhost:7750")
    timeout = cfg.get("agent_timeout_seconds", 120)
    empty_usage = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}

    # Mark all agents as running
    for a in agents:
        state.update_agent(request_id, a["agent_id"],
                           status="running", started_at=time.time())
        print(f"[agent-runner] {a['callsign']} calling xapi batch...", flush=True)

    # Build batch request
    batch_requests = []
    for a in agents:
        batch_requests.append({
            "model": full_model,
            "messages": [{"role": "user", "content": a["prompt"]}],
            "user": f"mas:{a['callsign']}",
            "max_tokens": 4096,
        })

    start = time.time()
    try:
        resp = _get_http().post(
            f"{xapi_url}/inference/batch",
            json={"requests": batch_requests},
            timeout=timeout + 30,  # extra margin for batch overhead
        )
    except (httpx.TimeoutException, httpx.ConnectError, Exception) as e:
        # Batch failed — mark all as failed
        error_msg = str(e)
        print(f"[agent-runner] Batch call failed: {error_msg}", flush=True)
        results = []
        for a in agents:
            state.update_agent(request_id, a["agent_id"],
                               status="failed", error=error_msg, model=model)
            results.append({"text": "", "tokens_used": 0, "model": model,
                            "duration_ms": 0, "error": error_msg})
        return results

    if resp.status_code != 200:
        error_msg = f"xapi batch {resp.status_code}: {resp.text[:300]}"
        print(f"[agent-runner] Batch HTTP error: {error_msg}", flush=True)
        results = []
        for a in agents:
            state.update_agent(request_id, a["agent_id"],
                               status="failed", error=error_msg, model=model)
            results.append({"text": "", "tokens_used": 0, "model": model,
                            "duration_ms": 0, "error": error_msg})
        return results

    batch_data = resp.json()
    batch_results = batch_data.get("results", [])
    total_ms = int((time.time() - start) * 1000)

    results = []
    for i, a in enumerate(agents):
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
        usage = {
            "input": raw_usage.get("input_tokens", raw_usage.get("prompt_tokens", 0)),
            "output": raw_usage.get("output_tokens", raw_usage.get("completion_tokens", 0)),
            "cacheRead": raw_usage.get("cache_read_input_tokens", 0),
            "cacheWrite": raw_usage.get("cache_creation_input_tokens", 0),
        }
        tokens_used = sum(usage.values())
        cost_usd = item.get("cost_usd", 0.0)

        print(f"[agent-runner] {a['callsign']} completed ({duration_ms}ms, {len(text)} chars, "
              f"{tokens_used} tokens, ${cost_usd:.4f})", flush=True)

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


def run_agents_parallel(
    request_id: str,
    agents: list[dict],
) -> list[dict]:
    """Run multiple agents in parallel.

    Prefers xapi /inference/batch (single HTTP call, async parallelism).
    Falls back to ThreadPoolExecutor if batch endpoint unavailable.

    agents: [{"agent_id": str, "prompt": str, "persona_id": str, "callsign": str}, ...]
    Returns list of results from run_agent.
    """
    # Try batch endpoint first (single HTTP call → xapi asyncio.gather)
    if cfg.get("use_batch_inference", True):
        try:
            return _run_agents_batch(request_id, agents)
        except Exception as e:
            print(f"[agent-runner] Batch failed, falling back to ThreadPool: {e}", flush=True)

    # Fallback: ThreadPoolExecutor (individual calls)
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

    print(f"[agent-runner] MAS-Synth synthesizing (timeout={synth_timeout}s)...", flush=True)
    result = call_xapi_inference(prompt, model=synth_model, timeout=synth_timeout, user="mas:synthesis")

    duration_ms = int((time.time() - start) * 1000)

    if result.get("error"):
        print(f"[agent-runner] MAS-Synth error: {result['error']}", flush=True)
        state.update_agent(request_id, agent_id,
                           status="failed", error=result["error"],
                           model=synth_model)
        return {"text": "", "tokens_used": 0, "error": result["error"]}

    text = filter_output(result["text"])
    usage = result.get("usage", {})
    tokens_used = sum(usage.values())
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
