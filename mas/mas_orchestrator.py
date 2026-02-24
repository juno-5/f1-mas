"""MAS Orchestrator — analyze request → select personas → spawn agents → synthesize."""

import re
import time

from . import mas_config as cfg
from . import mas_state as state
from .mas_persona_index import get_index, PersonaEntry
from .mas_templates import (
    build_prompt, build_synthesis_prompt, select_template,
    TECHNICAL_REVIEW, MARKETING_CAMPAIGN, CONTENT_MODEL,
    CREATIVE_DIRECTION, GENERATIVE_AI, SYNTHESIS,
)
from .mas_agent_runner import run_agent, run_agents_parallel, run_synthesis
from .mas_conversation import execute_pattern, determine_pattern

def _log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [orchestrator] {msg}", flush=True)


class Orchestrator:
    def __init__(self):
        self._index = get_index()

    # Metadata prefixes to strip before function/domain detection.
    # These are non-content tags that can trigger false positives.
    _METADATA_PREFIX_RE = re.compile(
        r"^\[auto[-\w]*\]\s*"          # [auto-debug], [auto-zero], etc.
        r"(?:Cycle\s*#\d+[:\s]*)?",    # optional "Cycle #N:"
        re.IGNORECASE,
    )

    def analyze_request(self, query: str, pattern: str = None,
                        tribe: str = None, squad: str = None) -> dict:
        """Analyze user request: detect domain, function, locale, complexity.

        Returns {"domains": [...], "functions": [...], "locale": str,
                 "complexity": str, "agent_count": int}.
        """
        # Strip metadata prefixes to avoid false positives in detection
        clean_query = self._METADATA_PREFIX_RE.sub("", query).strip() or query

        # Domain detection
        domains = self._index.detect_domain(clean_query)

        # Function detection (from org/functions.yaml)
        functions = self._index.detect_function(clean_query)

        # Cycle #59: When domain defaults to ["developers"] but functions matched,
        # infer domain from function candidates' categories.
        if domains == ["developers"] and functions:
            inferred = self._infer_domain_from_functions(functions)
            if inferred:
                domains = inferred

        # Locale detection
        locale = self._index.detect_locale(clean_query)

        # Complexity estimation — use domain-relevant function count to avoid
        # unrelated cross-domain functions inflating agent count
        query_len = len(clean_query)
        primary_domain = domains[0]
        domain_set = set(domains)
        domain_func_count = 0
        for func in functions:
            candidates = self._index.by_function(func)
            if candidates and any(c.category in domain_set for c in candidates):
                domain_func_count += 1
        # Use domain func count for sizing, but at least 1 if any functions matched
        effective_count = max(domain_func_count, 1) if functions else 0

        if query_len < 50 and effective_count <= 1:
            complexity = "simple"
            agent_count = 1
        elif query_len < 200 and effective_count <= 2:
            complexity = "focused"
            agent_count = min(2, effective_count + 1)
        elif len(domains) > 1 or effective_count >= 3:
            complexity = "full_project"
            agent_count = min(5, effective_count + 1)
        else:
            complexity = "multi_faceted"
            agent_count = min(3, effective_count + 1)

        # Pattern-based minimum: multi_perspective needs 2+, full_team needs 3+
        if pattern == "multi_perspective":
            agent_count = max(agent_count, 2)
        elif pattern == "full_team":
            agent_count = max(agent_count, 3)

        # Ensure at least 1 agent
        agent_count = max(1, agent_count)

        # Cost-aware agent count cap
        if cfg.get("cost_aware_limiting", True):
            try:
                from .mas_scoring import get_scorer
                avg_cost = get_scorer().global_avg_cost_per_agent()
                budget = cfg.get("per_request_budget_usd", 0.50)
                if avg_cost > 0:
                    max_by_budget = max(1, int(budget / avg_cost))
                    agent_count = min(agent_count, max_by_budget)
            except Exception:
                pass  # scoring not ready yet, skip

        # Tribe/Squad resolution
        resolved_squad = squad or self._index.detect_squad(query)
        resolved_tribe = tribe or self._index.detect_tribe(query)
        # Squad→tribe is authoritative (squad is more specific than tribe keyword matching)
        if resolved_squad:
            sq = self._index.get_squad(resolved_squad)
            if sq:
                resolved_tribe = sq.tribe_id

        return {
            "domains": domains,
            "functions": functions if functions else [self._default_function(domains[0])],
            "locale": locale,
            "complexity": complexity,
            "agent_count": agent_count,
            "tribe": resolved_tribe or "",
            "squad": resolved_squad or "",
            "_squad_explicit": bool(squad),
            "_tribe_explicit": bool(tribe),
            "clean_query": clean_query,
        }

    def _default_function(self, domain: str) -> str:
        """Get default function for a domain (from org/functions.yaml)."""
        return self._index.default_function(domain)

    def _infer_domain_from_functions(self, functions: list[str]) -> list[str] | None:
        """Infer domain from function candidates when domain detection failed.

        Counts which category appears most across all function candidates.
        Returns sorted domain list or None if no candidates.
        """
        from collections import Counter
        cat_counter: Counter = Counter()
        for func in functions:
            candidates = self._index.by_function(func)
            for c in candidates:
                cat_counter[c.category] += 1
        if not cat_counter:
            return None
        # Exclude developers — it was already the default we're trying to override
        non_dev = {k: v for k, v in cat_counter.items() if k != "developers"}
        if non_dev:
            return sorted(non_dev, key=non_dev.get, reverse=True)
        return None

    def select_personas(self, analysis: dict) -> list[PersonaEntry]:
        """Select optimal personas based on analysis.

        If tribe/squad is specified, constrain selection to that pool.
        For auto-detected tribe, only constrain if function candidates exist in pool.
        Otherwise, use function-priority-based selection (existing logic).
        """
        squad_id = analysis.get("squad", "")
        tribe_id = analysis.get("tribe", "")

        # Squad-constrained selection (always respected — squad is specific)
        if squad_id:
            pool = self._index.by_squad(squad_id)
            if pool:
                return self._select_from_pool(pool, analysis)

        # Tribe-constrained selection: only when explicitly provided by user
        # Auto-detected tribe is informational metadata, not a selection constraint
        if tribe_id and analysis.get("_tribe_explicit"):
            pool = self._index.by_tribe(tribe_id)
            if pool:
                return self._select_from_pool(pool, analysis)

        # Default: function-priority-based selection
        return self._select_by_function(analysis)

    def _select_from_pool(self, pool: list[PersonaEntry], analysis: dict) -> list[PersonaEntry]:
        """Select personas from a constrained pool (tribe/squad).

        Strategy:
        1. Function-priority matches within pool
        2. Locale matches to fill remaining
        3. Any remaining pool members
        """
        selected = []
        seen_ids = set()
        locale = analysis["locale"]
        max_count = analysis["agent_count"]
        pool_ids = {p.id for p in pool}

        # Pass 1: Function-priority matches within pool (locale-preferred)
        for func in analysis["functions"]:
            if len(selected) >= max_count:
                break
            candidates = self._index.by_function(func)
            pool_cands = [c for c in candidates if c.id in pool_ids and c.id not in seen_ids]
            if not pool_cands:
                continue
            # Prefer locale match within pool ("global" matches any locale)
            picked = None
            for c in pool_cands:
                if c.locale == locale or c.locale == "global":
                    picked = c
                    break
            if not picked:
                picked = pool_cands[0]
            selected.append(picked)
            seen_ids.add(picked.id)

        # Pass 2: Locale-matching pool members ("global" matches any locale)
        if len(selected) < max_count:
            for p in pool:
                if p.id not in seen_ids and (p.locale == locale or p.locale == "global"):
                    selected.append(p)
                    seen_ids.add(p.id)
                    if len(selected) >= max_count:
                        break

        # Pass 3: Any remaining pool members
        if len(selected) < max_count:
            for p in pool:
                if p.id not in seen_ids:
                    selected.append(p)
                    seen_ids.add(p.id)
                    if len(selected) >= max_count:
                        break

        return selected[:max_count]

    def _select_by_function(self, analysis: dict) -> list[PersonaEntry]:
        """Original function-priority-based selection (no pool constraint).

        Strategy: pick top-1 per function first (round-robin), then fill remaining slots.
        Functions are sorted so domain-relevant ones come before cross-domain ones.
        """
        selected = []
        seen_ids = set()
        locale = analysis["locale"]
        max_count = analysis["agent_count"]
        primary_domain = analysis["domains"][0]

        # Sort functions: domain-relevant first, cross-domain second
        domain_funcs = []
        cross_funcs = []
        for func in analysis["functions"]:
            candidates = self._index.by_function(func)
            if candidates and any(c.category == primary_domain for c in candidates):
                domain_funcs.append(func)
            else:
                cross_funcs.append(func)
        ordered_funcs = domain_funcs + cross_funcs

        # Score-aware reranking (if enabled and data available)
        scorer = None
        if cfg.get("scoring_enabled", True):
            try:
                from .mas_scoring import get_scorer
                scorer = get_scorer()
            except Exception:
                scorer = None

        # Pass 1: Pick top-1 per function (best locale match, score-reranked)
        for func in ordered_funcs:
            if len(selected) >= max_count:
                break
            candidates = self._index.by_function(func)
            if not candidates:
                continue
            # Rerank by efficiency score if data available
            if scorer and scorer.has_data(func):
                candidates = scorer.rerank(candidates, func, locale)

            picked = None
            # Prefer locale match ("global" matches any locale)
            for c in candidates:
                if (c.locale == locale or c.locale == "global") and c.id not in seen_ids:
                    picked = c
                    break
            if not picked:
                for c in candidates:
                    if c.id not in seen_ids:
                        picked = c
                        break
            if picked:
                selected.append(picked)
                seen_ids.add(picked.id)

        # Pass 2: Fill remaining slots from all functions' 2nd/3rd choices
        if len(selected) < max_count:
            for func in analysis["functions"]:
                candidates = self._index.by_function(func)
                for c in candidates:
                    if c.id not in seen_ids and len(selected) < max_count:
                        selected.append(c)
                        seen_ids.add(c.id)
                if len(selected) >= max_count:
                    break

        # Pass 3: Multi-domain fill — for multi-domain queries, ensure
        # at least one persona from each detected domain if slots remain.
        if len(selected) < max_count and len(analysis["domains"]) > 1:
            represented = {p.category for p in selected}
            for domain in analysis["domains"]:
                if domain in represented or len(selected) >= max_count:
                    continue
                domain_personas = self._index.by_category(domain)
                for p in domain_personas:
                    if p.id not in seen_ids and (p.locale == locale or p.locale == "global"):
                        selected.append(p)
                        seen_ids.add(p.id)
                        represented.add(domain)
                        break
                if len(selected) >= max_count:
                    break

        # Cycle #68: Domain affinity check — when function candidates don't match the
        # explicitly detected domain, prefer domain-based selection.
        # Only applies when domain was specifically matched (not default "developers").
        if selected and primary_domain != "developers":
            has_domain_match = any(p.category == primary_domain for p in selected)
            if not has_domain_match:
                _log(f"[selection] Domain affinity override: selected={[p.id for p in selected]} "
                     f"have no {primary_domain} match, overriding with domain-based")
                domain_personas = self._index.by_category(primary_domain)
                if domain_personas:
                    locale_match = [p for p in domain_personas
                                    if p.locale == locale or p.locale == "global"]
                    pool = locale_match if locale_match else domain_personas
                    selected = pool[:max_count]

        # Fallback: if no function-based selection, use domain + locale
        if not selected:
            domain = analysis["domains"][0]
            _log(f"[selection] Fallback to domain+locale: domain={domain}, locale={locale}")
            domain_personas = self._index.by_category(domain)
            locale_match = [p for p in domain_personas if p.locale == locale or p.locale == "global"]
            pool = locale_match if locale_match else domain_personas
            selected = pool[:max_count]

        return selected[:max_count]

    def execute(
        self,
        request_id: str,
        query: str,
        persona_ids: list[str] = None,
        pattern: str = None,
        tribe: str = None,
        squad: str = None,
        max_personas: int = None,
    ):
        """Full orchestration: analyze → select → spawn → synthesize.

        This runs synchronously (called from a background thread).
        """
        # [0] Routine check — intercept before expensive pipeline
        if not persona_ids:
            try:
                from .mas_routines import try_routine
                routine_result = try_routine(request_id, query)
                if routine_result is not None:
                    if routine_result.get("error"):
                        state.update_request(request_id, status="failed",
                                             error=routine_result["error"])
                    else:
                        state.update_request(request_id, status="completed",
                                             synthesis=routine_result["output"],
                                             pattern="routine",
                                             total_tokens_used=routine_result.get("tokens", 0),
                                             total_cost_usd=routine_result.get("cost_usd", 0))
                    self._slack_notify_complete(request_id)
                    state.record_event("complete", f"Request {request_id} completed (routine: {routine_result.get('routine_id', '?')})", request_id)
                    return
            except Exception as e:
                _log(f"[{request_id}] Routine check failed: {e}, continuing with pipeline")

        # 1. Analyze
        state.update_request(request_id, status="analyzing")
        analysis = self.analyze_request(query, pattern=pattern, tribe=tribe, squad=squad)

        # Record tribe/squad in state
        if analysis.get("tribe"):
            state.update_request(request_id, tribe=analysis["tribe"])
        if analysis.get("squad"):
            state.update_request(request_id, squad=analysis["squad"])
        # Apply max_personas cap (user-requested limit)
        if max_personas and isinstance(max_personas, int) and max_personas > 0:
            analysis["agent_count"] = min(analysis["agent_count"], max_personas)
            _log(f"[{request_id}] max_personas={max_personas} → agent_count capped to {analysis['agent_count']}")

        _log(f"[{request_id}] Analysis: {analysis}")

        # 2. Select personas
        state.update_request(request_id, status="assembling",
                             domain=analysis["domains"][0],
                             locale=analysis["locale"])

        if persona_ids:
            # Forced persona selection
            personas = [self._index.get(pid) for pid in persona_ids]
            personas = [p for p in personas if p is not None]
            if not personas:
                _log(f"[{request_id}] Forced persona_ids {persona_ids} all invalid, falling back to auto-select")
                personas = self.select_personas(analysis)
        else:
            personas = self.select_personas(analysis)

        if not personas:
            # Diagnostic: log index state to help debug transient empty selection
            idx_count = self._index.count()
            funcs = analysis.get("functions", [])
            func_results = {f: len(self._index.by_function(f)) for f in funcs[:3]}
            domain = analysis["domains"][0]
            cat_count = len(self._index.by_category(domain))
            _log(f"[{request_id}] No personas found — index={idx_count}, "
                 f"by_function={func_results}, by_category({domain})={cat_count}, "
                 f"analysis={analysis}")
            state.update_request(request_id, status="failed",
                                 error="no suitable personas found")
            return

        persona_id_list = [p.id for p in personas]
        state.update_request(request_id, selected_personas=persona_id_list)

        _log(f"[{request_id}] Selected: {[p.callsign for p in personas]}")

        # 3. Notify Slack (if enabled)
        self._slack_notify_assembly(request_id, query, personas, analysis)

        # 4. Determine pattern
        if pattern:
            conv_pattern = pattern
        else:
            conv_pattern = determine_pattern(analysis, personas)

        state.update_request(request_id, pattern=conv_pattern)
        _log(f"[{request_id}] Pattern: {conv_pattern}")

        # 5. Execute pattern (use cleaned query for agent prompts, AMM, synthesis)
        state.update_request(request_id, status="running")
        agent_query = analysis.get("clean_query", query)
        result = execute_pattern(
            request_id=request_id,
            query=agent_query,
            personas=personas,
            pattern=conv_pattern,
            index=self._index,
        )

        # 6. Update state with result
        if result.get("error"):
            state.update_request(request_id, status="failed",
                                 error=result["error"])
            _log(f"[{request_id}] Failed: {result['error']}")
        else:
            synthesis = result.get("synthesis", "")

            # 6a. Insight capture — extract [INSIGHT] blocks, save to library, strip from output
            try:
                from .mas_insight_capture import process_synthesis, extract_insights, save_insights
                primary_domain = analysis["domains"][0]

                # Capture insights from individual agent outputs (multi-agent)
                agent_outputs = result.get("agent_outputs", [])
                for i, ao in enumerate(agent_outputs):
                    ao_text = ao.get("text", "")
                    if not ao_text or "[INSIGHT]" not in ao_text:
                        continue
                    ao_callsign = personas[i].callsign if i < len(personas) else "unknown"
                    ao_insights = extract_insights(ao_text)
                    if ao_insights:
                        from .mas_insight_capture import _CATEGORY_DOMAIN_MAP
                        lib_domain = _CATEGORY_DOMAIN_MAP.get(primary_domain, primary_domain)
                        saved = save_insights(lib_domain, ao_insights,
                                              request_id=request_id,
                                              source_agent=ao_callsign)
                        if saved:
                            _log(f"[{request_id}] Agent insight: {ao_callsign} → {saved} insight(s)")

                # Capture insights from synthesis output + strip
                agent_names = ", ".join(p.callsign for p in personas)
                synthesis = process_synthesis(
                    synthesis,
                    domain=primary_domain,
                    request_id=request_id,
                    source_agent=agent_names,
                )
            except Exception as e:
                _log(f"[{request_id}] Insight capture failed: {e}")

            state.update_request(request_id,
                                 status="completed",
                                 synthesis=synthesis)
            _log(f"[{request_id}] Completed ({len(synthesis)} chars)")

        # 7. Slack final update
        self._slack_notify_complete(request_id)

        state.record_event("complete" if not result.get("error") else "error",
                           f"Request {request_id} {state.get_request(request_id).status}",
                           request_id)

        # 8. Performance ledger — record per-agent outcomes for scoring
        try:
            from .mas_performance import record_outcome
            record_outcome(request_id, analysis)
        except Exception as e:
            _log(f"[{request_id}] Performance recording failed: {e}")

    def _slack_notify_assembly(self, request_id, query, personas, analysis):
        """Send Slack notification about team assembly."""
        if not cfg.get_nested("slack", "enabled", False):
            return
        try:
            from .mas_slack import notify_assembly
            notify_assembly(request_id, query, personas, analysis)
        except Exception as e:
            _log(f"Slack assembly notify failed: {e}")

    def _slack_notify_complete(self, request_id):
        """Send Slack notification about completion."""
        if not cfg.get_nested("slack", "enabled", False):
            return
        try:
            from .mas_slack import notify_complete
            notify_complete(request_id)
        except Exception as e:
            _log(f"Slack complete notify failed: {e}")
