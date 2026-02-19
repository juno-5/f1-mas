"""MAS Agent Runner — ThreadPoolExecutor + Claude Code CLI via FAS consumer token.

Uses the FAS token system: token-manager writes auth-profiles.json for MAS,
agent_runner reads it to get the current OAuth token. Each agent gets its own
isolated config dir with a copy of the token to avoid auth-profiles race conditions.
"""

import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, Future

from . import mas_config as cfg
from . import mas_state as state
from .mas_constitution import filter_output

_pool: ThreadPoolExecutor | None = None

HOME = os.path.expanduser("~")
MAS_WORK_DIR = os.path.join(HOME, ".f1crew", "mas-agents")
MAS_AUTH_FILE = os.path.join(HOME, ".f1crew", "agents", "mas", "agent", "auth-profiles.json")


def _get_pool() -> ThreadPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ThreadPoolExecutor(
            max_workers=cfg.get("thread_pool_workers", 5),
            thread_name_prefix="mas-agent",
        )
    return _pool


def read_consumer_token() -> dict | None:
    """Read the current OAuth token from FAS-managed auth-profiles.json.

    Returns {"token": str, "name": str} or None if unavailable.
    The token-manager writes this file via update_agent_auth() on rotation.
    """
    try:
        with open(MAS_AUTH_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[agent-runner] Cannot read auth-profiles: {e}", flush=True)
        return None

    # order is {"anthropic": ["anthropic:xxx"]} — get the first profile key
    order = data.get("order", {})
    if isinstance(order, dict):
        profile_keys = order.get("anthropic", [])
    elif isinstance(order, list):
        profile_keys = order
    else:
        profile_keys = []

    if not profile_keys:
        print("[agent-runner] No profile in auth-profiles order", flush=True)
        return None

    profile_key = profile_keys[0]
    profile = data.get("profiles", {}).get(profile_key, {})
    token = profile.get("token", "")

    if not token:
        print(f"[agent-runner] Empty token for profile {profile_key}", flush=True)
        return None

    # Extract short name from profile key (e.g. "anthropic:kernel" → "kernel")
    name = profile_key.split(":", 1)[-1] if ":" in profile_key else profile_key
    return {"token": token, "name": name}


def _create_agent_config_dir(session_id: str, oauth_token: str) -> str:
    """Create an isolated ~/.claude-like config dir for one agent.

    Returns the config dir path. The caller must clean it up.
    """
    config_dir = os.path.join(MAS_WORK_DIR, session_id)
    os.makedirs(config_dir, exist_ok=True)

    # Write auth-profiles.json with this token
    profile_name = f"anthropic:mas-{session_id}"
    profiles = {
        "profiles": {
            profile_name: {
                "type": "token",
                "provider": "anthropic",
                "token": oauth_token,
            }
        },
        "order": {"anthropic": [profile_name]},
    }
    with open(os.path.join(config_dir, "auth-profiles.json"), "w") as f:
        json.dump(profiles, f)

    return config_dir


def _cleanup_agent_config_dir(session_id: str):
    """Remove agent's isolated config dir."""
    config_dir = os.path.join(MAS_WORK_DIR, session_id)
    try:
        shutil.rmtree(config_dir, ignore_errors=True)
    except Exception:
        pass


def call_claude_cli(prompt: str, config_dir: str, model: str = None) -> dict:
    """Call Claude via `claude -p` CLI with isolated config dir.

    Returns {"text": str, "model": str, "error": str|None}.
    """
    if model is None:
        model = cfg.get("claude_model", "claude-sonnet-4-5-20250929")

    timeout = cfg.get("agent_timeout_seconds", 120)

    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "text"]

    env = {**os.environ}
    env["CLAUDE_CONFIG_DIR"] = config_dir
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        if result.returncode != 0:
            error = result.stderr.strip() or f"claude CLI exit code {result.returncode}"
            return {"text": "", "model": model, "error": error}

        text = result.stdout.strip()
        return {"text": text, "model": model, "error": None}

    except subprocess.TimeoutExpired:
        return {"text": "", "model": model, "error": f"timeout after {timeout}s"}
    except FileNotFoundError:
        return {"text": "", "model": model, "error": "claude CLI not found"}


