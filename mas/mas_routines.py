"""MAS Routine Engine — Pre-optimized workflow interceptor.

Intercepts MAS requests before the expensive persona pipeline (analyze → select → spawn → synthesize)
and routes matching queries through pre-defined YAML routines. Saves 75-85% tokens by using haiku
model and structured steps instead of free-form multi-agent inference.

Architecture:
  User (Slack) → Master Agent → MAS Orchestrator
                                      ↓
                              [0] try_routine(query)
                              ├── MATCH → Routine Engine → Steps → Return
                              └── NO MATCH → [1] analyze_request() → 기존 파이프라인

Step types:
  tool       — execute mas_tools.execute_tool() directly (no LLM)
  inference  — haiku LLM call via xapi (structured prompt)
  template   — variable substitution only (no LLM)
  parallel   — run multiple steps concurrently (ThreadPoolExecutor)
  condition  — conditional branching (contains/matches/equals)
  nas_exec   — remote node command execution (NAS wrapper)
"""

import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

from . import mas_config as cfg
from . import mas_state as state

def _log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [routines] {msg}", flush=True)


# ── Registry ─────────────────────────────────────────────────────────────

_registry: dict[str, dict] = {}       # routine_id → parsed YAML
_trigger_index: list[dict] = []       # [{routine_id, pattern_re, keywords, confidence}]
_registry_lock = threading.Lock()
_routines_mtime: dict[str, float] = {}  # file_path → last mtime


def _find_routines_dir() -> str | None:
    """Find the routines/ directory."""
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "routines"),
        os.path.expanduser("~/F1/f1-mas/routines"),
        os.path.expanduser("~/projects/mayacrew-f1crew/f1-mas/routines"),
        os.path.expanduser("~/.f1crew/scripts/mas/routines"),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None


