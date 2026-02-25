# Auto × Infra — 2026-02-24

## Cycle #1 — 인프라 서비스 상태 조사
- **Observation**: 4개 HTTP 서비스 전부 inactive, 백업 타이머 미등록
- **Hypothesis**: systemd 유닛 존재하지만 비활성
- **Result**: 유닛 파일 자체 미존재, 스크립트 미배포 — 인프라 레이어가 전혀 배포된 적 없음
- **Verdict**: Rejected (가설보다 더 심각한 상태)

## Cycle #2 — 코드 배포 가능성 확인
- **Hypothesis**: 5개 서비스 로컬 코드가 배포 가능 상태
- **Result**: 전부 배포 가능 (deploy scripts, systemd units, server code, dependencies 완비)
- **Verdict**: Confirmed

## Cycle #3 — 전체 인프라 배포
- **Hypothesis**: 순차 배포로 5개 서비스 전부 가동 가능
- **Execution**:
  1. EventBus (:7810) — OK (health ok, topics:0, subs:0)
  2. LogBus (:7820) — OK (health ok, entries:0)
  3. Vault (:7830) — OK (health ok, key_initialized:true)
  4. ConfigStore (:7840) — OK (health ok, ns:0, keys:0)
  5. Backup (timer) — OK (1 timer registered, daily 03:00 UTC)
- **Verdict**: Confirmed — 전부 active

## Cycle #4 — 통합 테스트 + Vault 버그 수정
- **Tests**:
  - EventBus publish/read: OK
  - ConfigStore write/read: OK
  - ConfigStore → EventBus 알림: OK (config.changed.test 자동 발행)
  - LogBus ingest/query: OK
  - Vault write: **422 에러** (SecretRequest.path 필수)
- **Bug Fix**: `vault/models.py` SecretRequest.path 기본값 "" 추가
- **Redeploy**: Vault 재배포 후 전체 테스트 통과
- **Verdict**: Confirmed (버그 수정 후)

## Cycle #5 — Vault Migrate Dry Run
- **Hypothesis**: plaintext credential 파일 5+ 발견 가능
- **Result**: 14개 파일 마이그레이션 대상 (credentials/ 디렉토리)
- **Verdict**: Confirmed (14 >> 5)
- **적용 없음**: 실제 마이그레이션은 사용자 승인 필요

## Cycle #6 — Backup 실제 실행 상태 확인
- **Observation**: Timer LAST="-" (timer 경유 실행 이력 없음), 수동 실행 2026-02-24 성공
- **Hypothesis**: 백업이 정상적으로 데이터를 수집하고 있다
- **Result**: 7/7 targets success, BUT 6/7 rsync targets size_bytes=0 (Qdrant만 530MB 정상)
- **Actual files**: shared 94 files/16M, agents 645 files/23M — 파일은 존재
- **Verdict**: ⚠️ Partial — 백업 자체는 성공하나 size 리포팅 버그

## Cycle #7 — Backup size_bytes=0 리포팅 버그 수정
- **Hypothesis**: _backup_rsync()에 --stats 미사용 + rsync_backup()이 "Total transferred file size" 파싱 (delta only)
- **Root Cause 확인**:
  1. scheduler.py:_backup_rsync() — `rsync -a --delete` (no --stats) → 파싱 불가
  2. rsync.py:rsync_backup() — "Total transferred file size:" 파싱 (incremental=0)
- **Fix**: --stats 추가 + "Total file size:" 파싱 (transferred 제외)
- **Verification**: Full backup 7/7 success
  - shared-config: 16.4 MB, agent-profiles: 22.6 MB, qdrant: 525.4 MB, total: 564.4 MB
  - vault/eventbus/logs/configstore: <1KB each (deployed but minimal usage)
- **Verdict**: ✅ Confirmed
- **Files modified**: backup/scheduler.py, backup/rsync.py
- **Deployed**: deploy-ai1.sh → timer active for 03:00 UTC

## Cycle #8 — 인프라 서비스 프로덕션 사용 현황 감사
- **Hypothesis**: 인프라 4개 서비스가 테스트 데이터만 보유, 프로덕션 사용 없음
- **Result**: 전체 감사 — EventBus/Vault/ConfigStore: ZERO production usage. LogBus: minimal (Token Manager async best-effort)
- **Detail**: f1common clients 존재 + xapi proxy routes 구축됨, but NO service in active request path uses them
- **Architecture**: Ready (clients, fallbacks, proxies), Integration: NOT yet executed
- **Verdict**: ✅ Confirmed

## Cycle #9 — LogBus 실제 전달 여부 확인
- **Hypothesis**: Token Manager log() → LogBus 전달 안됨 (F1_SERVICE env 미설정)
- **Result**: F1_SERVICE 미설정 in any systemd unit. LogBus 4 entries 모두 테스트 잔여물.
- **Root cause**: f1common.logging.py line 57 `if svc:` — service name 비어있으면 enqueue 안함
- **Verdict**: ✅ Confirmed — LogBus도 완전 idle

## Cycle #10 — Idle 인프라 서비스 리소스 비용
- **Hypothesis**: 4개 idle 서비스 메모리 부담 무시 가능
- **Result**: 합산 202MB RSS (0.3% of 62GB). Available 48GB.
- **Swap 7.6/8.0 GB**: text-embeddings-router(8.2GB) + Qdrant(783MB) 등 대형 프로세스 때문
- **Decision**: Standby 유지 합리적 (향후 통합 시 재배포 불필요)
- **Verdict**: ✅ Confirmed

## 누적 현황: 10 cycles — Confirmed 8, Rejected 1, Partial 1
