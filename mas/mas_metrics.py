"""MAS Prometheus Metrics — /metrics endpoint."""

import time

from . import mas_state as state
from . import mas_persona_index as persona_idx

_start_time = time.time()


def render() -> str:
    """Render Prometheus text format metrics."""
    lines = []
    counters = state.get_counters()

    # Request counters
    lines.append("# HELP mas_requests_total Total requests received")
    lines.append("# TYPE mas_requests_total counter")
    lines.append(f"mas_requests_total {counters.get('total_requests', 0)}")

    lines.append("# HELP mas_requests_completed_total Total completed requests")
    lines.append("# TYPE mas_requests_completed_total counter")
    lines.append(f"mas_requests_completed_total {counters.get('completed_requests', 0)}")

    lines.append("# HELP mas_requests_failed_total Total failed requests")
    lines.append("# TYPE mas_requests_failed_total counter")
    lines.append(f"mas_requests_failed_total {counters.get('failed_requests', 0)}")

    lines.append("# HELP mas_requests_blocked_total Total blocked requests (P0)")
    lines.append("# TYPE mas_requests_blocked_total counter")
    lines.append(f"mas_requests_blocked_total {counters.get('blocked_requests', 0)}")

    # Agent counters
    lines.append("# HELP mas_agents_spawned_total Total agents spawned")
    lines.append("# TYPE mas_agents_spawned_total counter")
    lines.append(f"mas_agents_spawned_total {counters.get('total_agents_spawned', 0)}")

    lines.append("# HELP mas_tokens_used_total Total Claude API tokens used")
    lines.append("# TYPE mas_tokens_used_total counter")
    lines.append(f"mas_tokens_used_total {counters.get('total_tokens_used', 0)}")

    # Active requests gauge
    active = sum(
        1 for r in state.get_all_requests().values()
        if r.status in ("pending", "analyzing", "assembling", "running", "synthesizing")
    )
    lines.append("# HELP mas_active_requests Current in-flight requests")
    lines.append("# TYPE mas_active_requests gauge")
    lines.append(f"mas_active_requests {active}")

    # Persona index
    idx = persona_idx.get_index()
    lines.append("# HELP mas_personas_loaded Number of personas in index")
    lines.append("# TYPE mas_personas_loaded gauge")
    lines.append(f"mas_personas_loaded {idx.count()}")

    # Uptime
    lines.append("# HELP mas_uptime_seconds Service uptime")
    lines.append("# TYPE mas_uptime_seconds gauge")
    lines.append(f"mas_uptime_seconds {int(time.time() - _start_time)}")

    # Request duration histogram (simplified — last N requests)
    all_reqs = state.get_all_requests()
    completed = [r for r in all_reqs.values() if r.status == "completed" and r.duration_ms > 0]
    if completed:
        durations = [r.duration_ms for r in completed[-50:]]
        avg_ms = sum(durations) / len(durations)
        max_ms = max(durations)
        lines.append("# HELP mas_request_duration_ms Request duration in milliseconds")
        lines.append("# TYPE mas_request_duration_ms gauge")
        lines.append(f'mas_request_duration_ms{{stat="avg"}} {int(avg_ms)}')
        lines.append(f'mas_request_duration_ms{{stat="max"}} {max_ms}')

    return "\n".join(lines) + "\n"
