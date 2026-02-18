#!/usr/bin/env python3
"""
MAS (Master Agent System) Server — Port 7720
Orchestrates 158 expert personas for multi-agent task execution.

Endpoints:
  GET  /health              — Health check
  GET  /status              — Service status + counters
  GET  /metrics             — Prometheus metrics
  GET  /personas            — List all personas
  GET  /personas/select     — Dry-run persona selection
  POST /request             — Submit a task request
  GET  /request/<id>        — Get request status
"""

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
        elif path.startswith("/request/"):
            req_id = path.split("/request/")[1]
            self._handle_get_request(req_id)
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        path, params = self._parse_path()

        if path == "/request":
            self._handle_submit_request()
        else:
            self._send_json(404, {"error": "not found"})

    # ── Handlers ──

    def _handle_health(self):
        idx = persona_idx.get_index()
        self._send_json(200, {
            "status": "ok",
            "personas_loaded": idx.count(),
            "uptime_seconds": int(time.time() - _start_time),
        })

    def _handle_status(self):
        idx = persona_idx.get_index()
        counters = state.get_counters()
        timeline = state.get_timeline(20)

        self._send_json(200, {
            "uptime_seconds": int(time.time() - _start_time),
            "personas_loaded": idx.count(),
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

        orch = _get_orchestrator()
        analysis = orch.analyze_request(query)
        selected = orch.select_personas(analysis)

        self._send_json(200, {
            "query": query,
            "analysis": analysis,
            "selected": [
                {"id": e.id, "name": e.name, "callsign": e.callsign,
                 "role": e.role, "category": e.category}
                for e in selected
            ],
        })

    def _handle_submit_request(self):
        """Submit a request for agent execution."""
        body = self._read_body()
        query = body.get("query", "").strip()
        if not query:
            self._send_json(400, {"error": "missing 'query' field"})
            return

        # Optional overrides
        persona_ids = body.get("personas")  # force specific personas
        pattern = body.get("pattern")       # force specific pattern

        orch = _get_orchestrator()

        # Constitution check
        from mas.mas_constitution import check_input
        blocked, reason = check_input(query)
        if blocked:
            req = state.create_request(query)
            state.update_request(req.request_id, status="blocked", error=reason)
            state.record_event("block", f"P0 blocked: {reason}", req.request_id)
            log(f"[BLOCKED] {reason}")
            self._send_json(403, {
                "request_id": req.request_id,
                "status": "blocked",
                "reason": reason,
            })
            return

        # Start async execution
        req = state.create_request(query)
        log(f"[REQUEST] {req.request_id}: {query[:80]}")

        def _run():
            try:
                orch.execute(req.request_id, query, persona_ids=persona_ids, pattern=pattern)
            except Exception as e:
                state.update_request(req.request_id, status="failed", error=str(e))
                log(f"[ERROR] {req.request_id}: {e}")

        threading.Thread(target=_run, daemon=True).start()

        self._send_json(202, {
            "request_id": req.request_id,
            "status": "pending",
            "message": "Request accepted, processing async",
        })

    def _handle_get_request(self, request_id):
        """Get request status and results."""
        from dataclasses import asdict
        req = state.get_request(request_id)
        if not req:
            self._send_json(404, {"error": f"request {request_id} not found"})
            return

        self._send_json(200, asdict(req))


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

    # Start Slack if enabled
    if cfg.get_nested("slack", "enabled", False):
        try:
            from mas.mas_slack import start_slack
            start_slack()
            log("Slack Socket Mode started")
        except Exception as e:
            log(f"Slack failed to start: {e}")

    # HTTP server
    server = http.server.HTTPServer(("0.0.0.0", PORT), MASHandler)
    log(f"Listening on :{PORT}")
    state.record_event("boot", f"MAS started on port {PORT}")

    def shutdown_handler(signum, frame):
        log("Shutting down...")
        state.save_state()
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        state.save_state()


if __name__ == "__main__":
    main()
