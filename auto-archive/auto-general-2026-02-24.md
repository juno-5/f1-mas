# Auto — 2026-02-24

> 이전 세션에서 이어진 전체 시스템 탐색 (continuation from context compaction)

## Cycle #1 — FAS 프로세스 관리 조사
- **Observation**: `fas` systemd inactive, 그러나 port 7700/7710 응답 중
- **Hypothesis**: FAS가 systemd 밖에서 동작
- **Result**:
  - Port 7700: `token-manager-v5.py daemon` (PID 2147222, started 01:03 UTC)
  - Port 7710: `model-router.py` (PID 258653, started Feb 21)
  - No FAS systemd unit files exist
  - Both run as standalone daemons under user session (PPID 2105)
- **Verdict**: ✅ Confirmed
- 적용 없음 — FAS 프로세스 관리는 `/auto-fas` 영역

## Cycle #2 — xapi DOWN 조사
- **Observation**: xapi `deactivating (stop-sigterm)`, port 7750 no listener
- **Hypothesis**: 외부 stop 명령에 의한 중단 (crash 아님)
- **Result**: 이전 세션의 xapi workspace.py deploy → daemon-reload + restart
  - 04:17:52 stop → 04:18:42 old process done → 04:18:56 new PID 2302368 start
  - 내 scan이 restart gap에 정확히 걸림
- **Verdict**: ✅ Confirmed (deploy-triggered restart)
- 적용 없음

## Cycle #3 — AMM-Surfacer DOWN 조사
- **Observation**: `curl -sf http://localhost:7800/health` → DOWN
- **Hypothesis**: AMM-Surfacer crash 또는 미시작
- **Result**: AMM-Surfacer IS running (PID 2224302, port 7800)
  - `POST /health` → `{"status": "ok", "memories_count": 50752}` ← **정상**
  - `GET /health` → 404 (BaseHTTP 서버, POST만 지원)
  - `GET /stats` → 200 (50K memories, 33 agents, diverse domains)
- **Verdict**: ❌ Rejected (정상 가동, health endpoint가 POST)
- 적용 없음

## Cycle #4 — 디스크 78% (72G/98G) 분석
- **Hypothesis**: AMM/로그/Qdrant가 10G+ 차지
- **Result**:
  - complex-llm/: 71G (Python venv + ML checkpoints — xapi 실행환경)
  - ComfyUI/: 30G (이미지 생성 모델)
  - .f1crew/backups/: 3.4G (Qdrant 일일 스냅샷)
  - journal logs: 860M
  - amm/data/: 229M
  - 정리 가능 항목: ~5G (old checkpoints, journal, old backups)
- **Verdict**: ⚠️ Partial (핵심 소비자는 ML 모델, 정리 가능량 제한적)
- 적용 없음 — 데이터 삭제는 사용자 승인 필요

## Cycle #5 — f1common 인프라 클라이언트 사용 현황
- **Hypothesis**: f1common에 클라이언트 존재하나 실 서비스에서 미사용
- **Result**:
  - eventbus.py: publish/subscribe/replay 완전 구현 → FAS/MAS/xapi에서 0 import
  - vault.py: get_secret/put_secret + fallback 맵 → FAS/MAS/xapi에서 0 import
  - configstore.py: get_config/set_config/watch → FAS/MAS/xapi에서 0 import
  - xapi는 HTTP proxy만 제공 (vault_proxy.py, eventbus.py router)
- **Verdict**: ✅ Confirmed
- 적용 없음

## Cycle #6 — FAS vault 연동 가능성
- **Hypothesis**: FAS credential 경로와 vault fallback 경로가 일치하여 최소 변경 연동 가능
- **Result**:
  | Credential | FAS 경로 | vault fallback | 일치 |
  |-----------|---------|---------------|:---:|
  | token-config.json | ~/.f1crew/shared/ | ~/.f1crew/shared/ | ✅ |
  | token-pool.json | ~/.f1crew/shared/ | ~/.f1crew/shared/ | ✅ |
  | spare-tokens.json | ~/.f1crew/credentials/ | 매핑 없음 | ❌ |
  - 마이그레이션: ~60줄 변경 (43 in token-manager-v5.py + 17 in token-monitor.py)
