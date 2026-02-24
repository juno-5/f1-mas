# Auto × MAS — Cumulative Summary

## System Status (as of Cycle #35, 2026-02-24)
- **MAS**: healthy, 204 personas, 205+ requests
- **Cost**: ~$30 total, $0.144/request avg (but outliers up to $0.30/request)
- **Persona utilization**: scored personas present, scoring system active
- **Insight capture**: Active, fully verified — single + multi-agent. 6 insights captured (developers: 3, marketers: 3). Agent-level + synthesis-level capture. Source attribution with callsign.
- **Library injection**: 3000 chars per agent (configurable, reduced from 6000)
- **AMM**: conditional (keyword gating) + circuit breaker + async in parallel mode
- **NAS**: circuit breaker + 2s timeout

## Key Fixes Applied

### Domain Detection (`org/domains.yaml`)
1. **Sales false positive** (Cycle #11): `리드.*관리` → `리드.{0,4}관리` — prevents "하이브리드...상태관리" matching sales
2. **UI/UX/CS bare pattern** (Cycle #18): `UI|UX` → `\bUI\b|\bUX\b`, `CX|CS` → `\bCX\b|\bCS\b` — prevents Redux/Linux/CSS substring matching
3. **Frontend keywords** (Cycle #20): Added CSS/React/Vue/Angular/Svelte/webpack/vite/DOM/컴포넌트/렌더링 to developers — prevents CSS styling→models misroute
4. **ML model disambiguation** (Cycle #23): `모델|model` → ML context negative lookahead + developers ML keywords — prevents "모델 학습"→models(패션) misroute
5. **Creatives direction keywords** (Cycle #27): Added `크리에이티브.?디렉|creative.?direct|아트.?디렉션` — "크리에이티브 디렉션"→creatives

### Function Detection (`org/functions.yaml`)
2. **Memory leak routing** (Cycle #13): Added `메모리.{0,20}릭|memory.{0,20}leak|...` to `debugging` → routes to F1-05 (Trace)
3. **Auth routing** (Cycle #13): Added `\bOAuth\b|\bJWT\b|\bSSO\b|...` to `security_audit` → routes to F1-01 (Viper)
4. **Software testing** (Cycle #15): New `software_testing` function → routes to F1-05/F1-03/FC-04/F1-11
5. **brand_strategy CI/BI fix** (Cycle #16): `\bCI\b|\bBI\b` → context-specific `CI.{0,4}(가이드|매뉴얼|...)` — prevents CI/CD, BI dashboard false positives
6. **information_architecture IA fix** (Cycle #18): `IA` → `\bIA\b` — prevents "Pinia" substring matching
7. **Bare pattern systematic fix** (Cycle #22): DB/PM/AST/AWS → `\bABBR(?![a-zA-Z])` — prevents feedback/npm/fast/jaws substring matching

### Library Injection (`mas_insight_capture.py`, `mas_conversation.py`)
5. **Template filter bug** (Cycle #10): Removed `"| |" not in content` check that blocked 7/8 domains
6. **Cross-domain library** (Cycle #10): Removed library_context pre-fetch in parallel/relay — each agent now gets own domain library
7. **Library truncation fix** (Cycle #17): `max_refs_chars` 2000→6000 (configurable via `library_max_refs_chars`). 5/8 domains now 100% covered, rest 63-95%

### Performance Optimization
8. **AMM conditional** (Cycle #28 session): keyword gating + circuit breaker + async fetch → 5s blocking eliminated
9. **NAS circuit breaker** (Cycle #28 session): CB + 2s timeout (was 5s)
10. **Synthesis timeout** 300→60s, library 6000→3000 chars, connect timeout 10→5s

### Gateway Session Issue
11. **362K token root cause** (Cycle #29): Gateway executes tool-use for `mas-inference` agent → multi-turn sessions (web_fetch, exec, MySQL) → quadratic token accumulation. Normal: 12-25K tokens. With tools: 65K-362K tokens ($0.30/request).
12. **sessions.json accumulation**: 391 MAS sessions (13.9MB), cleanup script ineffective (checks .jsonl file age, not session age)
13. **Gateway tool-use fix** (Cycle #30): `tool_choice: "none"` in API body does NOT control OpenClaw built-in tools. **Root fix**: register `mas-inference` in f1crew.json + CLAUDE.md "No tools". Result: 378K→6K tokens (60x reduction), $0.38→$0.007 (53x cost reduction). Deployed 2026-02-24 11:55 UTC.
14. **stale main sessions**: 509 sessions (17MB) in `main` agent, ~55 are MAS sessions with tool-use. Need cleanup.

### Persona Selection (`mas_orchestrator.py`)
15. **YAML path mismatch** (Cycle #32): MAS reads from `~/projects/` (via persona_registry_path config) instead of `~/.f1crew/scripts/` deploy path. functions.yaml 24KB vs 20KB, domains.yaml 9.4KB vs 8.6KB. Synced both paths.
16. **Multi-domain fill** (Cycle #33): Added Pass 3 to `_select_by_function()` — ensures at least 1 persona per detected domain for multi-domain queries. D2C query: 1 persona → 5 personas (4 domains). Pattern: single → full_team.
17. **Debug logging** (Cycle #33): Added logging for domain affinity override and fallback paths in `_select_by_function()`.

### Insight Capture (`mas_insight_capture.py`, `mas_templates.py`)
18. **YAML hot-reload race condition** (Cycle #34): Atomic swap pattern for 4 YAML loaders — prevents threads reading None during reload.
19. **Insight template injection** (Cycle #35): Added `[INSIGHT]` instruction block to all 9 domain templates in `mas_templates.py`. Previously only in SYNTHESIS template (multi-agent only).
20. **Insight field parser** (Cycle #35): `_FIELD_RE` regex fix — `:\s*\**\s*(.*)` consumes `**` after colon. Multi-line parser with field-by-field accumulation for Insight values spanning multiple lines.
21. **Multi-agent insight capture** (Cycle #37): Individual agent outputs now scanned for [INSIGHT] blocks before synthesis. Previously only synthesis output was checked → multi-agent insights were lost. Agent callsign used as Source attribution via `personas[i].callsign` index matching.

### Config Path Clarification (Cycle #35)
- MAS running config: `~/.f1crew/shared/mas-config.json` (loaded by `mas_config.py` via `F1CREW_ROOT`)
- `~/.f1crew/scripts/mas/config/mas-config.json` and `~/projects/.../config/mas-config.json` are NOT used at runtime
- `library_base_dir` in running config: `/home/mayacrew/.f1crew/shared/library`

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
- Bare 2-3 char patterns (UI, UX, CS, IA, DB, PM, AST, AWS) MUST have `\b` boundaries — match as substrings in "Redux", "Linux", "CSS", "Pinia", "feedback", "npm", "fast", "jaws"
- Best pattern for abbreviations: `\bABBR(?![a-zA-Z])` — word boundary at start, negative lookahead for English letters only (allows Korean particles)

### Deployment
- YAML changes auto-reload via mtime check (30s interval, no restart needed)
- MAS Python code: deploy to **both** `~/.f1crew/scripts/mas/` AND `~/projects/mayacrew-f1crew/f1-mas/mas/`
- Org YAML: deploy to **both** `~/projects/mayacrew-f1crew/f1-mas/org/` (primary, read by MAS) AND `~/.f1crew/scripts/mas/org/` (backup)
- MAS reads YAML from `~/projects/` first due to `persona_registry_path` config pointing there
- **Config**: Running config is `~/.f1crew/shared/mas-config.json` (NOT `scripts/mas/config/` or `projects/.../config/`)

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
- ~~**insights.md empty**~~: Fixed in Cycle #35 — [INSIGHT] instruction added to all 9 domain templates + field parser fixed for `**Title:**` format + multi-line support. E2E verified.
- **Project-specific libraries** (cosduck, superchart, supermembers): Not injected into agent prompts — only domain-level libraries used
- ~~**Gateway tool-use for mas-inference**~~: Fixed in Cycle #30 — registered mas-inference in f1crew.json + CLAUDE.md "No tools". 60x token reduction.
- **stale main sessions**: 509 sessions (17MB) in `main` agent, ~55 are old MAS sessions with tool-use. Need one-time cleanup.
- ~~**"스타일링" ambiguity**~~: Fixed in Cycle #20 — CSS/frontend keywords added to developers
- ~~**Tailwind AI false positive**~~: Fixed in separate session (Cycle #48) — `\bAI(?=[^a-zA-Z]|$)` pattern
- ~~**Cross-domain persona diversity** (Cycle #24)~~: Fixed in Cycle #33 — Pass 3 multi-domain fill ensures 1 persona per domain.
- **Transient Ashley Yoo bug** (Cycle #32): 12:03-12:15 window에서 모든 요청이 Ashley Yoo 선택. 코드/YAML 동일 상태에서 발생, 12:22 이후 자동 복구. 재현 불가. 가능 원인: YAML hot-reload 경합 조건 또는 파일시스템 캐시.

## Session History
- 2026-02-23 (Cycles #1-#10): Failure analysis, retry improvements, domain keywords, library fix
- 2026-02-24 (Cycles #11-#27): 17 cycles — Sales regex, function coverage (debugging/auth/testing), pattern fixes (CI/BI, UI/UX/CS/IA word boundary, frontend keywords, DB/PM/AST/AWS bare pattern, ML model disambiguation), library truncation 6000, cross-domain persona diversity analysis, insight capture audit, creatives keywords
- 2026-02-24 (Cycles #28-#29): Token anomaly investigation — 362K token root cause found (Gateway tool-use for mas-inference agent), sessions.json accumulation identified
- 2026-02-24 (Cycle #30): Gateway tool-use fix verified — mas-inference registered in f1crew.json, 60x token reduction confirmed. Local config synced.
- 2026-02-24 (Cycles #31-#33): Stale session analysis (509 orphans), persona selection quality audit (transient Ashley Yoo bug), YAML path mismatch fix, multi-domain fill (Pass 3), debug logging added.
- 2026-02-24 (Cycle #34): YAML hot-reload race condition fix — atomic swap pattern for 4 loaders.
- 2026-02-24 (Cycle #35): Insight capture E2E fix — template injection (9 domains) + field parser (`**Title:**` + multi-line) + config path clarification. Verified with live request.
- 2026-02-24 (Cycles #36-#37): Source attribution (callsign), multi-agent insight capture gap fixed. Agent-level insights now captured alongside synthesis. Verified: 6 insights across 2 domains.
