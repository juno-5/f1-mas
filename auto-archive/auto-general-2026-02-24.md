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

## 누적 현황: 11 cycles — Confirmed 6, Rejected 2, Partial 1, Archive 2
## Applied Changes: 1 (xapi 인프라 통합)