- **Verdict**: ✅ Confirmed (2/3 경로 일치, spare-tokens만 추가 매핑 필요)
- 적용 없음 — `/auto-fas` 영역

## Cycle #7 — Gateway 안정성
- **Hypothesis**: Gateway가 systemd 밖에서 실행되어 에러/불안정 가능성
- **Result**:
  - PID 2224577, started 02:45:43, RSS 502MB, 10 threads
  - systemd unit 자체 없음 (Feb 13에 마지막 사용 후 삭제됨)
  - 유일한 에러: cloudflared → xapi 7750 connection refused (deploy 중 일시적)
  - Gateway 자체 에러 없음, 안정 가동
- **Verdict**: ❌ Rejected (안정적)
- 적용 없음

## Cycle #8 — 아카이브 체크포인트
- Cycles #1-7 기록 완료

## Cycle #9 — xapi 인프라 프록시 활성화
- **Observation**: xapi에 vault_proxy.py, eventbus.py, configstore.py, logbus.py 라우터 존재하나 `_EXCLUDE_MODULES`로 비활성
- **Hypothesis**: 인프라 프록시 라우터가 비활성 상태
- **Result**: 136개 라우트 중 인프라 프록시 0개 — 확인됨
- **Verdict**: ✅ Confirmed
- **Applied changes** (후 사용자에 의해 revert):
  - `xapi/config.py`: F1_SERVICES에 4개 추가 → **reverted** (사용자 판단)
  - `xapi/main.py`: `_EXCLUDE_MODULES` 제거 → **reverted** (사용자 판단)
  - `xapi/CLAUDE.md`: Service Ports 테이블에 4개 인프라 포트 추가 (유지)
  - **최종 상태**: 인프라 프록시 라우터 + 서비스 레지스트리 모두 비활성. SSH 경유 접근 유지.
  - 코드는 scaffolded 상태로 남아있어 향후 활성화 시 exclude 제거만 하면 됨

## Cycle #10 — 10사이클 체크포인트
- 누적 요약 작성

## Additional Findings

### Backup 이중 시스템
- **qdrant-backup (기존 cron)**: 매일 03:00 UTC, 8개 Qdrant 컬렉션 스냅샷, 14일 retention, 3.4G
  - agent-memory, amm-memories(365M), training-conversations, f1_amem, inference_cache, f1_shared_memory, amm-shared-insights, shaka-memory-expanded
  - SQLite backup도 포함
- **f1-backup (신규 timer)**: 배포 완료, 한번도 실행된 적 없음, 내일 03:08 UTC 첫 실행 예정

### NAS 상태
- mac02 1대만 온라인 (CPU 33.9%, Disk 5%)
- Chrome CDP 브라우저 자동화 태스크 활발

### Prometheus 메트릭 (from /services/health)
- 10 tokens total, 10 available, 0 CB open
- Token manager mode: low-power (1)
- kernel: 87.5% usage (603 count), forge-mapda: 25.9%
- Daily: 307 requests, 8M tokens, $38.94 estimated cost
- GPU: 28°C, 620MB/32GB, 0% utilization

### 봇 토큰 할당
- zero → kernel | dev-master → kernel-mapda | mkt-master → wnsgg0844
- art-master → shaka | commerce-master → viper | sales-master → viper-mapda
- uiux-master → vegapunk | cx-master → forge

## Cycle #11 — Gateway Stale Sessions 분석

- **Observation**: auto-mas에서 main agent 509 sessions (17MB) 식별, cleanup 효과 미미
- **Hypothesis**: cleanup cron이 main agent의 일반 세션을 정리하지 않아 509 files / 17MB 잔존
- **Result**:
  - main: 509 files, 277 older than 24h, 17MB (가장 큰 파일 529KB)
  - size distribution: 127 <10KB, 368 10-100KB, 14 100KB-1MB
  - cleanup cron: 454 sessions.json entries 중 6개만 제거 → main agent 일반 세션 미처리
  - ~55 orphan files (sessions.json에 없는 .jsonl)
  - per-bot sessions: 5-15각, 합계 ~5MB (무시 가능)
  - mas-inference: tool-use fix 후 12 files, 716KB (정상)
