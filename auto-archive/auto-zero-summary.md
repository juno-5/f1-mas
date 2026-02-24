# Auto×Zero Summary

## 주요 발견 (Confirmed)

1. **Cycle #3 (2026-02-23)**: AMM memory fetch 호이스팅
   - multi-agent 요청에서 AMM API 호출 N→1 최적화
   - `mas_conversation.py` 수정, 커밋 `ed2a1f9`

2. **Cycle #4 (2026-02-23)**: MAS xapi 스타트업 헬스체크
   - 배포 중 19.5% 실패율 원인: xapi 미가용 상태에서 요청 수락
   - `_wait_for_xapi()` 추가 — xapi /health 폴링 후 서빙 시작
   - `mas_server.py` 수정, 커밋 `3e06acf`

3. **Cycle #6 (2026-02-23)**: MAS /requests 진단 필드 추가
   - `/requests` list에 `error`, `selected_personas`, `failed_agents` 필드 추가
   - `mas_server.py` 수정, 커밋 `8974a03`

4. **Cycle #8 (2026-02-23)**: MAS Prometheus 메트릭 강화
   - p50/p95 percentile, per-pattern breakdown, cost counter 추가
   - `mas_metrics.py` 수정, 커밋 `9f6830d`

5. **Cycle #9 (2026-02-23)**: MAS 상태 복원 버그 수정
   - save/load 비대칭: active_requests 저장은 하지만 로드 안 함
   - 재시작 시 running 요청 유실 → failed로 복원 + 카운터 증가
   - `mas_state.py` 수정, 커밋 `46be0c7`

## 기각된 가설 (Rejected/Partial)

1. **Cycle #1 (2026-02-23)**: xapi 0.0.0.0 바인딩 → 127.0.0.1 변경으로 보안 강화
   - 판정: Partial — API 키 인증 이미 활성화. Tailscale 접근 때문에 0.0.0.0 필요. 방화벽 규칙이 더 적합.

## 변경 이력

1. `mas/mas_conversation.py` — AMM fetch 호이스팅 (ed2a1f9, 2026-02-23)
2. `mas/mas_server.py` — xapi 스타트업 헬스체크 + tribe/squad API (3e06acf, 2026-02-23)
3. `mas/mas_server.py` — /requests 진단 필드 추가 (8974a03, 2026-02-23)
4. `mas/mas_metrics.py` — p50/p95 percentile + per-pattern 메트릭 (9f6830d, 2026-02-23)
5. `mas/mas_state.py` — interrupted request 복원 버그 수정 (46be0c7, 2026-02-23)
6. `mas/mas_agent_runner.py` — 502/503 재시도 추가 (f78a119, 2026-02-23)

