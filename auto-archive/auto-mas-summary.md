# Auto × MAS — Cumulative Summary

## System Status (as of Cycle #21, 2026-02-24)
- **MAS**: healthy, 204 personas, 201 requests (161 completed, 36 failed)
- **Cost**: $28.90 total, $0.144/request avg
- **Persona utilization**: 34/204 scored (17%)
- **Scoring system**: Active, 34 personas with performance data, 161 records
- **Insight capture**: Active, 4 insights accumulated (developers domain)
- **Library injection**: 6000+ chars per agent (configurable)

## Key Fixes Applied

### Domain Detection (`org/domains.yaml`)
1. **Sales false positive** (Cycle #11): `리드.*관리` → `리드.{0,4}관리` — prevents "하이브리드...상태관리" matching sales
2. **UI/UX/CS bare pattern** (Cycle #18): `UI|UX` → `\bUI\b|\bUX\b`, `CX|CS` → `\bCX\b|\bCS\b` — prevents Redux/Linux/CSS substring matching
3. **Frontend keywords** (Cycle #20): Added CSS/React/Vue/Angular/Svelte/webpack/vite/DOM/컴포넌트/렌더링 to developers — prevents CSS styling→models misroute

### Function Detection (`org/functions.yaml`)
2. **Memory leak routing** (Cycle #13): Added `메모리.{0,20}릭|memory.{0,20}leak|...` to `debugging` → routes to F1-05 (Trace)
3. **Auth routing** (Cycle #13): Added `\bOAuth\b|\bJWT\b|\bSSO\b|...` to `security_audit` → routes to F1-01 (Viper)
4. **Software testing** (Cycle #15): New `software_testing` function → routes to F1-05/F1-03/FC-04/F1-11
5. **brand_strategy CI/BI fix** (Cycle #16): `\bCI\b|\bBI\b` → context-specific `CI.{0,4}(가이드|매뉴얼|...)` — prevents CI/CD, BI dashboard false positives
6. **information_architecture IA fix** (Cycle #18): `IA` → `\bIA\b` — prevents "Pinia" substring matching

### Library Injection (`mas_insight_capture.py`, `mas_conversation.py`)
5. **Template filter bug** (Cycle #10): Removed `"| |" not in content` check that blocked 7/8 domains
6. **Cross-domain library** (Cycle #10): Removed library_context pre-fetch in parallel/relay — each agent now gets own domain library
7. **Library truncation fix** (Cycle #17): `max_refs_chars` 2000→6000 (configurable via `library_max_refs_chars`). 5/8 domains now 100% covered, rest 63-95%

### Other Fixes
7. **Retry improvements** (Cycle #3): `inference_max_retries` default 3, exponential backoff
8. **Function pattern tightening** (Cycle #6): `revenue_operations` CRM/리드 patterns with lookbehind
9. **SRE monitoring patterns** (Cycle #8): 서버/노드/디스크/점검 keywords for sre_monitoring

## Failure Analysis
- **61% infrastructure** (xapi/Gateway downtime) — not MAS logic issues
- **17% agent failures** — cascade from infra
- **17% CLI exit codes** — transient
- **6% timeout/rate limit** — expected edge cases

## Patterns Learned

### Korean Regex
- `\b` word boundary fails between English abbreviations and Korean particles (TDD로, jest로)
- Use `\bABBR` (start only) or remove trailing `\b` for mixed-language patterns
- `.{0,N}` much safer than `.*` — prevents cross-sentence matching
- Bare 2-3 char patterns (UI, UX, CS, IA) MUST have `\b` boundaries — match as substrings in "Redux", "Linux", "CSS", "Pinia"

### Deployment
- YAML changes auto-reload via mtime check (30s interval, no restart needed)
- MAS Python code: deploy to `~/.f1crew/scripts/mas/` (flat, not nested)
- Org YAML: deploy to `~/projects/mayacrew-f1crew/f1-mas/org/`

### Function Detection Coverage
- 35/89 functions matched in production (39%)
- `system_architecture` hyper-dominant (51%) — includes genuine matches + default fallbacks
- Remaining gaps: Git/VCS, API design, general coding patterns (lower priority)
- `scent_sensory` has empty patterns (by design)

## Open Items
- ~~**brand_strategy `\bCI\b` false positive**~~: Fixed in Cycle #16
- **Gateway ASCII encoding**: 한소민 error originates in FAS Gateway, not MAS
- **Deduplication**: No mechanism for repeated identical queries
- **Low-traffic domains**: cx (1%), creatives (1%) have minimal function scoring data
- **xapi instability**: Frequent stop-sigterm states (observed in Cycles #15, #16)
- **insights.md empty**: All 8 domains have 0 insights — [INSIGHT] instruction only in synthesis template (optional), not in agent prompts
- **Project-specific libraries** (cosduck, superchart, supermembers): Not injected into agent prompts — only domain-level libraries used
- ~~**"스타일링" ambiguity**~~: Fixed in Cycle #20 — CSS/frontend keywords added to developers
- **Tailwind AI false positive**: "Tailwind" matches developers AI pattern via "ai" substring

## Session History
- 2026-02-23 (Cycles #1-#10): Failure analysis, retry improvements, domain keywords, library fix
- 2026-02-24 (Cycles #11-#21): 11 cycles — Sales regex, function coverage (debugging/auth/testing), pattern fixes (CI/BI, UI/UX/CS/IA word boundary, frontend keywords), library truncation 6000, insight capture live, production health audit
