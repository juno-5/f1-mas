"""MAS Conversation Patterns — Single/Multi-Perspective/Relay/FullTeam execution."""

import re
import time
from concurrent.futures import ThreadPoolExecutor, Future

try:
    import httpx
except ImportError:
    httpx = None

from . import mas_config as cfg
from . import mas_state as state
from .mas_persona_index import PersonaEntry, PersonaIndex
from .mas_templates import (
    build_prompt, build_synthesis_prompt, select_template,
)
from .mas_agent_runner import run_agent, run_agents_parallel, run_synthesis
from .mas_insight_capture import strip_insights
from .mas_tools import get_tools_for_query


PATTERN_SINGLE = "single"
PATTERN_MULTI = "multi_perspective"
PATTERN_RELAY = "relay"
PATTERN_FULL_TEAM = "full_team"


def _log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [conversation] {msg}", flush=True)


def determine_pattern(analysis: dict, personas: list[PersonaEntry]) -> str:
    """Determine conversation pattern based on analysis and persona count."""
    count = len(personas)
    complexity = analysis.get("complexity", "simple")
    domains = analysis.get("domains", [])

    if count == 1:
        return PATTERN_SINGLE

    # Cross-domain → relay if 2, full_team if 3+
    if len(domains) > 1 and count >= 3:
        return PATTERN_FULL_TEAM

    # Relay pattern: when outputs chain naturally (e.g., copy → design)
    if count == 2 and _is_relay_pair(personas):
        return PATTERN_RELAY

    if count >= 3:
        return PATTERN_FULL_TEAM

    return PATTERN_MULTI


def _is_relay_pair(personas: list[PersonaEntry]) -> bool:
    """Check if two personas form a natural relay chain."""
    if len(personas) != 2:
        return False

    # Known relay pairs: branding → design, copy → design, strategy → execution
    relay_pairs = {
        ("branding", "design"),
        ("brand", "design"),
        ("commerce", "design"),
        ("growth", "commerce"),
        ("strategy", "design"),
        ("content", "design"),
    }

    cats = []
    for p in personas:
        for tag in p.tags:
            cats.append(tag.lower())
        # Also check role
        cats.append(p.role.lower())

    for a, b in relay_pairs:
        if any(a in c for c in cats[:len(personas[0].tags)+1]):
            if any(b in c for c in cats[len(personas[0].tags)+1:]):
                return True
    return False


def execute_pattern(
    request_id: str,
    query: str,
    personas: list[PersonaEntry],
    pattern: str,
    index: PersonaIndex,
) -> dict:
    """Execute the chosen conversation pattern.

    Returns {"synthesis": str, "agent_outputs": [...], "error": str|None}.
    """
    start = time.time()
    callsigns = [p.callsign for p in personas]

    if pattern == PATTERN_SINGLE:
        result = _execute_single(request_id, query, personas[0], index)
    elif pattern == PATTERN_MULTI:
        result = _execute_parallel(request_id, query, personas, index, pattern_name="Multi-Perspective")
    elif pattern == PATTERN_RELAY:
        result = _execute_relay(request_id, query, personas, index)
    elif pattern == PATTERN_FULL_TEAM:
        result = _execute_full_team(request_id, query, personas, index)
    else:
        result = _execute_single(request_id, query, personas[0], index)

    duration_ms = int((time.time() - start) * 1000)
    status = "OK" if not result.get("error") else f"ERROR: {result['error'][:60]}"
    _log(f"[{request_id}] DONE pattern={pattern} agents={callsigns} "
         f"duration={duration_ms}ms status={status}")
    return result



# ---------------------------------------------------------------------------
# AMM Circuit Breaker + Keyword Gating
# ---------------------------------------------------------------------------

class _AmmCircuitBreaker:
    """Simple circuit breaker for AMM service.

    States: CLOSED (normal) → OPEN (skip calls) → HALF-OPEN (try one call).
    """

    def __init__(self):
        self._fail_count = 0
        self._open_until = 0.0

    @property
    def is_open(self) -> bool:
        if self._open_until and time.time() < self._open_until:
            return True
        if self._open_until and time.time() >= self._open_until:
            # Half-open: allow one attempt, reset counter
            self._open_until = 0.0
            self._fail_count = 0
        return False

    def record_success(self):
        self._fail_count = 0
        self._open_until = 0.0

    def record_failure(self):
        threshold = cfg.get("amm_cb_fail_threshold", 3)
        cooldown = cfg.get("amm_cb_open_seconds", 300)
        self._fail_count += 1
        if self._fail_count >= threshold:
            self._open_until = time.time() + cooldown
            _log(f"AMM circuit breaker OPEN for {cooldown}s after {self._fail_count} failures")


