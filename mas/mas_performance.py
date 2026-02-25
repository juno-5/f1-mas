"""MAS Performance Ledger — record per-agent performance after each request.

Appends PerformanceRecord to daily JSONL for persona scoring and analytics.
"""

import json
import os
import time
from dataclasses import dataclass, asdict

from . import mas_config as cfg
from . import mas_state as state


PERFORMANCE_DIR = os.path.expanduser("~/.f1crew/shared/datasets")


@dataclass
class PerformanceRecord:
    ts: int
    request_id: str
    persona_id: str
    callsign: str
    function: str
    domain: str
    pattern: str
    locale: str
    # Agent outcome
    status: str           # completed/failed
    tokens_used: int
    cost_usd: float
    duration_ms: int
    output_length: int
    model: str
    # Request context
    request_status: str
    agent_count: int
    # Optional
    model_reason: str = ""


def _ledger_path(date_str: str = "") -> str:
    if not date_str:
        date_str = time.strftime("%Y-%m-%d")
    return os.path.join(PERFORMANCE_DIR, f"mas-performance-{date_str}.jsonl")


def record_outcome(request_id: str, analysis: dict):
    """Record performance data for all agents in a completed request.

    Called from mas_orchestrator after request completion.
    analysis: the dict from analyze_request() with domains, functions, etc.
    """
    req = state.get_request(request_id)
    if not req:
        return

    functions = analysis.get("functions", [])
    primary_function = functions[0] if functions else ""
    domains = analysis.get("domains", [])
    primary_domain = domains[0] if domains else ""

    records = []
    for agent in req.agents:
        record = PerformanceRecord(
            ts=int(time.time()),
            request_id=request_id,
            persona_id=agent.persona_id,
            callsign=agent.callsign,
            function=primary_function,
            domain=primary_domain,
            pattern=req.pattern,
            locale=req.locale,
            status=agent.status,
            tokens_used=agent.tokens_used,
            cost_usd=agent.cost_usd,
            duration_ms=agent.duration_ms,
            output_length=len(agent.output) if agent.output else 0,
            model=agent.model,
            model_reason=getattr(agent, "model_reason", ""),
            request_status=req.status,
            agent_count=len(req.agents),
        )
        records.append(record)

    if not records:
        return

    path = _ledger_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            for rec in records:
                f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
    except OSError:
        pass  # best-effort; don't crash the request flow


def load_records(lookback_days: int = 7) -> list[dict]:
    """Load performance records from the last N days."""
    records = []
    today = time.time()
    for i in range(lookback_days):
        date_str = time.strftime("%Y-%m-%d", time.localtime(today - i * 86400))
        path = _ledger_path(date_str)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except (OSError, json.JSONDecodeError):
            continue
    return records