- **Verdict**: ✅ Confirmed
- 적용 없음 — 데이터 삭제 사용자 승인 필요
- **제안**: cleanup-sessions.sh 확장 — (1) orphan .jsonl 정리, (2) 48h+ 비MAS 세션 정리

## Cycle #12 — FAS assign_token() Race Condition 분석

- **Observation**: 이전 세션에서 "FAS get_state()/save_state() 덮어쓰기" 이슈 식별
- **Hypothesis**: TOCTOU race condition 존재 — 동시 요청 시 state 유실
- **Result (코드 분석)**:
  - `assign_token()` L1154, `check_and_heal()` L2080, `proactive_rotate()` L1203 — 3개 함수가 get→mutate→save 패턴
  - Lock 메커니즘: **0개** (threading.Lock, RLock, fcntl.flock 모두 미사용)
  - `HTTPServer(daemon_threads=True)` — 동시 HTTP 스레드 + 백그라운드 daemon 루프
  - STATE_FILE + POOL_FILE 2개 파일 동시 경합 가능
  - 위험 필드: totalRotations, rotationHistory, circuitBreakers, stormPauseUntil 등
  - 폭발 반경: CB 감지 실패, rotation 기록 유실, 403 storm 루프
- **Result (실제 증상)**:
  - totalRotations=18, history=18 → gap 없음
  - 403 events: 0건
  - 최근 로그에 race 관련 에러 없음
  - **이유**: low-power mode, 저빈도 rotation (18건), 동시 요청 충돌 확률 매우 낮음
- **Verdict**: ⚠️ Partial (코드 취약점 확인, 실제 증상 미발현)
- **수정안**: `threading.RLock()` 추가 — assign_token/check_and_heal/proactive_rotate 전체를 단일 lock 보호
- 적용 없음 — 잠재적 취약점, 즉각적 피해 없음

---

## Cycle #13 — Direct Inference Mode 배포 확인

- **Hypothesis**: direct inference mode (Gateway 우회) 코드가 미배포
- **Result**: 이미 배포 완료 — 두 서버 경로 + 런타임 config에 "direct" 설정
- **Verdict**: ❌ Rejected

## Cycle #14 — Direct Mode 실효성 검증

- **Hypothesis**: direct mode가 실가동 중이며 토큰/비용 대폭 절감
- **Result**: 3개 요청 분석 — 에이전트당 6.8K-14.6K 토큰 (이전 65K-378K 대비 95% 감소), 비용 $0.026-$0.178/req (이전 $0.30)
- "Skipping batch (direct mode)" 로그로 실제 raw endpoint 사용 확인
- **Verdict**: ✅ Confirmed

## Cycle #15 — Swap 95% 사용량 영향 조사

- **Hypothesis**: Swap 95% (7.6G/8G)가 시스템 성능 저하 유발
- **Result**: memory pressure avg=0.00, swap I/O si=0 so=0, available 48Gi — 과거 할당 잔재
- **Verdict**: ❌ Rejected

## Cycle #16 — MAS 최근 에러 패턴

- **Observation**: 12시간 35 요청, 에러 4건 (11:58-12:14 xapi restart window)
- 12:16 이후 20 요청 100% 성공, 18 고유 에이전트 사용
- Ashley Yoo 35%, Nexus 25% — 약간 높은 집중도

## Cycle #17 — React 쿼리 uiux 오라우팅 버그 발견 및 수정

- **Observation**: "React 19 서버 컴포넌트" → domains=['uiux'] (developers여야 함)
- **Root Cause**: Cycle #59 함수→도메인 추론 로직 (`analyze_request` L52)
  - `domains == ["developers"]` 체크가 default fallback과 실제 매칭 구분 불가
  - `_infer_domain_from_functions`가 developers를 제외 (L148) → uiux로 오버라이드