def load_registry(force: bool = False) -> int:
    """Scan routines/ recursively, parse YAML files, build trigger index.

    Returns count of loaded routines.
    """
    global _registry, _trigger_index, _routines_mtime

    routines_dir = _find_routines_dir()
    if not routines_dir:
        return 0

    # Check mtimes — skip reload if nothing changed
    if not force:
        changed = False
        for yml_path in Path(routines_dir).rglob("*.yml"):
            sp = str(yml_path)
            try:
                mt = os.path.getmtime(sp)
                if sp not in _routines_mtime or _routines_mtime[sp] != mt:
                    changed = True
                    break
            except OSError:
                changed = True
                break
        if not changed and _registry:
            return len(_registry)

    with _registry_lock:
        new_registry = {}
        new_triggers = []
        new_mtimes = {}

        for yml_path in Path(routines_dir).rglob("*.yml"):
            sp = str(yml_path)
            try:
                mt = os.path.getmtime(sp)
                new_mtimes[sp] = mt
                with open(sp, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if not data or not isinstance(data, dict):
                    continue
                rid = data.get("id")
                if not rid:
                    _log(f"WARN: no 'id' in {sp}, skipping")
                    continue

                new_registry[rid] = data

                # Build triggers
                for trigger in data.get("triggers", []):
                    pattern = trigger.get("pattern")
                    keywords = trigger.get("keywords", [])
                    confidence = trigger.get("confidence", 0.8)

                    entry = {
                        "routine_id": rid,
                        "confidence": confidence,
                        "pattern_re": None,
                        "keywords": [],
                    }
                    if pattern:
                        try:
                            entry["pattern_re"] = re.compile(pattern, re.IGNORECASE)
                        except re.error as e:
                            _log(f"WARN: bad regex in {rid}: {e}")
                    if keywords:
                        entry["keywords"] = [kw.lower() for kw in keywords]

                    new_triggers.append(entry)

            except Exception as e:
                _log(f"WARN: failed to load {sp}: {e}")

        _registry = new_registry
        _trigger_index = new_triggers
        _routines_mtime = new_mtimes

    _log(f"Loaded {len(_registry)} routines: {list(_registry.keys())}")
    return len(_registry)


def get_registry() -> dict[str, dict]:
    """Return current routine registry (id → YAML data)."""
    if not _registry:
        load_registry()
    return dict(_registry)


# ── Trigger Matching ──────────────────────────────────────────────────────

def match_routine(query: str) -> tuple[str, float] | None:
    """Match a query against routine triggers.

    Returns (routine_id, confidence) or None if no match.
    Requires confidence >= routine_min_confidence config value.
    """
    if not cfg.get("routines_enabled", True):
        return None

    if not _registry:
        load_registry()

    if not _trigger_index:
        return None

    min_confidence = cfg.get("routine_min_confidence", 0.7)
    query_lower = query.lower()

    best_match = None
    best_confidence = 0.0

    for trigger in _trigger_index:
        confidence = 0.0

        # Pattern regex match
        if trigger["pattern_re"] and trigger["pattern_re"].search(query):
            confidence = max(confidence, trigger["confidence"])

        # Keyword match
        if trigger["keywords"]:
            matched = sum(1 for kw in trigger["keywords"] if kw in query_lower)
            if matched > 0:
                kw_conf = trigger["confidence"] * (matched / len(trigger["keywords"]))
                confidence = max(confidence, kw_conf)

        if confidence >= min_confidence and confidence > best_confidence:
            best_confidence = confidence
            best_match = trigger["routine_id"]

    if best_match:
        return (best_match, best_confidence)
    return None


# ── Variable Interpolation ────────────────────────────────────────────────

def _interpolate(template: str, ctx: dict) -> str:
    """Replace {steps.<id>.output}, {query}, {routine.id}, {routine.duration_ms}, etc."""
    def replacer(m):
        key = m.group(1)
        parts = key.split(".")
        obj = ctx
        for p in parts:
            if isinstance(obj, dict):
                obj = obj.get(p)
            else:
                return m.group(0)  # leave unresolved
            if obj is None:
                return ""
        return str(obj)

    return re.sub(r"\{([\w.]+)\}", replacer, template)


# ── Step Execution ────────────────────────────────────────────────────────

def _exec_tool_step(step: dict, ctx: dict) -> str:
    """Execute a tool step via mas_tools.execute_tool()."""
    from .mas_tools import execute_tool
    tool_name = step.get("tool", "")
    raw_args = step.get("args", {})
    # Interpolate string values in args
    args = {}
    for k, v in raw_args.items():
        if isinstance(v, str):
            args[k] = _interpolate(v, ctx)
        else:
            args[k] = v
    return execute_tool(tool_name, args)


def _exec_inference_step(step: dict, ctx: dict) -> str:
    """Execute an inference step via xapi haiku call."""
    from .mas_agent_runner import call_xapi_inference

    prompt = step.get("prompt", "")
    prompt = _interpolate(prompt, ctx)
    model = step.get("model") or ctx.get("routine", {}).get("default_model") or cfg.get("routine_default_model", "haiku")
    max_tokens = step.get("max_tokens", 2048)
    timeout = step.get("timeout") or cfg.get("routine_timeout", 60)

    user_tag = f"mas:routine:{ctx.get('routine', {}).get('id', 'unknown')}"
    result = call_xapi_inference(
        prompt=prompt,
        model=model,
        timeout=timeout,
        user=user_tag,
        max_tokens=max_tokens,
    )

    # Track tokens
    usage = result.get("usage", {})
    tokens = (usage.get("input", 0) + usage.get("output", 0)
              + usage.get("cacheRead", 0) + usage.get("cacheWrite", 0))
    ctx.setdefault("_tokens", 0)
    ctx["_tokens"] += tokens
    ctx.setdefault("_cost", 0.0)
    ctx["_cost"] += result.get("cost_usd", 0.0)

    if result.get("error"):
        raise RuntimeError(f"Inference failed: {result['error']}")

    return result.get("text", "")


def _exec_template_step(step: dict, ctx: dict) -> str:
    """Execute a template step (pure variable substitution, no LLM)."""
    template = step.get("template", "")
    return _interpolate(template, ctx)


def _exec_parallel_step(step: dict, ctx: dict) -> dict[str, str]:
    """Execute multiple sub-steps concurrently."""
    sub_steps = step.get("steps", [])
    results = {}
    max_workers = min(len(sub_steps), 5)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for sub in sub_steps:
            sid = sub.get("id", f"parallel_{len(futures)}")
            futures[pool.submit(_execute_step, sub, ctx)] = sid

        for future in as_completed(futures):
            sid = futures[future]
            try:
                results[sid] = future.result()
            except Exception as e:
                results[sid] = f"ERROR: {e}"

    # Merge into steps context
    for sid, output in results.items():
        ctx.setdefault("steps", {}).setdefault(sid, {})["output"] = output

    return results


def _exec_condition_step(step: dict, ctx: dict) -> str:
    """Execute a conditional step (branch based on previous output)."""
    check_value = _interpolate(step.get("check", ""), ctx)
    branches = step.get("branches", [])

    for branch in branches:
        op = branch.get("op", "contains")
        value = branch.get("value", "")
        matched = False

        if op == "contains":
            matched = value.lower() in check_value.lower()
        elif op == "equals":
            matched = check_value.strip() == value.strip()
        elif op == "matches":
            matched = bool(re.search(value, check_value, re.IGNORECASE))

        if matched:
            then_steps = branch.get("then", [])
            last_output = ""
            for sub in then_steps:
                last_output = _execute_step(sub, ctx)
            return last_output

    # Default branch
    default_steps = step.get("default", [])
    last_output = ""
    for sub in default_steps:
        last_output = _execute_step(sub, ctx)
    return last_output


def _exec_nas_exec_step(step: dict, ctx: dict) -> str:
    """Execute a NAS remote command step."""
    from .mas_tools import execute_tool

    node_id = _interpolate(step.get("node_id", ""), ctx)
    command = _interpolate(step.get("command", ""), ctx)
    timeout = step.get("timeout", 30)

    # Support batch execution by tag
    tag = step.get("tag")
    if tag:
        import httpx
        nas_url = cfg.get("nas_url", "http://localhost:7730")
        nas_timeout = cfg.get("nas_timeout", 5.0)
        try:
            resp = httpx.post(
                f"{nas_url}/nodes/batch/exec",
                json={"command": command, "tag": tag, "timeout": timeout},
                timeout=timeout + 10,
            )
            return resp.text
        except Exception as e:
            return json.dumps({"error": str(e)})

    # Single node execution
    return execute_tool("nas_exec", {
        "node_id": node_id,
        "command": command,
        "timeout": timeout,
    })


def _execute_step(step: dict, ctx: dict) -> str:
    """Route step to the right executor based on type."""
    step_type = step.get("type", "template")

    if step_type == "tool":
        return _exec_tool_step(step, ctx)
    elif step_type == "inference":
        return _exec_inference_step(step, ctx)
    elif step_type == "template":
        return _exec_template_step(step, ctx)
    elif step_type == "parallel":
        # Returns dict but we stringify for step output
        results = _exec_parallel_step(step, ctx)
        return json.dumps(results, ensure_ascii=False)
    elif step_type == "condition":
        return _exec_condition_step(step, ctx)
    elif step_type == "nas_exec":
        return _exec_nas_exec_step(step, ctx)
    else:
        return f"ERROR: unknown step type '{step_type}'"


# ── Routine Execution ─────────────────────────────────────────────────────

def execute_routine(request_id: str, routine_id: str, query: str) -> dict:
    """Execute a full routine by ID.

    Returns {"output": str, "tokens": int, "cost_usd": float, "duration_ms": int, "routine_id": str}.
    Raises RuntimeError on failure.
    """
    routine = _registry.get(routine_id)
    if not routine:
        raise RuntimeError(f"Routine '{routine_id}' not found in registry")

    start_time = time.time()
    _log(f"[{request_id}] Executing routine: {routine_id}")

    # Build execution context
    ctx = {
        "query": query,
        "request_id": request_id,
        "routine": {
            "id": routine_id,
            "name": routine.get("name", routine_id),
            "domain": routine.get("domain", ""),
            "default_model": routine.get("config", {}).get("model", cfg.get("routine_default_model", "haiku")),
        },
        "steps": {},
        "_tokens": 0,
        "_cost": 0.0,
    }

    # Execute steps sequentially
    steps = routine.get("steps", [])
    for step in steps:
        sid = step.get("id", f"step_{steps.index(step)}")
        _log(f"[{request_id}]   Step: {sid} ({step.get('type', 'template')})")
        try:
            output = _execute_step(step, ctx)
            ctx["steps"][sid] = {"output": output}
        except Exception as e:
            _log(f"[{request_id}]   Step {sid} failed: {e}")
            raise RuntimeError(f"Step '{sid}' failed: {e}")

    # Build final output
    duration_ms = int((time.time() - start_time) * 1000)
    ctx["routine"]["duration_ms"] = duration_ms

    output_template = routine.get("output", {}).get("format", "")
    if output_template:
        final_output = _interpolate(output_template, ctx)
    else:
        # Fallback: use last step output
        last_step_id = steps[-1].get("id", f"step_{len(steps)-1}") if steps else ""
        final_output = ctx["steps"].get(last_step_id, {}).get("output", "(no output)")

    _log(f"[{request_id}] Routine {routine_id} completed in {duration_ms}ms "
         f"({ctx['_tokens']} tokens, ${ctx['_cost']:.4f})")

    return {
        "output": final_output,
        "tokens": ctx["_tokens"],
        "cost_usd": ctx["_cost"],
        "duration_ms": duration_ms,
        "routine_id": routine_id,
    }


# ── Public API (called from orchestrator) ─────────────────────────────────

def try_routine(request_id: str, query: str) -> dict | None:
    """Try to match and execute a routine for the given query.

    Returns result dict if a routine matched and executed successfully.
    Returns None if no routine matched or if execution failed with fallback enabled.
    """
    if not cfg.get("routines_enabled", True):
        return None

    match = match_routine(query)
    if match is None:
        return None

    routine_id, confidence = match
    routine = _registry.get(routine_id, {})
    _log(f"[{request_id}] Routine matched: {routine_id} (confidence={confidence:.2f})")

    state.update_request(request_id, status="running")

    try:
        result = execute_routine(request_id, routine_id, query)

        # Update state with token/cost tracking
        state.update_request(
            request_id,
            total_tokens_used=result["tokens"],
            total_cost_usd=result["cost_usd"],
            duration_ms=result["duration_ms"],
        )

        return result

    except Exception as e:
        _log(f"[{request_id}] Routine {routine_id} failed: {e}")
        fallback = routine.get("config", {}).get("fallback_to_pipeline",
                    cfg.get("routine_fallback_to_pipeline", True))
        if fallback:
            _log(f"[{request_id}] Falling back to MAS pipeline")
            return None
        else:
            state.update_request(request_id, status="failed", error=f"Routine failed: {e}")
            return {"output": f"Routine execution failed: {e}", "tokens": 0, "cost_usd": 0, "duration_ms": 0, "routine_id": routine_id, "error": str(e)}


# ── Hot Reload ────────────────────────────────────────────────────────────

def _reload_loop():
    """Background thread: reload routines on file change."""
    while True:
        interval = cfg.get("routine_reload_interval", 30)
        time.sleep(interval)
        try:
            load_registry()
        except Exception as e:
            _log(f"Reload failed: {e}")


def start_hot_reload():
    """Start background routine reload thread."""
    load_registry(force=True)
    t = threading.Thread(target=_reload_loop, daemon=True)
    t.start()
    _log("Hot-reload started")
