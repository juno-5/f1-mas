"""MAS State Management — atomic JSON state with request/agent tracking."""

import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum

from f1common.io import save_json_atomic
from f1common.events import record_event as _common_record_event

from . import mas_config as cfg


class RequestStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    ASSEMBLING = "assembling"
    RUNNING = "running"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    agent_id: str = ""
    persona_id: str = ""
    callsign: str = ""
    role: str = ""
    status: str = "pending"
    started_at: float = 0.0
    completed_at: float = 0.0
    duration_ms: int = 0
    output: str = ""
    error: str = ""
    tokens_used: int = 0
    model: str = ""


@dataclass
class RequestState:
    request_id: str = ""
    user_query: str = ""
    status: str = "pending"
    pattern: str = "single"  # single/multi_perspective/relay/full_team
    created_at: float = 0.0
    completed_at: float = 0.0
    duration_ms: int = 0
    agents: list[AgentState] = field(default_factory=list)
    synthesis: str = ""
    domain: str = ""
    locale: str = ""
    selected_personas: list[str] = field(default_factory=list)
    slack_thread_ts: str = ""
    error: str = ""


_state_lock = threading.Lock()
_requests: dict[str, RequestState] = {}
_timeline: list[dict] = []
_counters = {
    "total_requests": 0,
    "completed_requests": 0,
    "failed_requests": 0,
    "blocked_requests": 0,
    "total_agents_spawned": 0,
    "total_tokens_used": 0,
}


def _state_file():
    return cfg.get("state_file", os.path.expanduser("~/.f1crew/shared/mas-state.json"))


def _save():
    """Atomic JSON write via f1common."""
    path = _state_file()
    try:
        data = {
            "version": 1,
            "saved_at": time.time(),
            "counters": _counters,
            "timeline": _timeline[-200:],
            "active_requests": {
                rid: asdict(r) for rid, r in _requests.items()
                if r.status in ("pending", "analyzing", "assembling", "running", "synthesizing")
            },
        }
        save_json_atomic(path, data)
    except OSError:
        pass


def _load():
    """Load state from file (counters + timeline only; active requests reset on boot)."""
    global _counters, _timeline
    path = _state_file()
    try:
        with open(path, "r") as f:
            data = json.load(f)
        _counters.update(data.get("counters", {}))
        _timeline = data.get("timeline", [])[-200:]
    except (FileNotFoundError, json.JSONDecodeError):
        pass


def record_event(event_type: str, detail: str, request_id: str = ""):
    """Append to activity timeline via f1common."""
    with _state_lock:
        extra = {"request_id": request_id} if request_id else {}
        _common_record_event(_timeline, event_type, detail, **extra)


def create_request(user_query: str) -> RequestState:
    """Create a new request and return its state."""
    req = RequestState(
        request_id=str(uuid.uuid4())[:8],
        user_query=user_query,
        status=RequestStatus.PENDING,
        created_at=time.time(),
    )
    with _state_lock:
        _requests[req.request_id] = req
        _counters["total_requests"] += 1
    record_event("request", f"New request: {user_query[:80]}", req.request_id)
    return req


def update_request(request_id: str, **kwargs):
    """Update request fields."""
    with _state_lock:
        req = _requests.get(request_id)
        if not req:
            return
        for k, v in kwargs.items():
            if hasattr(req, k):
                setattr(req, k, v)
        if kwargs.get("status") == RequestStatus.COMPLETED:
            req.completed_at = time.time()
            req.duration_ms = int((req.completed_at - req.created_at) * 1000)
            _counters["completed_requests"] += 1
        elif kwargs.get("status") == RequestStatus.FAILED:
            req.completed_at = time.time()
            req.duration_ms = int((req.completed_at - req.created_at) * 1000)
            _counters["failed_requests"] += 1
        elif kwargs.get("status") == RequestStatus.BLOCKED:
            _counters["blocked_requests"] += 1


def add_agent(request_id: str, persona_id: str, callsign: str, role: str) -> str:
    """Add an agent to a request, return agent_id."""
    agent_id = str(uuid.uuid4())[:8]
    agent = AgentState(
        agent_id=agent_id,
        persona_id=persona_id,
        callsign=callsign,
        role=role,
        status=AgentStatus.PENDING,
    )
    with _state_lock:
        req = _requests.get(request_id)
        if req:
            req.agents.append(agent)
            _counters["total_agents_spawned"] += 1
    return agent_id


def update_agent(request_id: str, agent_id: str, **kwargs):
    """Update agent fields within a request."""
    with _state_lock:
        req = _requests.get(request_id)
        if not req:
            return
        for agent in req.agents:
            if agent.agent_id == agent_id:
                for k, v in kwargs.items():
                    if hasattr(agent, k):
                        setattr(agent, k, v)
                if kwargs.get("status") == AgentStatus.COMPLETED:
                    agent.completed_at = time.time()
                    agent.duration_ms = int((agent.completed_at - agent.started_at) * 1000)
                    _counters["total_tokens_used"] += agent.tokens_used
                break


def get_request(request_id: str) -> RequestState | None:
    with _state_lock:
        return _requests.get(request_id)


def get_all_requests() -> dict[str, RequestState]:
    with _state_lock:
        return dict(_requests)


def get_counters() -> dict:
    with _state_lock:
        return dict(_counters)


def get_timeline(limit: int = 50) -> list[dict]:
    with _state_lock:
        return _timeline[-limit:]


def save_state():
    with _state_lock:
        _save()


def load_state():
    with _state_lock:
        _load()


def _save_periodic():
    while True:
        time.sleep(60)
        save_state()


def start_saver():
    t = threading.Thread(target=_save_periodic, daemon=True)
    t.start()