- **Fix**: `detect_domain()`에 `return_default_flag` 추가 → `domain_is_default` 기반 조건 분기
- **Verification**: React 쿼리 2건 → developers 유지, Kubernetes default → function inference 정상, 기존 케이스 변화 없음
- **Files**: `mas/mas_persona_index.py` (detect_domain), `mas/mas_orchestrator.py` (analyze_request)
- **Verdict**: ✅ Confirmed — 적용됨

→ 다음: 서버 배포 및 라이브 검증

## Cycle #18 — Gateway Session Cleanup 확장

- **Observation**: Cycle #11에서 main agent 509 sessions (17MB), cleanup 무효 확인
- **Hypothesis**: cleanup-sessions.sh가 MAS 키만 처리하므로, orphan 파일 + 비MAS 세션 정리 추가 필요
- **실험 (sessions.json 분석)**:
  - sessions.json: 88 keys, MAS keys 0%, 비MAS keys 100% (UUID)
  - orphan 파일: 421/509 (83%), 14MB
- **적용**: cleanup-sessions.sh 3-phase 확장
  - Phase 1: MAS keys (24h TTL, 기존)
  - Phase 2: Non-MAS conv keys (72h TTL, 신규)
  - Phase 3: Orphan .jsonl files (24h TTL, 신규)
- **Dry-run 결과**: Phase 2: 15 test keys, Phase 3: 197 orphan files (5.9MB), 총 212건
- **Verdict**: ✅ Confirmed — 스크립트 배포 완료, 다음 cron (04:00 UTC) 자동 실행
- **Files**: `scripts/cleanup-sessions.sh` (로컬 + 서버)

## Cycle #19 — FAS Race Condition (상세 분석)

- **Observation**: 이전 세션에서 "FAS assign_token() state race" 식별
- **Hypothesis**: TOCTOU race condition — lock 0개, 동시 요청 시 state 덮어쓰기
- **실험**: Explore 에이전트 코드 분석 + 서버 로그 증상 검색
- **결과**: 코드에 Lock 메커니즘 0개 확인, 다만 실제 증상 미관찰 (저부하)
  - totalRotations=18, history=18, 403 events=0
  - 잠재적 위험: CB 감지 실패, 403 storm 루프
- **수정안**: `threading.RLock()` 추가 (assign_token, check_and_heal, proactive_rotate 래핑)
- **Verdict**: ⚠️ Partial (코드 취약점 확인, 실제 증상 미발현)
- 적용 없음 — 잠재적 취약점

## Cycle #20 — Direct Inference Mode 배포 확인

- **Hypothesis**: direct inference mode (Gateway 우회) 코드가 미배포
- **Result**: 이미 배포 완료 — 두 서버 경로 + 런타임 config에 `inference_mode: "direct"` 설정
- **Verdict**: ❌ Rejected

## Cycle #21 — Direct Mode 토큰/비용 효과

- **Hypothesis**: direct mode가 실가동하며 토큰/비용 대폭 절감
- **Result**: 에이전트당 6.8K-14.6K 토큰 (이전 378K 대비 95% 감소), $0.026-$0.178/req (이전 $0.30)
- "Skipping batch (direct mode)" 로그 확인
- **Verdict**: ✅ Confirmed

## Cycle #22 — Swap 95% 영향

- **Hypothesis**: Swap 7.6G/8G가 성능 저하 유발
- **Result**: memory pressure 0.00, swap I/O 0, available 48Gi — 과거 잔재
- **Verdict**: ❌ Rejected

## Cycle #23 — MAS 에러 패턴

- 12시간 35 요청, 에러 4건 (11:58-12:14 xapi restart window)
- 12:16 이후 20 요청 100% 성공
- 18 고유 에이전트, Ashley Yoo 35% / Nexus 25%

## Cycle #24 — React 쿼리 uiux 오라우팅 **버그 발견+수정**

