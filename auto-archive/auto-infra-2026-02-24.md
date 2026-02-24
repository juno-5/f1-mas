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

## 누적 현황: 5 cycles — Confirmed 4, Rejected 1