_amm_cb = _AmmCircuitBreaker()

_AMM_TRIGGER_RE = re.compile(
    r"지난번|이전에|저번|예전에|기억|우리\s*브랜드|과거|히스토리|history|"
    r"remember|previous|last\s*time|before|기존|했던|했었|알려줬|말했|"
    r"참고.*자료|레퍼런스|reference|context|맥락",
    re.IGNORECASE,
)

_amm_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="amm")


def _should_call_amm(query: str) -> bool:
    """Determine if AMM memory lookup is needed for this query.

    Policy modes (amm_policy config key):
      - "always": always call AMM
      - "never": never call AMM
      - "auto" (default): keyword-based gating
    """
    policy = cfg.get("amm_policy", "auto")
    if policy == "always":
        return True
    if policy == "never":
        return False
    # auto: keyword-based gating
    return bool(_AMM_TRIGGER_RE.search(query))


def _fetch_amm_memories(query: str, limit: int = 3, persona_role: str = "") -> str:
    """Fetch relevant AMM memories — conditional + circuit breaker + fast timeout."""
    if not cfg.get("amm_memory_injection", True):
        return ""
    if httpx is None:
        return ""

    # Keyword gating: skip AMM for queries that don't need memory
    if not _should_call_amm(query):
        _log("AMM: skipped (no memory keywords)")
        return ""

    # Circuit breaker: skip if AMM is failing
    if _amm_cb.is_open:
        _log("AMM: skipped (circuit breaker OPEN)")
        return ""

    _log(f"AMM: fetching memories for query: {query[:60]}...")
    xapi_url = cfg.get("xapi_url", "http://localhost:7750")
    timeout = cfg.get("amm_timeout", 1.5)

    try:
        resp = httpx.post(
            f"{xapi_url}/amm/surface",
            json={
                "query": query,
                "limit": limit,
                "min_relevance": 0.4,
            },
            timeout=timeout,
        )
        if resp.status_code != 200:
            _amm_cb.record_failure()
            return ""

        _amm_cb.record_success()
        data = resp.json()
        memories = data.get("memories", [])
        if not memories:
            return ""

        sections = []
        for m in memories[:limit]:
            title = m.get("raw_title", m.get("title", ""))
            interp = m.get("interpretation", "")[:200]
            source = m.get("source_url", "")
            rel = m.get("score", m.get("relevance_score", 0))
            if title and interp:
                entry = f"- **{title}** (rel={rel:.2f}): {interp}"
                if source:
                    entry += "\n  Source: " + source
                sections.append(entry)

        if not sections:
            _log("AMM: no sections built")
            return ""

        result = "\n\n## Recent Intelligence (AMM Memory)\n" + "\n".join(sections)
        _log(f"AMM: injecting {len(sections)} memories ({len(result)} chars)")
        return result
    except Exception as e:
        _amm_cb.record_failure()
        _log(f"AMM memory fetch ERROR: {e}")
        return ""


def _fetch_amm_async(query: str, limit: int = 3) -> "Future[str]":
    """Launch AMM fetch in background thread. Returns a Future.

    Use future.result(timeout=0) to get result without blocking,
    or just ignore if agent execution finished first.
    """
    return _amm_executor.submit(_fetch_amm_memories, query, limit)


_NAS_RELEVANT_RE = re.compile(
    r"노드|node|서버|server|배포|deploy|인프라|infra|클라우드|cloud|PC|"
    r"원격|remote|실행|exec|파일|file|문서.*검색|doc.*search|NAS",
    re.IGNORECASE,
)

# NAS circuit breaker — same pattern as AMM
_nas_cb = _AmmCircuitBreaker()