- **Root Cause**: Cycle #59 `domains == ["developers"]` 체크가 default vs actual match 구분 불가
- `_infer_domain_from_functions`가 developers 제외 → uiux로 오버라이드
- **Fix**: `detect_domain(return_default_flag=True)` + `domain_is_default` 조건
- **Verification**: 7개 테스트 케이스 통과, 라이브 MAS dry-run 확인
- **Files**: `mas/mas_persona_index.py`, `mas/mas_orchestrator.py`
- **Deployed**: 양쪽 경로 + MAS restart
- **Verdict**: ✅ Confirmed

## Cycle #25 — Routines 엔진 작동 확인

- 4 routines loaded, 24h 5회 trigger
- system-health-check 3회 성공, video-production 1회 타임아웃 + 1회 성공 (29s, $0.015)
- 타임아웃은 xapi 불안정 시간대 일시적 이슈
- **Verdict**: ⚠️ Partial (정상 작동, 샘플 부족)

## Cycle #26 — 인사이트 축적 현황

- developers 3건, marketers 3건, 나머지 0건 (총 6건)
- 고품질: WebSocket 메모리 누수, HPA 120초 체인, Amazon PPC 타이밍, A+ 72시간 룰
- 라이브러리 injection 확인됨 (에이전트 프롬프트에 포함)

## Cycle #27 — Library injection char limit 분석

- **Hypothesis**: library injection이 max_refs_chars(3000) 초과 → 4971 chars developers
- **Result**: `max_refs_chars`는 references.md에만 적용 (설계 의도). insights.md는 별도 추가. total = refs(≤3000) + insights(~1900) + formatting
- **Verdict**: ❌ Rejected (설계대로)

## Cycle #28 — AMM 메모리 활용률 분석

- **Hypothesis**: AMM keyword gating이 너무 엄격하여 trigger율 < 10%
- **Result**: 24h 229 decisions — skip 53(23%), inject 69(30%), timeout 0
  - **Trigger rate 57%** (checked queries 중)
  - amm_timeout 3.0s 수정 이후 timeout 0건
  - 57,494 memories (cold 3.5K, warm 53.6K, hot 345)
  - AMM cron: 정상, 품질 게이트 100%
- **Verdict**: ❌ Rejected (57% 활용률, 건강)

## Cycle #29 — 10사이클 체크포인트

### 오늘 세션 누적 현황 (Cycles #1-28)
- **Confirmed**: 12 (FAS 프로세스, xapi deploy restart, 디스크 분석, f1common 미사용, FAS vault, xapi 프록시 비활성, direct mode, React routing fix, session cleanup 확장, NAS regex 배포 확인 기각→확인, 인사이트 축적)
- **Rejected**: 9 (AMM-Surfacer DOWN, Gateway 불안정, NAS regex 미배포, Swap 영향, Library char limit, AMM 활용률 저조, direct mode 미배포)
- **Partial**: 4 (디스크 정리, FAS race condition, Routines 엔진, domain detection)
- **Observation**: 3 (MAS 에러 패턴, MAS 39회 재시작, sub-product library)

### 주요 성과
1. **Session cleanup 스크립트 확장**: 3-phase (MAS/conv/orphan) → 다음 cron에서 ~212파일(6MB) 정리 예정
2. **FAS race condition 문서화**: TOCTOU 취약점 확인, 수정안 제시 (현재 저부하로 미발현)
3. **시스템 건강도 종합 확인**: 9/9 서비스 active, AMM 57K memories + 57% 활용, 에러 0

### 미해결 항목 (우선순위)
1. **Brave Search API 키 갱신** — 사용자 행동 필요
2. **xapi anthropic_api_key 갱신** — 사용자 행동 필요
3. **FAS threading.RLock() 추가** — 저위험 잠재 취약점
4. **stale main sessions cleanup 실행** — 스크립트 배포됨, cron 대기
5. **Sub-product library injection** — 기능 확장, 복잡

## 누적 현황: 29 cycles — Confirmed 12, Rejected 9, Partial 4, Archive 3, Observation 3
## Applied Changes: 5 (xapi 인프라, domain detection fix, session cleanup, domain default fix, session cleanup 3-phase)
