"""MAS Agent Runner — ThreadPoolExecutor + xapi inference API.

Uses xapi /inference/chat endpoint which proxies through FAS Gateway (port 18789).
Token management, usage tracking, and rate limiting handled automatically by FAS Gateway.

Supports tool-use: when agents are given tools, the runner executes a multi-turn loop
(LLM → tool_calls → execute → feed results → LLM → ... → final text).
"""

import json
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

    last_error = ""
    for attempt in range(2):  # 1 retry on transient errors
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

            if resp.status_code in (502, 503) and attempt == 0:
                print(f"[agent-runner] xapi {resp.status_code}, retrying in 5s...", flush=True)
                time.sleep(5)
                continue
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
        except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
            last_error = str(e)
            if attempt == 0:
                time.sleep(5)  # wait for xapi restart
                continue
            return {"text": "", "model": full_model, "error": f"xapi unreachable at {xapi_url} (after retry)",
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
) -> dict:
    """Execute a single agent via xapi inference.

    Args:
        tools: Optional OpenAI function-calling tool definitions. When provided,
            uses tool-use loop (LLM → tool_calls → execute → feed back → repeat).

    Returns {"text": str, "tokens_used": int, "model": str, "duration_ms": int}.
    """
    start = time.time()
    state.update_agent(request_id, agent_id,
                       status="running", started_at=start)

    model = cfg.get("claude_model", "sonnet")

    if tools:
        print(f"[agent-runner] {callsign} calling xapi inference "
              f"with {len(tools)} tools...", flush=True)
        result = call_xapi_with_tools(prompt, tools, model=model, user=f"mas:{callsign}")
    else:
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

    def _fail_all(error_msg: str) -> list[dict]:
        """Mark all agents as failed and return error results."""
        print(f"[agent-runner] Batch failed: {error_msg}", flush=True)
        return [
            (state.update_agent(request_id, a["agent_id"],
                                status="failed", error=error_msg, model=model),
             {"text": "", "tokens_used": 0, "model": model,
              "duration_ms": 0, "error": error_msg})[1]
            for a in agents
        ]

    start = time.time()
    resp = None
    for attempt in range(2):  # 1 retry on transient errors
        try:
            resp = _get_http().post(
                f"{xapi_url}/inference/batch",
                json={"requests": batch_requests},
                timeout=timeout + 30,  # extra margin for batch overhead
            )
            if resp.status_code in (502, 503) and attempt == 0:
                print(f"[agent-runner] Batch xapi {resp.status_code}, retrying in 5s...", flush=True)
                time.sleep(5)
                continue
            break
        except (httpx.ConnectError, httpx.RemoteProtocolError):
            if attempt == 0:
                print(f"[agent-runner] Batch connect error, retrying in 5s...", flush=True)
                time.sleep(5)
                continue
            return _fail_all(f"xapi unreachable at {xapi_url} (after retry)")
        except Exception as e:
            return _fail_all(str(e))

    if resp.status_code != 200:
        return _fail_all(f"xapi batch {resp.status_code}: {resp.text[:300]}")

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

        if not text.strip():
            empty_err = "empty response from inference"
            print(f"[agent-runner] {a['callsign']} empty response ({duration_ms}ms)", flush=True)
            state.update_agent(request_id, a["agent_id"],
                               status="failed", error=empty_err, model=model)
            results.append({"text": "", "tokens_used": tokens_used, "model": model,
                            "duration_ms": duration_ms, "error": empty_err})
            continue

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
    model = cfg.get("claude_model", "sonnet")
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
                "user": f"mas:{callsign}",
                "max_tokens": 4096,
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
            )
        else:
            # Fallback to local execution
            print(f"[agent-runner] {a['callsign']} → local (no worker available)", flush=True)
            f = pool.submit(
                run_agent,
                request_id, a["agent_id"], a["prompt"],
                a["persona_id"], a["callsign"], a.get("tools"),
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
    if not has_tools and cfg.get("use_batch_inference", True):
        try:
            return _run_agents_batch(request_id, agents)
        except Exception as e:
            print(f"[agent-runner] Batch failed, falling back to ThreadPool: {e}", flush=True)

    if has_tools:
        print(f"[agent-runner] Using ThreadPool (agents have tools)", flush=True)

    # Fallback: ThreadPoolExecutor (individual calls, supports tool-use)
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
