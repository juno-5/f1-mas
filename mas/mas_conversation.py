"""MAS Conversation Patterns — Single/Multi-Perspective/Relay/FullTeam execution."""

import time

from . import mas_config as cfg
from . import mas_state as state
from .mas_persona_index import PersonaEntry, PersonaIndex
from .mas_templates import (
    build_prompt, build_synthesis_prompt, select_template,
)
from .mas_agent_runner import run_agent, run_agents_parallel, run_synthesis


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
    if pattern == PATTERN_SINGLE:
        return _execute_single(request_id, query, personas[0], index)
    elif pattern == PATTERN_MULTI:
        return _execute_multi_perspective(request_id, query, personas, index)
    elif pattern == PATTERN_RELAY:
        return _execute_relay(request_id, query, personas, index)
    elif pattern == PATTERN_FULL_TEAM:
        return _execute_full_team(request_id, query, personas, index)
    else:
        return _execute_single(request_id, query, personas[0], index)


def _build_agent_prompt(persona: PersonaEntry, query: str, index: PersonaIndex, extra_context: str = "") -> str:
    """Build a prompt for a persona agent."""
    # Extract key sections from character file
    char_content = index.extract_character_sections(persona.id)
    if not char_content:
        char_content = f"# {persona.callsign}\n{persona.role}\n{persona.name}"

    template_id = select_template(persona.category, persona.tags)

    full_query = query
    if extra_context:
        full_query = f"{query}\n\n## Previous Context\n{extra_context}"

    return build_prompt(
        template_id=template_id,
        character_content=char_content,
        callsign=persona.callsign,
        role=persona.role,
        user_request=full_query,
        sense=persona.specialty,
    )


def _execute_single(request_id: str, query: str, persona: PersonaEntry, index: PersonaIndex) -> dict:
    """Single Expert: 1 agent, direct response."""
    _log(f"[{request_id}] Single Expert: {persona.callsign}")

    agent_id = state.add_agent(request_id, persona.id, persona.callsign, persona.role)
    prompt = _build_agent_prompt(persona, query, index)

    # Notify Slack progress
    _slack_agent_progress(request_id, persona.callsign, "running")

    result = run_agent(request_id, agent_id, prompt, persona.id, persona.callsign)

    _slack_agent_progress(request_id, persona.callsign,
                          "completed" if not result.get("error") else "failed")

    if result.get("error"):
        return {"synthesis": "", "agent_outputs": [result], "error": result["error"]}

    # Single expert: output IS the synthesis
    synthesis = f"## {persona.callsign} ({persona.role})\n\n{result['text']}"
    return {"synthesis": synthesis, "agent_outputs": [result], "error": None}


def _execute_multi_perspective(
    request_id: str, query: str, personas: list[PersonaEntry], index: PersonaIndex
) -> dict:
    """Multi-Perspective: 2-3 agents in parallel → synthesize."""
    _log(f"[{request_id}] Multi-Perspective: {[p.callsign for p in personas]}")

    # Register agents
    agents_info = []
    for p in personas:
        agent_id = state.add_agent(request_id, p.id, p.callsign, p.role)
        prompt = _build_agent_prompt(p, query, index)
        agents_info.append({
            "agent_id": agent_id,
            "prompt": prompt,
            "persona_id": p.id,
            "callsign": p.callsign,
            "role": p.role,
        })
        _slack_agent_progress(request_id, p.callsign, "running")

    # Run in parallel
    results = run_agents_parallel(request_id, agents_info)

    # Notify completion
    for ai, r in zip(agents_info, results):
        _slack_agent_progress(request_id, ai["callsign"],
                              "completed" if not r.get("error") else "failed")

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
        return {
            "synthesis": f"## {ai['callsign']} ({ai['role']})\n\n{r['text']}",
            "agent_outputs": results, "error": None,
        }

    # Synthesize with available results (don't wait for slow agents)
    state.update_request(request_id, status="synthesizing")
    synth_prompt = build_synthesis_prompt(
        query,
        [{"callsign": ai["callsign"], "role": ai["role"], "output": r["text"]}
         for ai, r in successful],
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

    all_results = []
    previous_output = ""

    for i, persona in enumerate(personas):
        agent_id = state.add_agent(request_id, persona.id, persona.callsign, persona.role)
        prompt = _build_agent_prompt(persona, query, index, extra_context=previous_output)

        _slack_agent_progress(request_id, persona.callsign, "running")
        result = run_agent(request_id, agent_id, prompt, persona.id, persona.callsign)
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
    """Full Team: parallel execution + synthesis + optional relay."""
    _log(f"[{request_id}] Full Team: {[p.callsign for p in personas]}")

    # Run all in parallel first
    agents_info = []
    for p in personas:
        agent_id = state.add_agent(request_id, p.id, p.callsign, p.role)
        prompt = _build_agent_prompt(p, query, index)
        agents_info.append({
            "agent_id": agent_id,
            "prompt": prompt,
            "persona_id": p.id,
            "callsign": p.callsign,
            "role": p.role,
        })
        _slack_agent_progress(request_id, p.callsign, "running")

    results = run_agents_parallel(request_id, agents_info)

    for ai, r in zip(agents_info, results):
        _slack_agent_progress(request_id, ai["callsign"],
                              "completed" if not r.get("error") else "failed")

    # Progressive synthesis: synthesize with whatever succeeded
    successful = [(ai, r) for ai, r in zip(agents_info, results) if not r.get("error")]
    failed_team = [(ai, r) for ai, r in zip(agents_info, results) if r.get("error")]
    if failed_team:
        _log(f"[{request_id}] Full Team: {len(failed_team)}/{len(agents_info)} agents failed, "
             f"synthesizing with {len(successful)} successful")

    if not successful:
        return {"synthesis": "", "agent_outputs": results,
                "error": "all agents failed"}

    if len(successful) == 1:
        ai, r = successful[0]
        return {
            "synthesis": f"## {ai['callsign']} ({ai['role']})\n\n{r['text']}",
            "agent_outputs": results, "error": None,
        }

    # Synthesize with available results
    state.update_request(request_id, status="synthesizing")
    synth_prompt = build_synthesis_prompt(
        query,
        [{"callsign": ai["callsign"], "role": ai["role"], "output": r["text"]}
         for ai, r in successful],
    )

    synth_result = run_synthesis(request_id, synth_prompt)

    if synth_result.get("error"):
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


def _slack_agent_progress(request_id: str, callsign: str, status: str):
    """Notify Slack about agent progress."""
    if not cfg.get_nested("slack", "enabled", False):
        return
    try:
        from .mas_slack import notify_agent_progress
        notify_agent_progress(request_id, callsign, status)
    except Exception:
        pass