def run_agent(
    request_id: str,
    agent_id: str,
    prompt: str,
    persona_id: str,
    callsign: str,
) -> dict:
    """Execute a single agent: read consumer token → isolated config → claude CLI → cleanup.

    Returns {"text": str, "tokens_used": int, "model": str, "duration_ms": int}.
    """
    start = time.time()
    state.update_agent(request_id, agent_id,
                       status="running", started_at=start)

    session_id = f"{request_id}-{agent_id}"

    # 1. Read token from FAS-managed auth-profiles
    token_info = read_consumer_token()
    if not token_info:
        state.update_agent(request_id, agent_id,
                           status="failed", error="no token available")
        return {"text": "", "tokens_used": 0, "model": "", "duration_ms": 0,
                "error": "no token available"}

    oauth_token = token_info["token"]
    token_name = token_info["name"]

    config_dir = None
    try:
        # 2. Create isolated config dir
        config_dir = _create_agent_config_dir(session_id, oauth_token)

        # 3. Call Claude CLI
        claude_model = cfg.get("claude_model", "claude-sonnet-4-5-20250929")
        model = f"anthropic/{claude_model}"

        print(f"[agent-runner] {callsign} ({token_name}) calling claude...", flush=True)
        result = call_claude_cli(prompt, config_dir, model=claude_model)

        if result.get("error"):
            print(f"[agent-runner] {callsign} error: {result['error']}", flush=True)
            state.update_agent(request_id, agent_id,
                               status="failed", error=result["error"])
            return {
                "text": "",
                "tokens_used": 0,
                "model": model,
                "duration_ms": int((time.time() - start) * 1000),
                "error": result["error"],
            }

        text = filter_output(result["text"])
        duration_ms = int((time.time() - start) * 1000)

        print(f"[agent-runner] {callsign} completed ({duration_ms}ms, {len(text)} chars)", flush=True)

        state.update_agent(request_id, agent_id,
                           status="completed",
                           output=text,
                           tokens_used=0,
                           model=model)

        return {
            "text": text,
            "tokens_used": 0,
            "model": model,
            "duration_ms": duration_ms,
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        error_msg = str(e)
        state.update_agent(request_id, agent_id,
                           status="failed", error=error_msg)
        return {
            "text": "",
            "tokens_used": 0,
            "model": "",
            "duration_ms": duration_ms,
            "error": error_msg,
        }
    finally:
        _cleanup_agent_config_dir(session_id)


def run_agents_parallel(
    request_id: str,
    agents: list[dict],
) -> list[dict]:
    """Run multiple agents in parallel.

    agents: [{"agent_id": str, "prompt": str, "persona_id": str, "callsign": str}, ...]
    Returns list of results from run_agent.
    """
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
    """Run synthesis using vanilla Claude CLI (no persona)."""
    start = time.time()
    session_id = f"{request_id}-synth"

    token_info = read_consumer_token()
    if not token_info:
        return {"text": "", "tokens_used": 0, "error": "no token for synthesis"}

    oauth_token = token_info["token"]
    synth_model = cfg.get("synthesis_model", cfg.get("claude_model"))

    config_dir = None
    try:
        config_dir = _create_agent_config_dir(session_id, oauth_token)
        result = call_claude_cli(prompt, config_dir, model=synth_model)

        if result.get("error"):
            return {"text": "", "tokens_used": 0, "error": result["error"]}

        text = filter_output(result["text"])
        return {
            "text": text,
            "tokens_used": 0,
            "model": synth_model,
            "duration_ms": int((time.time() - start) * 1000),
        }
    except Exception as e:
        return {"text": "", "tokens_used": 0, "error": str(e)}
    finally:
        _cleanup_agent_config_dir(session_id)
