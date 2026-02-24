"""MAS Persona Scoring — aggregate performance ledger into per-persona efficiency scores.

Reads JSONL performance records and provides:
- Per-persona efficiency scores (success_rate * quality_proxy / cost_factor)
- Per-function score breakdown
- Reranking for score-aware persona selection
"""

import statistics
import threading
import time
from dataclasses import dataclass, field

from . import mas_config as cfg
from .mas_performance import load_records
from .mas_persona_index import PersonaEntry


@dataclass
class FunctionScore:
    function: str
    total_requests: int = 0
    success_count: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: int = 0
    total_output_length: int = 0
    success_rate: float = 0.0
    avg_cost_usd: float = 0.0
    avg_duration_ms: int = 0
    efficiency_score: float = 0.0


@dataclass
class PersonaScore:
    persona_id: str
    total_requests: int = 0
    success_count: int = 0
    success_rate: float = 0.0
    avg_cost_usd: float = 0.0
    avg_duration_ms: int = 0
    avg_output_length: int = 0
    efficiency_score: float = 0.0
    by_function: dict[str, FunctionScore] = field(default_factory=dict)


class Scorer:
    def __init__(self):
        self._lock = threading.Lock()
        self._scores: dict[str, PersonaScore] = {}
        self._global_avg_cost: float = 0.0
        self._last_computed: float = 0.0

    def _ensure_computed(self):
        ttl = cfg.get("scoring_cache_ttl", 300)
        if time.time() - self._last_computed < ttl and self._scores:
            return
        with self._lock:
            if time.time() - self._last_computed < ttl and self._scores:
                return
            self._compute()

    def _compute(self):
        lookback = cfg.get("scoring_lookback_days", 7)
        records = load_records(lookback)
        if not records:
            self._scores = {}
            self._global_avg_cost = 0.0
            self._last_computed = time.time()
            return

        # Aggregate per-persona
        persona_data: dict[str, list[dict]] = {}
        all_costs = []
        for rec in records:
            pid = rec.get("persona_id", "")
            if not pid:
                continue
            persona_data.setdefault(pid, []).append(rec)
            cost = rec.get("cost_usd", 0)
            if cost > 0:
                all_costs.append(cost)

        median_cost = statistics.median(all_costs) if all_costs else 0.01
        self._global_avg_cost = statistics.mean(all_costs) if all_costs else 0.0

        scores = {}
        for pid, recs in persona_data.items():
            ps = PersonaScore(persona_id=pid)
            ps.total_requests = len(recs)
            ps.success_count = sum(1 for r in recs if r.get("status") == "completed")
            ps.success_rate = ps.success_count / ps.total_requests if ps.total_requests > 0 else 0

            costs = [r.get("cost_usd", 0) for r in recs]
            durations = [r.get("duration_ms", 0) for r in recs]
            output_lens = [r.get("output_length", 0) for r in recs]

            ps.avg_cost_usd = statistics.mean(costs) if costs else 0
            ps.avg_duration_ms = int(statistics.mean(durations)) if durations else 0
            ps.avg_output_length = int(statistics.mean(output_lens)) if output_lens else 0

            # Composite efficiency score
            quality_proxy = min(ps.avg_output_length / 1000, 3.0) / 3.0
            cost_factor = max(ps.avg_cost_usd / median_cost, 0.5) if median_cost > 0 else 1.0
            ps.efficiency_score = ps.success_rate * quality_proxy * (1.0 / cost_factor)

            # Per-function breakdown
            func_data: dict[str, list[dict]] = {}
            for r in recs:
                func = r.get("function", "")
                if func:
                    func_data.setdefault(func, []).append(r)

            for func, frecs in func_data.items():
                fs = FunctionScore(function=func)
                fs.total_requests = len(frecs)
                fs.success_count = sum(1 for r in frecs if r.get("status") == "completed")
                fs.success_rate = fs.success_count / fs.total_requests if fs.total_requests > 0 else 0
                fs.total_cost_usd = sum(r.get("cost_usd", 0) for r in frecs)
                fs.total_duration_ms = sum(r.get("duration_ms", 0) for r in frecs)
                fs.total_output_length = sum(r.get("output_length", 0) for r in frecs)
                fs.avg_cost_usd = fs.total_cost_usd / fs.total_requests
                fs.avg_duration_ms = int(fs.total_duration_ms / fs.total_requests)
                fq = min((fs.total_output_length / fs.total_requests) / 1000, 3.0) / 3.0
                fc = max(fs.avg_cost_usd / median_cost, 0.5) if median_cost > 0 else 1.0
                fs.efficiency_score = fs.success_rate * fq * (1.0 / fc)
                ps.by_function[func] = fs

            scores[pid] = ps

        self._scores = scores
        self._last_computed = time.time()

    def get_all_scores(self) -> dict[str, PersonaScore]:
        self._ensure_computed()
        return dict(self._scores)

    def get_score(self, persona_id: str) -> PersonaScore | None:
        self._ensure_computed()
        return self._scores.get(persona_id)

    def get_function_score(self, persona_id: str, function: str) -> FunctionScore | None:
        ps = self.get_score(persona_id)
        if not ps:
            return None
        return ps.by_function.get(function)

    def has_data(self, function: str) -> bool:
        """Check if we have enough scoring data for a function."""
        self._ensure_computed()
        min_samples = cfg.get("scoring_min_samples", 3)
        for ps in self._scores.values():
            fs = ps.by_function.get(function)
            if fs and fs.total_requests >= min_samples:
                return True
        return False

    def global_avg_cost_per_agent(self) -> float:
        self._ensure_computed()
        return self._global_avg_cost

    def rerank(self, candidates: list[PersonaEntry], function: str, locale: str) -> list[PersonaEntry]:
        """Rerank candidates by efficiency score for a specific function.

        Personas with sufficient data are sorted by efficiency_score desc.
        Personas without data keep their original position.

        Epsilon-greedy exploration: with configurable probability (default 10%),
        skip reranking and return original priority order. This prevents
        positive feedback loops where high-volume personas dominate scoring.
        """
        import random

        # Epsilon-greedy: sometimes skip reranking to explore alternatives
        epsilon = cfg.get("scoring_explore_rate", 0.1)
        if random.random() < epsilon:
            return candidates

        self._ensure_computed()
        min_samples = cfg.get("scoring_min_samples", 3)

        scored = []
        unscored = []
        for i, c in enumerate(candidates):
            fs = self.get_function_score(c.id, function)
            if fs and fs.total_requests >= min_samples:
                scored.append((c, fs.efficiency_score, i))
            else:
                unscored.append((c, i))

        scored.sort(key=lambda x: (-x[1], x[2]))
        return [c for c, _, _ in scored] + [c for c, _ in unscored]

    def function_ranking(self, function: str) -> list[dict]:
        """Get personas ranked by score for a function."""
        self._ensure_computed()
        results = []
        for pid, ps in self._scores.items():
            fs = ps.by_function.get(function)
            if fs:
                results.append({
                    "persona_id": pid,
                    "total_requests": fs.total_requests,
                    "success_rate": round(fs.success_rate, 3),
                    "avg_cost_usd": round(fs.avg_cost_usd, 4),
                    "efficiency_score": round(fs.efficiency_score, 4),
                })
        results.sort(key=lambda x: -x["efficiency_score"])
        return results


# Singleton
_scorer: Scorer | None = None
_scorer_lock = threading.Lock()


def get_scorer() -> Scorer:
    global _scorer
    if _scorer is None:
        with _scorer_lock:
            if _scorer is None:
                _scorer = Scorer()
    return _scorer
