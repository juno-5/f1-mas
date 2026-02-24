#!/usr/bin/env python3
"""
MAS (Master Agent System) Server — Port 7720
Orchestrates 184 expert personas for multi-agent task execution.

Endpoints:
  GET  /health              — Health check
  GET  /status              — Service status + counters
  GET  /metrics             — Prometheus metrics
  GET  /personas            — List all personas
  GET  /personas/select     — Dry-run persona selection
  GET  /personas/scores     — Per-persona efficiency scores
  GET  /personas/<id>/character — Get persona character content
  GET  /functions/<key>/ranking — Personas ranked by score for a function
  GET  /squads/detect       — Auto-detect squad from query text
  POST /request             — Submit a task request
  POST /cancel              — Cancel an active request
  GET  /request/<id>        — Get request status
  GET  /requests            — List all requests
"""

import hashlib
import http.server
import json
import os
import signal
import sys
import threading
import time
from urllib.parse import urlparse, parse_qs

# Add parent to path for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mas import mas_config as cfg
from mas import mas_state as state
from mas import mas_persona_index as persona_idx
from mas import mas_metrics as metrics

# Lazy imports (after config loaded)
_orchestrator = None


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from mas.mas_orchestrator import Orchestrator
        _orchestrator = Orchestrator()
    return _orchestrator


PORT = cfg.get("port", 7720)
_start_time = time.time()
_draining = False  # Set True on SIGTERM to reject new requests

# Request dedup — prevent duplicate query floods within a time window
_recent_queries: dict[str, tuple[str, float]] = {}  # hash -> (request_id, timestamp)
_recent_lock = threading.Lock()
_DEDUP_WINDOW = cfg.get("dedup_window_sec", 10)  # seconds


def _dedup_key(query: str, user: str) -> str:
    """Hash (query, user) for dedup lookup."""
    return hashlib.md5(f"{user}:{query}".encode()).hexdigest()


def _dedup_check(query: str, user: str) -> str | None:
    """Return existing request_id if same query was submitted within window, else None."""
    now = time.time()
    key = _dedup_key(query, user)
    with _recent_lock:
        # Cleanup expired entries
        expired = [k for k, (_, ts) in _recent_queries.items() if now - ts > _DEDUP_WINDOW]
        for k in expired:
            del _recent_queries[k]
        # Check for duplicate
        if key in _recent_queries:
            req_id, ts = _recent_queries[key]
            if now - ts <= _DEDUP_WINDOW:
                return req_id
    return None


def _dedup_register(query: str, user: str, request_id: str) -> None:
    """Register a new query for dedup tracking."""
    key = _dedup_key(query, user)
    with _recent_lock:
        _recent_queries[key] = (request_id, time.time())


def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [mas] {msg}", flush=True)


class MASHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError):
            return {}

    def _parse_path(self):
        parsed = urlparse(self.path)
        params = {}
        for k, v in parse_qs(parsed.query).items():
            params[k] = v[0] if len(v) == 1 else v
        return parsed.path, params

    def do_GET(self):
        path, params = self._parse_path()

        if path == "/health":
            self._handle_health()
        elif path == "/status":
            self._handle_status()
        elif path == "/metrics":
            self._handle_metrics()
        elif path == "/personas":
            self._handle_personas(params)
        elif path == "/personas/select":
            self._handle_persona_select(params)
        elif path.startswith("/personas/") and path.endswith("/character"):
            persona_id = path.split("/personas/")[1].rsplit("/character")[0]
            self._handle_persona_character(persona_id)
        elif path == "/tribes":
            self._handle_tribes(params)
        elif path.startswith("/tribes/") and path.endswith("/squads"):
            tribe_id = path.split("/tribes/")[1].rsplit("/squads")[0]
            self._handle_tribe_squads(tribe_id)
        elif path.startswith("/tribes/"):
            tribe_id = path.split("/tribes/")[1]
            self._handle_tribe_detail(tribe_id)
        elif path == "/squads":
            self._handle_squads(params)
        elif path == "/squads/detect":
            self._handle_squad_detect(params)
        elif path.startswith("/squads/"):
            squad_id = path.split("/squads/")[1]
            self._handle_squad_detail(squad_id)
        elif path == "/personas/scores":
            self._handle_persona_scores()
        elif path.startswith("/functions/") and path.endswith("/ranking"):
            func_key = path.split("/functions/")[1].rsplit("/ranking")[0]
            self._handle_function_ranking(func_key)
        elif path == "/routines":
            self._handle_routines()
        elif path == "/requests":
            self._handle_list_requests()
        elif path.startswith("/request/"):
            req_id = path.split("/request/")[1]
            self._handle_get_request(req_id)
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        path, params = self._parse_path()

        if path == "/request":
            self._handle_submit_request()
        elif path == "/cancel":
            self._handle_cancel()
        else:
            self._send_json(404, {"error": "not found"})

    # ── Handlers ──

    def _handle_health(self):
        idx = persona_idx.get_index()
        status = "draining" if _draining else "ok"
        self._send_json(200, {
            "status": status,
            "personas_loaded": idx.count(),
            "tribes_loaded": len(idx.all_tribes()),
            "squads_loaded": len(idx.all_squads()),
            "uptime_seconds": int(time.time() - _start_time),
        })

    def _handle_status(self):
        idx = persona_idx.get_index()
        counters = state.get_counters()
        timeline = state.get_timeline(20)
        tribes = idx.all_tribes()
        squads = idx.all_squads()

        self._send_json(200, {
            "uptime_seconds": int(time.time() - _start_time),
            "personas_loaded": idx.count(),
            "tribes_loaded": len(tribes),
            "squads_loaded": len(squads),
            "counters": counters,
            "recent_events": timeline,
            "config": {
                "port": PORT,
                "max_agents": cfg.get("max_agents", 5),
                "claude_model": cfg.get("claude_model"),
                "slack_enabled": cfg.get_nested("slack", "enabled", False),
            },
        })

    def _handle_metrics(self):
        body = metrics.render().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_personas(self, params):
        idx = persona_idx.get_index()

        # Optional filters
        category = params.get("category")
        locale = params.get("locale")
        search = params.get("q")
        tag = params.get("tag")

        if search:
            entries = idx.search(search)
        elif tag:
            entries = idx.by_tag(tag)
        elif category and locale:
            cat_entries = idx.by_category(category)
            loc_ids = {e.id for e in idx.by_locale(locale)}
            entries = [e for e in cat_entries if e.id in loc_ids]
        elif category:
            entries = idx.by_category(category)
        elif locale:
            entries = idx.by_locale(locale)
        else:
            entries = idx.all_entries()

        self._send_json(200, {
            "count": len(entries),
            "personas": [
                {
                    "id": e.id, "name": e.name, "callsign": e.callsign,
                    "role": e.role, "category": e.category,
                    "locale": e.locale, "tags": e.tags,
                    "tribe": e.tribe, "squad": e.squad,
                }
                for e in entries
            ],
        })

    def _handle_persona_select(self, params):
        """Dry-run persona selection for a query."""
        query = params.get("q", "")
        if not query:
            self._send_json(400, {"error": "missing ?q= parameter"})
            return

        tribe = params.get("tribe")
        squad = params.get("squad")

        orch = _get_orchestrator()
        analysis = orch.analyze_request(query, tribe=tribe, squad=squad)
        selected = orch.select_personas(analysis)

        self._send_json(200, {
            "query": query,
            "analysis": analysis,
            "selected": [
                {"id": e.id, "name": e.name, "callsign": e.callsign,
                 "role": e.role, "category": e.category,
                 "tribe": e.tribe, "squad": e.squad}
                for e in selected
            ],
        })

    def _handle_persona_character(self, persona_id):
        """Return character file content for a persona (key sections, token-efficient)."""
        idx = persona_idx.get_index()
        entry = idx.get(persona_id)
        if not entry:
            self._send_json(404, {"error": f"persona {persona_id} not found"})
            return

        try:
            content = idx.extract_character_sections(persona_id)
        except Exception as e:
            log(f"[WARN] character load failed for {persona_id}: {e}")
            content = f"(character file unavailable: {e})"

        self._send_json(200, {
            "id": entry.id,
            "name": entry.name,
            "callsign": entry.callsign,
            "role": entry.role,
            "category": entry.category,
            "character_content": content,
        })

    # ── Tribe/Squad Handlers ──

    def _handle_tribes(self, params):
        """List all tribes with squad counts and member counts."""
        idx = persona_idx.get_index()
        tribes = idx.all_tribes()
        self._send_json(200, {
            "count": len(tribes),
            "tribes": [
                {
                    "tribe_id": t.tribe_id,
                    "tribe_name": t.tribe_name,
                    "description": t.description,
                    "squad_count": len(t.squad_ids),
                    "member_count": len(idx.by_tribe(t.tribe_id)),
                    "squads": t.squad_ids,
                }
                for t in tribes
            ],
        })

    def _handle_tribe_detail(self, tribe_id):
        """Get tribe detail with squads and members."""
        idx = persona_idx.get_index()
        tribe = idx.get_tribe(tribe_id)
        if not tribe:
            self._send_json(404, {"error": f"tribe '{tribe_id}' not found"})
            return

        squads_data = []
        for sid in tribe.squad_ids:
            sq = idx.get_squad(sid)
            if sq:
                squads_data.append({
                    "squad_id": sq.squad_id,
                    "squad_name": sq.squad_name,
                    "lead_id": sq.lead_id,
                    "member_count": len(sq.member_ids),
                    "member_ids": sq.member_ids,
                })

        members = idx.by_tribe(tribe_id)
        self._send_json(200, {
            "tribe_id": tribe.tribe_id,
            "tribe_name": tribe.tribe_name,
            "description": tribe.description,
            "squad_count": len(tribe.squad_ids),
            "member_count": len(members),
            "squads": squads_data,
            "members": [
                {"id": e.id, "name": e.name, "callsign": e.callsign,
                 "category": e.category, "squad": e.squad}
                for e in members
            ],
        })

    def _handle_tribe_squads(self, tribe_id):
        """List squads in a tribe."""
        idx = persona_idx.get_index()
        tribe = idx.get_tribe(tribe_id)
        if not tribe:
            self._send_json(404, {"error": f"tribe '{tribe_id}' not found"})
            return

        squads = idx.all_squads(tribe_id)
        self._send_json(200, {
            "tribe_id": tribe_id,
            "count": len(squads),
            "squads": [
                {
                    "squad_id": sq.squad_id,
                    "squad_name": sq.squad_name,
                    "lead_id": sq.lead_id,
                    "member_count": len(sq.member_ids),
                    "member_ids": sq.member_ids,
                }
                for sq in squads
            ],
        })

    def _handle_squads(self, params):
        """List all squads, optionally filtered by tribe."""
        idx = persona_idx.get_index()
        tribe_filter = params.get("tribe")
        squads = idx.all_squads(tribe_filter)

        self._send_json(200, {
            "count": len(squads),
            "squads": [
                {
                    "squad_id": sq.squad_id,
                    "squad_name": sq.squad_name,
                    "tribe_id": sq.tribe_id,
                    "lead_id": sq.lead_id,
                    "member_count": len(sq.member_ids),
                    "member_ids": sq.member_ids,
                }
                for sq in squads
            ],
        })

    def _handle_squad_detail(self, squad_id):
        """Get squad detail with members."""
        idx = persona_idx.get_index()
        sq = idx.get_squad(squad_id)
        if not sq:
            self._send_json(404, {"error": f"squad '{squad_id}' not found"})
            return

        members = idx.by_squad(squad_id)
        lead = idx.squad_lead(squad_id)
        meta = idx.get_squad_meta(squad_id)
        result = {
            "squad_id": sq.squad_id,
            "squad_name": sq.squad_name,
            "tribe_id": sq.tribe_id,
            "lead": {
                "id": lead.id, "name": lead.name, "callsign": lead.callsign,
                "role": lead.role,
            } if lead else None,
            "member_count": len(members),
            "members": [
                {"id": e.id, "name": e.name, "callsign": e.callsign,
                 "role": e.role, "category": e.category, "locale": e.locale}
                for e in members
            ],
        }
        if meta:
            result["expertise"] = meta.get("expertise", [])
            result["tools"] = meta.get("tools", [])
        self._send_json(200, result)

    def _handle_squad_detect(self, params):
        """Detect squad from query text."""
        q = params.get("q", "")
        if not q:
            self._send_json(400, {"error": "missing 'q' parameter"})
            return
        idx = persona_idx.get_index()
        squad_id = idx.detect_squad(q)
        tribe_id = None
        meta = None
        if squad_id:
            sq = idx.get_squad(squad_id)
            if sq:
                tribe_id = sq.tribe_id
            meta = idx.get_squad_meta(squad_id)
        result = {
            "query": q,
            "squad_id": squad_id or "",
            "tribe_id": tribe_id or "",
        }
        if meta:
            result["expertise"] = meta.get("expertise", [])
            result["tools"] = meta.get("tools", [])
        self._send_json(200, result)

    def _handle_routines(self):
        """List loaded routines."""
        try:
            from mas.mas_routines import get_registry
            registry = get_registry()
            routines = []
            for rid, data in registry.items():
                routines.append({
                    "id": rid,
                    "name": data.get("name", rid),
                    "description": data.get("description", ""),
                    "domain": data.get("domain", ""),
                    "steps": len(data.get("steps", [])),
                    "triggers": len(data.get("triggers", [])),
                })
            self._send_json(200, {
                "enabled": cfg.get("routines_enabled", True),
                "count": len(routines),
                "routines": routines,
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_submit_request(self):
        """Submit a request for agent execution."""
        body = self._read_body()
        if _draining:
            self._send_json(503, {"error": "service shutting down"})
            return

        query = body.get("query", "").strip()
        if not query:
            self._send_json(400, {"error": "missing 'query' field"})
            return

        user = body.get("user", "")         # caller identification

        # Dedup check — reject identical query from same user within time window
        existing_id = _dedup_check(query, user)
        if existing_id:
            log(f"[DEDUP] query already processing as {existing_id}: {query[:80]}")
            self._send_json(200, {
                "request_id": existing_id,
                "status": "dedup",
                "message": f"Duplicate request — already processing as {existing_id}",
            })
            return

        # Optional overrides
        persona_ids = body.get("personas")  # force specific personas
        pattern = body.get("pattern")       # force specific pattern
        tribe = body.get("tribe")           # tribe constraint
        squad = body.get("squad")           # squad constraint
        max_personas = body.get("max_personas")  # cap agent count

        orch = _get_orchestrator()

        # Constitution check
        from mas.mas_constitution import check_input
        blocked, reason = check_input(query)
        if blocked:
            req = state.create_request(query, user=user)
            state.update_request(req.request_id, status="blocked", error=reason)
            state.record_event("block", f"P0 blocked: {reason}", req.request_id)
            log(f"[BLOCKED] {reason}")
            self._send_json(403, {
                "request_id": req.request_id,
                "status": "blocked",
                "reason": reason,
            })
            return

        # P1 refusal — refuse with helpful message instead of spawning agents
        if reason:
            req = state.create_request(query, user=user)
            state.update_request(req.request_id, status="refused", error=reason)
            state.record_event("refuse", f"P1 refused: {reason}", req.request_id)
            log(f"[REFUSED] {reason}")
            self._send_json(200, {
                "request_id": req.request_id,
                "status": "refused",
                "reason": reason,
                "message": "이 주제에 대해서는 전문가 상담을 권장합니다. AI 시스템은 의료, 법률, 금융 등 전문 분야의 조언을 제공할 수 없습니다.",
            })
            return

        # Start async execution
        req = state.create_request(query, user=user)
        _dedup_register(query, user, req.request_id)
        log(f"[REQUEST] {req.request_id}: {query[:80]}")

        def _run():
            try:
                orch.execute(req.request_id, query, persona_ids=persona_ids,
                            pattern=pattern, tribe=tribe, squad=squad,
                            max_personas=max_personas)
            except Exception as e:
                state.update_request(req.request_id, status="failed", error=str(e))
                log(f"[ERROR] {req.request_id}: {e}")

        threading.Thread(target=_run, daemon=True).start()

        self._send_json(202, {
            "request_id": req.request_id,
            "status": "pending",
            "message": "Request accepted, processing async",
        })

    def _handle_cancel(self):
        """Cancel an active request."""
        body = self._read_body()
        request_id = body.get("request_id", "").strip()
        if not request_id:
            self._send_json(400, {"error": "missing 'request_id' field"})
            return

        cancelled = state.cancel_request(request_id)
        if cancelled:
            log(f"[CANCEL] {request_id}")
            state.record_event("cancel", f"Request {request_id} cancelled", request_id)
            self._send_json(200, {
                "request_id": request_id,
                "cancelled": True,
                "message": "Request cancelled",
            })
        else:
            req = state.get_request(request_id)
            if not req:
                self._send_json(404, {
                    "request_id": request_id,
                    "cancelled": False,
                    "message": "Request not found",
                })
            else:
                self._send_json(409, {
                    "request_id": request_id,
                    "cancelled": False,
                    "message": f"Cannot cancel: status is {req.status}",
                })

    def _handle_list_requests(self):
        """List all active and recent requests."""
        from dataclasses import asdict
        all_reqs = state.get_all_requests()
        active = sum(1 for r in all_reqs.values()
                     if r.status in ("pending", "analyzing", "assembling",
                                     "running", "synthesizing"))
        summaries = []
        for r in sorted(all_reqs.values(), key=lambda x: x.created_at, reverse=True):
            summary = {
                "request_id": r.request_id,
                "status": r.status,
                "user_query": r.user_query,
                "pattern": r.pattern,
                "domain": r.domain,
                "tribe": r.tribe,
                "squad": r.squad,
                "user": r.user,
                "agent_count": len(r.agents),
                "selected_personas": r.selected_personas,
                "total_cost_usd": r.total_cost_usd,
                "total_tokens_used": r.total_tokens_used,
                "duration_ms": r.duration_ms,
                "created_at": r.created_at,
            }
            if r.error:
                summary["error"] = r.error
            if r.agents:
                failed = [a for a in r.agents if a.status == "failed"]
                if failed:
                    summary["failed_agents"] = [
                        {"callsign": a.callsign, "error": a.error}
                        for a in failed
                    ]
            summaries.append(summary)
        self._send_json(200, {
            "total": len(all_reqs),
            "active": active,
            "requests": summaries,
        })

    def _handle_persona_scores(self):
        """Return per-persona efficiency scores from performance ledger."""
        if not cfg.get("scoring_enabled", True):
            self._send_json(200, {"enabled": False, "scores": {}})
            return
        try:
            from mas.mas_scoring import get_scorer
            scorer = get_scorer()
            scores = scorer.get_all_scores()
            result = {}
            for pid, ps in scores.items():
                result[pid] = {
                    "total_requests": ps.total_requests,
                    "success_rate": round(ps.success_rate, 3),
                    "avg_cost_usd": round(ps.avg_cost_usd, 4),
                    "avg_duration_ms": ps.avg_duration_ms,
                    "efficiency_score": round(ps.efficiency_score, 4),
                    "functions": list(ps.by_function.keys()),
                }
            self._send_json(200, {"enabled": True, "count": len(result), "scores": result})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_function_ranking(self, func_key):
        """Return personas ranked by score for a function."""
        if not cfg.get("scoring_enabled", True):
            self._send_json(200, {"enabled": False, "ranking": []})
            return
        try:
            from mas.mas_scoring import get_scorer
            scorer = get_scorer()
            ranking = scorer.function_ranking(func_key)
            self._send_json(200, {"function": func_key, "ranking": ranking})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_get_request(self, request_id):
        """Get request status and results."""
        from dataclasses import asdict
        req = state.get_request(request_id)
        if not req:
            self._send_json(404, {"error": f"request {request_id} not found"})
            return

        self._send_json(200, asdict(req))


def _wait_for_xapi(max_wait: int = 30, interval: int = 2) -> bool:
    """Wait for xapi + Gateway to become ready before accepting requests.

    Checks /inference/capacity for full chain readiness (xapi + Gateway + tokens).
    Falls back to /health if /inference/capacity unavailable.
    Returns True if ready, False if timeout exceeded (MAS starts anyway with warning).
    """
    import urllib.request
    import urllib.error

    xapi_url = cfg.get("xapi_url", "http://localhost:7750")
    capacity_url = f"{xapi_url}/inference/capacity"
    health_url = f"{xapi_url}/health"
    deadline = time.time() + max_wait

    while time.time() < deadline:
        try:
            # Try /inference/capacity first — checks full chain
            req = urllib.request.Request(capacity_url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read())
                    gw_ok = data.get("gateway_healthy", False)
                    ready = data.get("ready", False)
                    if ready:
                        log(f"xapi ready at {xapi_url} (gateway_healthy={gw_ok}, "
                            f"tokens_available={data.get('tokens_available_pct', '?')}%)")
                        return True
                    remaining = int(deadline - time.time())
                    log(f"xapi up but not ready (gateway_healthy={gw_ok}) "
                        f"— waiting ({remaining}s remaining)...")
                    time.sleep(interval)
                    continue
        except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
            pass

        # Fallback: try /health (xapi might not have /inference/capacity)
        try:
            req = urllib.request.Request(health_url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    log(f"xapi ready at {xapi_url} (health-only, capacity endpoint unavailable)")
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            pass

        remaining = int(deadline - time.time())
        log(f"Waiting for xapi at {xapi_url} ({remaining}s remaining)...")
        time.sleep(interval)

    log(f"WARNING: xapi not reachable after {max_wait}s — starting anyway")
    return False


def main():
    log(f"Starting MAS on port {PORT}")

    # Load state + index
    state.load_state()
    idx = persona_idx.get_index()
    log(f"Loaded {idx.count()} personas")

    # Start background threads
    state.start_saver()
    cfg.start_hot_reload()
    persona_idx.start_hot_reload()

    # Start routine engine hot-reload
    if cfg.get("routines_enabled", True):
        try:
            from mas.mas_routines import start_hot_reload as start_routine_reload
            start_routine_reload()
            log("Routine engine started")
        except Exception as e:
            log(f"Routine engine failed to start: {e}")

    # Wait for xapi dependency before accepting requests
    _wait_for_xapi()

    # Start Slack if enabled
    if cfg.get_nested("slack", "enabled", False):
        try:
            from mas.mas_slack import start_slack
            start_slack()
            log("Slack Socket Mode started")
        except Exception as e:
            log(f"Slack failed to start: {e}")

    # HTTP server — allow_reuse_address prevents "Address already in use" on restart
    http.server.HTTPServer.allow_reuse_address = True
    server = http.server.HTTPServer(("0.0.0.0", PORT), MASHandler)
    log(f"Listening on :{PORT}")
    state.record_event("boot", f"MAS started on port {PORT}")

    def shutdown_handler(signum, frame):
        global _draining
        _draining = True
        log("Shutting down (draining — new requests rejected)...")
        state.save_state()
        # server.shutdown() from signal handler deadlocks:
        # it waits for serve_forever() which is blocked on this same thread.
        # Run in a separate thread so serve_forever() can exit its loop.
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Wait for in-flight requests to complete (up to shutdown_wait_seconds)
        # Daemon threads are killed on main thread exit, so this gives them
        # a chance to finish before the process terminates.
        wait_max = cfg.get("shutdown_wait_seconds", 30)
        active = state.count_active()
        if active > 0:
            log(f"Waiting for {active} active request(s) (max {wait_max}s)...")
            waited = 0
            while waited < wait_max:
                time.sleep(1)
                waited += 1
                active = state.count_active()
                if active == 0:
                    log(f"All requests completed after {waited}s")
                    break
            else:
                active = state.count_active()
                if active > 0:
                    log(f"Shutdown timeout: {active} request(s) still active after {wait_max}s")
        state.save_state()


if __name__ == "__main__":
    main()