6. **Cycle #11 (2026-02-23)**: xapi 502/503 재시도 추가
   - synthesis/batch에서 "Server disconnected" 502 에러 시 즉시 실패 반환
   - 502/503 응답에 5초 대기 후 1회 재시도 로직 추가
   - `mas/mas_agent_runner.py` 수정, 커밋 `f78a119`
   - **배포 완료** (Cycle #12에서)

7. **Cycle #12 (2026-02-23)**: MAS ↔ FAS 전체 연결 체인 검증
   - MAS→xapi→Gateway→Token Manager→Claude API 전 구간 정상 확인
   - Gateway→NAS: nasUrl+nasApiKey 설정됨, callNas()가 X-API-Key 헤더 전송 확인
   - MAS→NAS: /nodes, /docs/search (인증 불필요) 정상
   - NAS exec API key 인증 동작 확인 (578ms)
   - Cycle #11 502/503 retry 서버 배포 완료

8. **Cycle #13 (2026-02-23)**: Synthesis output cap + input truncation
   - `call_xapi_inference()`: max_tokens 파라미터 추가
   - `run_synthesis()`: `synthesis_max_tokens` config (default 2048)
   - `build_synthesis_prompt()`: `synthesis_max_input_chars` config (default 4000) truncation
   - `mas_agent_runner.py`, `mas_templates.py`, `mas_conversation.py` 수정, 커밋 `2a8737c`

9. **Cycle #14 (2026-02-23)**: mas_performance.py 배포 누락 수정
   - `mas_performance.py`, `mas_scoring.py` 서버 배포
   - 모든 요청 완료 시 performance JSONL 기록 시작
   - persona scoring 기반 데이터 수집 활성화

10. **Cycle #15 (2026-02-23)**: xapi TimeoutStopSec 15→60
    - xapi restart 시 `Failed with result 'timeout'` — 15s timeout으로 inference 요청 강제 종료
    - `TimeoutStopSec=60`으로 변경, 서버 배포 + daemon-reload
    - `xapi/systemd/xapi.service` 수정, 커밋 `425eae9`

11. **Cycle #18 (2026-02-23)**: **Gateway 세션 누적 해소 + 캐시 추적** ⭐
    - user 필드 `mas:{callsign}` → `mas:{request_id}:{callsign}` — 요청별 독립 세션
    - **Before: 360K tokens/$0.647/55s → After: 34K tokens/$0.019/14s** (90%+ 절감)
    - OpenAI format prompt_tokens_details cache 추적 추가
    - `mas/mas_agent_runner.py` 수정, 커밋 `678899c`

12. **Cycle #22 (2026-02-23)**: MAS 스타트업 전체 체인 검증 강화
    - `_wait_for_xapi()`: `/health` → `/inference/capacity` (`ready`, `gateway_healthy`, `tokens_available_pct`)
    - `mas/mas_server.py` 수정, 커밋 `d594e25`

13. **Cycle #26 (2026-02-23)**: 페르소나 선택 정확도 개선 ⭐
    - `frontend_ui` priority: F1-02(아키텍트) → F1-03(프론트엔드) 교체
    - `system_architecture` 패턴: 단독 "설계" 제거 (오탐 방지)
    - **Before**: "React 상태관리" → Forge, "UX 리서치" → Forge
    - **After**: "React 상태관리" → Blaze, "UX 리서치" → Palette
    - `org/functions.yaml` + `mas/mas_persona_index.py` 수정, 커밋 `8394197`

15. **Cycle #29 (2026-02-23)**: tokens_used 이중 계산 버그 수정 ⭐
    - `sum(usage.values())` → `usage.get("input", 0) + usage.get("output", 0)`
    - cacheRead는 input의 subset — sum()이 이중 계산하고 있었음
    - **Before: 28,359 tokens → After: 14,217 tokens (-50%)**
    - `mas/mas_agent_runner.py` 4곳 수정, 커밋 `2a463cf`

16. **Cycle #31 (2026-02-23)**: 강제 persona_ids 실패 시 auto-select fallback ⭐
    - Gateway agent가 잘못된 persona ID 전달 시 "no suitable personas found" 즉시 실패
    - fallback: 잘못된 ID 전부 필터 → 자동 선택 로직으로 재시도
    - 진단 로깅 추가: 실패 경로에서 analysis 정보 출력
    - `mas/mas_orchestrator.py` 수정, 커밋 `d274b6a`

14. **Cycle #27 (2026-02-23)**: **Gateway 시스템 프롬프트 오버헤드 감소** ⭐
    - xapi가 MAS 요청 시 `X-OpenClaw-Session-Key: subagent:mas:{user}` 자동 주입
    - Gateway "full" → "minimal" prompt mode: **15,904 → 10,480 tokens (-34%)**
    - 비-MAS 요청은 영향 없음 (full mode 유지)
    - E2E 단일 에이전트: 33,956 → 29,637 tokens (-13%)
    - `xapi/xapi/routers/inference.py` 수정

17. **Cycle #33 (2026-02-23)**: **비ASCII 페르소나 callsign 인코딩 에러 수정** ⭐
    - `user` 태그에 한국어/일본어 callsign 포함 → HTTP 헤더 ASCII 인코딩 실패 (502)
    - 30개 모델 페르소나(한국 20 + 일본 10) 전원 영향
    - `user_tag`에 callsign 대신 persona_id(항상 ASCII) 사용
    - xapi에 ASCII 인코딩 safety net 추가
    - **Before: 100% 실패 → After: 정상 완료** (윤소라 KF01 테스트 검증)
    - `mas/mas_agent_runner.py` 3곳 수정 커밋 `b123eb7` + `xapi/routers/inference.py` 커밋 `eaf9c2a`

18. **Cycle #35 (2026-02-23)**: **Tool injection regex false positive 수정** ⭐
    - 85.7% false positive rate (6/7 요청): `PC`→gRPC 내부 매칭, `실행`→실행 계획, `서비스`→마이크로서비스
    - NAS: `\bPC\b` word boundary, 실행→compound, 배포 제거
    - INFRA: 서비스→compound, `(?<!블)로그`, 배포→compound, 모니터→모니터링
    - **Before: 비인프라 요청에 4~8 tools 오주입 → ThreadPool 강제**
    - **After: No tools → batch inference 사용** (4 agents in 51.8s, 진정한 병렬)
    - `mas/mas_tools.py` 수정, 커밋 `2d0c734`
    - ⚠️ 배포 경로 발견: `~/.f1crew/scripts/mas/` (실행) ≠ `~/f1-mas/mas/` (소스 복사)

19. **Cycle #36 (2026-02-23)**: xapi inference semaphore 4→6
    - 5-agent batch가 semaphore=4에서 1 agent 직렬화됨
    - 6으로 증가: 5-agent batch + 1 concurrent 요청 동시 처리 가능
    - `xapi/routers/inference.py` 수정, 커밋 `47cffae`

20. **Cycle #37 (2026-02-23)**: **Character file extraction 활성화** ⭐
    - `extract_character_sections()` 존재하나 config 미설정 → 전체 캐릭터 파일 주입
    - `character_extract_sections` + `character_extract_max_chars` 설정으로 핵심 섹션만 추출
    - **Forge: 36,203→5,572 chars, 입력 토큰 30,912→15,956 (-48.4%), 비용 $0.158→$0.082 (-48.3%)**
    - **Flux: 25,068→6,953 chars, 입력 토큰 27,890→17,170 (-38.4%), 비용 $0.146→$0.068 (-53.3%)**
    - 추가 효과: 캐시 히트율 증가 (10K→16K cached tokens) — 짧은 캐릭터로 prefix 공유 향상
    - 74% 페르소나(219/295)에 적용 → 시스템 전체 비용 ~30% 절감 추정
    - `config/mas-config.json` 수정 (코드 변경 없음, config만)

21. **Cycle #38 (2026-02-23)**: **Output token 잘림 수정 (agent_max_tokens)** ⭐
    - MAS max_tokens=4096 하드코딩 → Gateway가 5,120 output token에서 응답 강제 종료
    - 3곳 모두 `cfg.get("agent_max_tokens", 8192)`로 통일
    - **Before: Forge out=5,120 tokens (잘림) → After: Blaze out=7,495 tokens (자연 완료)**
    - `mas/mas_agent_runner.py` 3곳 수정, 커밋 `450e1ff`

22. **Cycle #39 (2026-02-23)**: **Tool injection compound 패턴 강화 (2차)** ⭐
    - "서버 컴포넌트", "에러 바운더리" 등 개발 용어가 infra 도구 오주입 유발
    - 단독 키워드(서버, 에러, 토큰, 로그, 노드, 파일 등)를 모두 compound 패턴으로 변경
    - NAS 패턴도 동시 수정: 노드→NAS+노드, 파일→문서검색만, PC→+접속/연결
    - **Before: "서버 컴포넌트" → 4 tools → ThreadPool → After: 0 tools → batch**
    - `mas/mas_tools.py` 수정, 커밋 `64e75ce`

23. **Cycle #40 (2026-02-23)**: **Function detection regex distance bound** ⭐
    - `.*` (무제한) greedy 매칭 → "서버 컴포넌트...상태관리"가 `sre_monitoring` 오탐
    - "하이브리드...상태관리"가 `revenue_operations` 오탐 (리드.*관리 cross-match)
    - 전체 `.*` → `.{0,20}` 거리 제한 + "리드" Korean lookbehind
    - **Before: React 쿼리 → 5 agents/$0.59 → After: 2 agents/$0.30 (-49% 비용)**
    - `org/functions.yaml` 수정, 커밋 `52b951f`

24. **Cycle #41 (2026-02-24)**: **Hot reload empty index guard** ⭐
    - `load()` clears ALL index dicts before repopulating — if entries=[] (partial file during SCP), index becomes empty for ~30s
    - 동시 요청 2개 중 1개만 실패 (race condition evidence at 11:15:18)
    - `load()`: entries 빈 경우 기존 인덱스 유지 + `_load_functions_yaml()`: 빈 patterns 캐시 안 함
    - **Before: 3/51 requests "no suitable personas found" → After: guard prevents all transient failures**
    - `mas/mas_persona_index.py` 수정, 커밋 `b12b3c7`

25. **Cycle #42 (2026-02-24)**: **Haiku synthesis model — 75.8% synthesis cost reduction** ⭐
    - Synthesis uses sonnet ($0.075 avg) for structured summarization — over-provisioned
    - `synthesis_model: "haiku"` — same quality (all sections, tables, formatting preserved)
    - **Before: $0.075/synthesis (sonnet) → After: $0.018/synthesis (haiku) — 75.8% reduction**
    - Config-only change, no code modification
    - 부수 발견: MAS runtime config path = `~/.f1crew/shared/mas-config.json` ≠ source `config/mas-config.json`

26. **Cycle #43 (2026-02-24)**: **Metadata prefix stripping for detection accuracy** ⭐
    - `[auto-debug]` prefix in query caused `debugging` false positive → wrong persona (Trace instead of Apex)
    - `_METADATA_PREFIX_RE` strips `[auto-*] Cycle #N:` before domain/function/locale detection
    - `query_len` now uses cleaned query for complexity estimation
    - **Before: functions=`['debugging', 'payment_checkout', 'mobile_ux']` → Touch + Trace (wrong)**
    - **After: functions=`['payment_checkout', 'mobile_ux']` → Touch + Apex (correct)**
    - `mas/mas_orchestrator.py` 수정

27. **Cycle #44 (2026-02-24)**: **Global locale matching for Five Senses personas** ⭐
    - Five Senses (01-05, locale=global) systematically deprioritized: "global" ≠ "korea" in locale matching
    - Added `or c.locale == "global"` to all 4 locale-matching locations
    - **Before: creative query → Yena Jang + Resonance (marketer + developer)**
    - **After: creative query → CHROMA + ECHO + Yena Jang (color + sound + design)**
    - `mas/mas_orchestrator.py` 수정

28. **Cycle #45 (2026-02-24)**: **Library injection domain verification for Five Senses**
    - Five Senses 선택 후 `library/creatives/` 올바르게 주입 확인 (읽기 전용 검증)
    - `_build_agent_prompt()` → `persona.category` 기반 라이브러리 선택 — 설계 올바름
    - 부수 발견: creatives library(2748 chars) — 다른 도메인(6050+ chars) 절반 미만

29. **Cycle #46 (2026-02-24)**: **Clean query propagation to execution pipeline** ⭐
    - Cycle #43의 메타데이터 접두사 strip이 분석에만 적용, 실행 파이프라인에는 raw query 전달
    - `analyze_request()` → `clean_query` 반환 → `execute_pattern(query=agent_query)`
    - **Before AMM**: `[auto-debug] Cycle #28: React Native 앱에서 FlatList...`
    - **After AMM**: `React Native 앱에서 FlatList 성능 최적화 방법 알려줘`
    - `mas/mas_orchestrator.py` 수정 (+3 lines)

30. **Cycle #47 (2026-02-24)**: **Performance function regex disambiguation** ⭐
    - Standalone `performance` matched non-technical contexts (brand, campaign, sales)
    - Replaced with compound patterns requiring technical context words
    - Korean `성능` kept standalone (unambiguous)
    - **Before: "brand strategy...performance" → `['performance', 'brand_strategy']` → Core + Ashley Yoo**
    - **After: → `['brand_strategy']` → Ashley Yoo only**
    - `org/functions.yaml` 수정

## 변경 이력

7. `mas/mas_agent_runner.py` + `mas/mas_templates.py` + `mas/mas_conversation.py` — synthesis cap + truncation (2a8737c, 2026-02-23)
8. `mas/mas_performance.py` + `mas/mas_scoring.py` — 서버 배포 (2026-02-23, 배포만)
9. `xapi/systemd/xapi.service` — TimeoutStopSec 15→60 (425eae9, 2026-02-23)
10. `mas/mas_agent_runner.py` — Gateway 세션 격리 + cache tracking (678899c, 2026-02-23)
11. `mas/mas_agent_runner.py` + `systemd/mas.service` — partial result recovery + TimeoutStopSec 90 (436f908, 2026-02-23)
12. `mas/mas_server.py` — MAS startup 전체 체인 검증 (d594e25, 2026-02-23)
13. `scripts/cleanup-sessions.sh` — Gateway 세션 자동 정리 cron (d4b3021, 2026-02-23)
14. `org/functions.yaml` + `mas/mas_persona_index.py` — 페르소나 선택 정확도 개선 (8394197, 2026-02-23)
15. `xapi/xapi/routers/inference.py` — MAS 요청 시 subagent session key 주입 (2026-02-23)
16. `mas/mas_agent_runner.py` — tokens_used 이중 계산 수정 (2a463cf, 2026-02-23)
17. `mas/mas_orchestrator.py` — 강제 persona_ids 실패 시 auto-select fallback (d274b6a, 2026-02-23)
18. `mas/mas_agent_runner.py` — 비ASCII callsign→persona_id + retry 개선 (b123eb7, 2026-02-23)
19. `xapi/xapi/routers/inference.py` — ASCII-safe session key header + Bedrock normalization (eaf9c2a, 2026-02-23)
20. `mas/mas_tools.py` — tool injection regex false positive 수정 (2d0c734, 2026-02-23)
21. `xapi/xapi/routers/inference.py` — inference semaphore 4→6 (47cffae, 2026-02-23)
22. `config/mas-config.json` — character extraction 활성화 (config만, 코드 변경 없음, 2026-02-23)
23. `mas/mas_agent_runner.py` — agent max_tokens 4096→8192 configurable (450e1ff, 2026-02-23)
24. `mas/mas_tools.py` — tool injection compound 패턴 강화 2차 (64e75ce, 2026-02-23)
25. `org/functions.yaml` — regex distance bound .{0,20} + 리드 lookbehind (52b951f, 2026-02-23)
26. `mas/mas_persona_index.py` — hot reload empty index guard (b12b3c7, 2026-02-24)
27. `config/mas-config.json` + runtime config — synthesis_model sonnet→haiku (2026-02-24)
28. `mas/mas_orchestrator.py` — metadata prefix stripping for detection accuracy (2026-02-24)
29. `mas/mas_orchestrator.py` — global locale matching for Five Senses personas (2026-02-24)
30. `mas/mas_orchestrator.py` — clean_query propagation to execution pipeline (2026-02-24)
31. `org/functions.yaml` — performance regex disambiguation (compound pattern, 2026-02-24)

## 미해결 가설

- ~~MAS 페르소나 선택 정확도 검증~~ → **해결** (Cycle #26: frontend_ui/system_architecture 패턴 + priority 개선)
- xapi 시맨틱 캐시 hit/miss/error 3-state 반환
- MAS→NAS 호출 시 API key 미전달 (현재 인증 불필요 endpoint만 사용하므로 문제 없으나, exec 필요시 수정 필요)
- ~~Forge 178K 토큰/$0.64 비용~~ → **해결** (Cycle #18: 세션 누적이 원인, 90%+ 절감)
- ~~Gateway 15K 토큰 시스템 프롬프트~~ → **부분 해결** (Cycle #27: subagent session key로 15.9K→10.5K 감소. 완전 해소는 `/inference/raw` + 토큰 매니저 통합 필요)
- Gateway 오래된 세션 파일 정리 (sessions/ 디렉토리 비대, sessions.json 2MB)
- ~~mas/mas/ orphan 서브디렉토리 cleanup~~ → **해결** (Cycle #24: 서버에서 삭제)
- MAS 빈번한 재시작 원인 분석 (6h/13회, 외부 deploy 트리거, daemon-reload→restart 패턴)
- ~~Gateway 재시작 시 batch 실패 — MAS startup에 Gateway 가용성 확인 필요~~ → **해결** (Cycle #22: /inference/capacity 전체 체인 검증)
- ~~Gateway 구세션 파일 정리 (109개, 5.1MB)~~ → **해결** (Cycle #23: 정리 스크립트 + 일일 cron)