def _fetch_nas_context(query: str, domain: str = "") -> str:
    """Fetch NAS node info + relevant docs — with circuit breaker + reduced timeout."""
    if not cfg.get("nas_context_injection", True):
        return ""
    if httpx is None:
        return ""
    # Only inject when query explicitly mentions NAS-relevant keywords
    if not _NAS_RELEVANT_RE.search(query):
        return ""

    # Circuit breaker
    if _nas_cb.is_open:
        _log("NAS: skipped (circuit breaker OPEN)")
        return ""

    nas_url = cfg.get("nas_url", "http://localhost:7730")
    timeout = cfg.get("nas_timeout", 2.0)
    doc_limit = cfg.get("nas_doc_limit", 3)

    sections = []
    try:
        # 1. Available nodes
        resp = httpx.get(f"{nas_url}/nodes", timeout=timeout)
        if resp.status_code != 200:
            _nas_cb.record_failure()
            return ""
        _nas_cb.record_success()

        data = resp.json()
        nodes = data.get("nodes", [])
        online = [n for n in nodes if n.get("status") == "online"]
        if online:
            node_lines = []
            for n in online:
                nid = n.get("node_id", "?")
                ip = n.get("ip_address", "?")
                os_info = n.get("os_info", "?")
                cpu = n.get("cpu_percent", 0)
                mem = n.get("mem_percent", 0)
                node_lines.append(f"- **{nid}** ({os_info}) IP={ip} CPU={cpu}% MEM={mem}%")
            sections.append("### Available Nodes\n" + "\n".join(node_lines))
            sections.append(
                "### Node Commands\n"
                f"원격 실행: `POST {nas_url}/nodes/{{node_id}}/exec` "
                '`{"command": "...", "timeout": 30}`'
            )

        # 2. Relevant docs
        resp = httpx.get(
            f"{nas_url}/docs/search",
            params={"q": query[:100], "limit": doc_limit},
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            docs = data.get("docs", [])
            if docs:
                doc_lines = []
                for d in docs[:doc_limit]:
                    title = d.get("title", d.get("filename", "?"))
                    preview = d.get("preview", "")[:120]
                    doc_id = d.get("doc_id", "")
                    doc_lines.append(f"- **{title}** (id={doc_id}): {preview}")
                sections.append("### Related Documents\n" + "\n".join(doc_lines))
                sections.append(
                    f"문서 상세: `GET {nas_url}/docs/{{doc_id}}`\n"
                    f"문서 검색: `GET {nas_url}/docs/search?q=키워드`"
                )

    except Exception as e:
        _nas_cb.record_failure()
        _log(f"NAS context fetch ERROR: {e}")
        return ""

    if not sections:
        return ""

    result = "\n\n## Infrastructure Resources (NAS)\n" + "\n\n".join(sections)
    _log(f"NAS: injecting context ({len(result)} chars)")
    return result


def _fetch_library_context(domain: str) -> str:
    """Fetch team library references + recent insights for prompt injection."""
    try:
        from .mas_insight_capture import fetch_library_context
        return fetch_library_context(domain)
    except Exception as e:
        _log(f"Library context fetch ERROR: {e}")
        return ""


def _build_agent_prompt(persona: PersonaEntry, query: str, index: PersonaIndex,
                        extra_context: str = "", amm_context: str = None,
                        nas_context: str = None, library_context: str = None,
                        domain: str = "") -> str:
    """Build a prompt for a persona agent.

    Args:
        amm_context: Pre-fetched AMM memories. If None, fetches independently.
            Pass pre-fetched value for multi-agent patterns to avoid redundant calls.
        nas_context: Pre-fetched NAS context. If None, fetches independently.
        library_context: Pre-fetched library context. If None, fetches independently.
        domain: Primary domain for NAS relevance check.
    """
    # Extract key sections from character file
    char_content = index.extract_character_sections(persona.id)
    if not char_content:
        char_content = f"# {persona.callsign}\n{persona.role}\n{persona.name}"

    template_id = select_template(persona.category, persona.tags)

    # AMM Memory Injection — use pre-fetched if available
    if amm_context is None:
        amm_context = _fetch_amm_memories(query, persona_role=persona.role if hasattr(persona, "role") else "")

    # NAS Context Injection — use pre-fetched if available
    if nas_context is None:
        nas_context = _fetch_nas_context(query, domain=domain or persona.category)

    # Library Context Injection — team references + recent insights
    if library_context is None:
        library_context = _fetch_library_context(domain or persona.category)

    full_query = query
    if library_context:
        full_query += library_context
    if amm_context:
        full_query += amm_context
    if nas_context:
        full_query += nas_context
    if extra_context:
        full_query += f"\n\n## Previous Context\n{extra_context}"

    result = build_prompt(
        template_id=template_id,
        character_content=char_content,
        callsign=persona.callsign,
        role=persona.role,
        user_request=full_query,
        sense=persona.specialty,
    )
    return result


def _execute_single(request_id: str, query: str, persona: PersonaEntry, index: PersonaIndex) -> dict:
    """Single Expert: 1 agent, direct response."""
    _log(f"[{request_id}] Single Expert: {persona.callsign}")

    agent_id = state.add_agent(request_id, persona.id, persona.callsign, persona.role)
    nas_context = _fetch_nas_context(query, domain=persona.category)
    library_context = _fetch_library_context(persona.category)
    prompt = _build_agent_prompt(persona, query, index, nas_context=nas_context,
                                 library_context=library_context)

    # Determine available tools for this query
    tools = get_tools_for_query(query, domain=persona.category) or None
    if tools:
        _log(f"[{request_id}] Tools enabled: {len(tools)} tool(s)")

    # Notify Slack progress
    _slack_agent_progress(request_id, persona.callsign, "running")

    result = run_agent(request_id, agent_id, prompt, persona.id, persona.callsign, tools=tools, query=query)

    _slack_agent_progress(request_id, persona.callsign,
                          "completed" if not result.get("error") else "failed")

    if result.get("error"):
        return {"synthesis": "", "agent_outputs": [result], "error": result["error"]}

    # Single expert: output IS the synthesis
    synthesis = f"## {persona.callsign} ({persona.role})\n\n{result['text']}"
    return {"synthesis": synthesis, "agent_outputs": [result], "error": None}


def _execute_parallel(
    request_id: str, query: str, personas: list[PersonaEntry], index: PersonaIndex,
    pattern_name: str = "Parallel",
) -> dict:
    """Parallel execution: register → run parallel → synthesize.

    Used by both multi_perspective and full_team patterns.
    AMM fetch runs async in parallel with agent inference, injected at synthesis.
    """
    _log(f"[{request_id}] {pattern_name}: {[p.callsign for p in personas]}")

    # Launch AMM fetch async — runs in parallel with agent inference
    amm_future = _fetch_amm_async(query)

    # NAS context (sync, keyword-gated so usually skipped)
    nas_context = _fetch_nas_context(query, domain=personas[0].category if personas else "")

    # Determine available tools for this query
    tools = get_tools_for_query(query, domain=personas[0].category if personas else "") or None
    if tools:
        _log(f"[{request_id}] Tools enabled: {len(tools)} tool(s)")

    # Register agents — build prompts WITHOUT AMM (injected at synthesis)
    agents_info = []
    for p in personas:
        agent_id = state.add_agent(request_id, p.id, p.callsign, p.role)
        prompt = _build_agent_prompt(p, query, index, amm_context="",
                                     nas_context=nas_context)
        agents_info.append({
            "agent_id": agent_id,
            "prompt": prompt,
            "persona_id": p.id,
            "callsign": p.callsign,
            "role": p.role,
            "tools": tools,
            "query": query,
        })
        _slack_agent_progress(request_id, p.callsign, "running")

    # Run in parallel (AMM fetch also running concurrently)
    results = run_agents_parallel(request_id, agents_info)

    # Notify completion
    for ai, r in zip(agents_info, results):
        _slack_agent_progress(request_id, ai["callsign"],
                              "completed" if not r.get("error") else "failed")

    # Collect AMM result (non-blocking — should be done by now)
    amm_context = ""
    try:
        amm_context = amm_future.result(timeout=0.5)
    except Exception:
        _log(f"[{request_id}] AMM async: not available at synthesis time")

    # Progressive synthesis: synthesize with whatever succeeded
    successful = [(ai, r) for ai, r in zip(agents_info, results) if not r.get("error")]
    failed = [(ai, r) for ai, r in zip(agents_info, results) if r.get("error")]
    if failed:
        _log(f"[{request_id}] {len(failed)}/{len(agents_info)} agents failed, "
             f"synthesizing with {len(successful)} successful")

    if not successful:
        return {"synthesis": "", "agent_outputs": results,
                "error": "all agents failed"}

    # If only 1 succeeded, skip synthesis
    if len(successful) == 1:
        ai, r = successful[0]
        text = r['text']
        if amm_context:
            text = amm_context + "\n\n" + text
        return {
            "synthesis": f"## {ai['callsign']} ({ai['role']})\n\n{text}",
            "agent_outputs": results, "error": None,
        }

    # Synthesize with available results (don't wait for slow agents)
    state.update_request(request_id, status="synthesizing")
    max_input_chars = cfg.get("synthesis_max_input_chars", 4000)

    # Build synthesis query — inject AMM context if available
    synth_query = query
    if amm_context:
        synth_query = query + amm_context

    # Strip [INSIGHT] blocks from agent outputs before synthesis —
    # agent insights are captured separately; including them causes duplicates.
    synth_prompt = build_synthesis_prompt(
        synth_query,
        [{"callsign": ai["callsign"], "role": ai["role"],
          "output": strip_insights(r["text"])}
         for ai, r in successful],
        max_chars_per_agent=max_input_chars,
    )

    synth_result = run_synthesis(request_id, synth_prompt)

    if synth_result.get("error"):
        # Fallback: concatenate outputs without synthesis
        parts = [f"### {ai['callsign']} ({ai['role']})\n{r['text']}"
                 for ai, r in successful]
        return {
            "synthesis": "\n\n---\n\n".join(parts),
            "agent_outputs": results, "error": None,
        }

    return {
        "synthesis": synth_result["text"],
        "agent_outputs": results, "error": None,
    }


def _execute_relay(
    request_id: str, query: str, personas: list[PersonaEntry], index: PersonaIndex
) -> dict:
    """Relay: A's output → B's input, sequential."""
    _log(f"[{request_id}] Relay: {' → '.join(p.callsign for p in personas)}")

    # AMM: conditional + fast-fail (relay is sequential, async has less benefit)
    amm_context = _fetch_amm_memories(query)
    nas_context = _fetch_nas_context(query, domain=personas[0].category if personas else "")

    # Determine available tools for this query
    tools = get_tools_for_query(query, domain=personas[0].category if personas else "") or None
    if tools:
        _log(f"[{request_id}] Tools enabled: {len(tools)} tool(s)")

    all_results = []
    previous_output = ""

    for i, persona in enumerate(personas):
        agent_id = state.add_agent(request_id, persona.id, persona.callsign, persona.role)
        prompt = _build_agent_prompt(persona, query, index, extra_context=previous_output,
                                     amm_context=amm_context, nas_context=nas_context)

        _slack_agent_progress(request_id, persona.callsign, "running")
        result = run_agent(request_id, agent_id, prompt, persona.id, persona.callsign, tools=tools, query=query)
        all_results.append(result)

        status = "completed" if not result.get("error") else "failed"
        _slack_agent_progress(request_id, persona.callsign, status)

        if result.get("error"):
            # Relay breaks on failure
            return {"synthesis": "", "agent_outputs": all_results,
                    "error": f"Relay broke at {persona.callsign}: {result['error']}"}

        previous_output = result["text"]

    # Final output is the last agent's output, with attribution
    synthesis_parts = []
    for persona, result in zip(personas, all_results):
        synthesis_parts.append(f"### {persona.callsign} ({persona.role})\n{result['text']}")

    return {
        "synthesis": "\n\n---\n\n".join(synthesis_parts),
        "agent_outputs": all_results, "error": None,
    }


def _execute_full_team(
    request_id: str, query: str, personas: list[PersonaEntry], index: PersonaIndex
) -> dict:
    """Full Team: parallel execution + synthesis."""
    return _execute_parallel(request_id, query, personas, index, pattern_name="Full Team")


def _slack_agent_progress(request_id: str, callsign: str, status: str):
    """Notify Slack about agent progress."""
    if not cfg.get_nested("slack", "enabled", False):
        return
    try:
        from .mas_slack import notify_agent_progress
        notify_agent_progress(request_id, callsign, status)
    except Exception:
        pass
