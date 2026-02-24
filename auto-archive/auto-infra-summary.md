# Auto × Infra — Summary

## Infrastructure Stack

| Service | Port | Status | Storage |
|---------|------|--------|---------|
| EventBus | 7810 | active | JSONL (7-day retention) |
| LogBus | 7820 | active | JSONL (14-day retention) |
| Vault | 7830 | active | Encrypted files (Fernet) |
| ConfigStore | 7840 | active | Versioned JSON |
| Backup | timer | daily 03:00 UTC | Snapshots + rsync |

## Key Findings

1. **인프라 전체 미배포 상태** — 5개 서비스 전부 코드 완비였으나 서버에 한 번도 배포되지 않았음
2. **Cycle #3에서 전체 배포 완료** — EventBus → LogBus → Vault → ConfigStore → Backup 순차 배포
3. **Vault SecretRequest 버그 수정** — `path` 필드가 body에서 필수로 요구되어 422 에러 발생, 기본값 `""` 추가로 해결
4. **통합 테스트 전체 통과** — publish/subscribe, write/read, ingest/query, ConfigStore→EventBus 알림 모두 정상
5. **Vault migrate dry_run** — 14개 plaintext credential 파일 마이그레이션 가능 (실제 마이그레이션은 사용자 승인 대기)

## Bug Fixes

- `f1-vault/vault/models.py`: `SecretRequest.path` 기본값 `""` 추가 (기존: 필수 필드)

## Pending Actions

1. Vault plaintext → encrypted 마이그레이션 (14 files, 사용자 승인 필요)
2. Backup 첫 실행 테스트 (`backup.scheduler local`)
3. xapi 인프라 프록시 — scaffolded (코드 완비), 활성화 시 `_EXCLUDE_MODULES` 제거 + `F1_SERVICES` 추가 필요
4. f1common 클라이언트 → 인프라 서비스 연동 (FAS: ~60줄, 2/3 경로 일치 확인)
5. EventBus well_known topics에 대한 실제 구독 설정

## Change History

- 2026-02-24 (Cycle #1-2): 인프라 미배포 상태 발견, 코드 배포 가능 확인
- 2026-02-24 (Cycle #3): 5개 서비스 전체 배포 (EventBus → LogBus → Vault → ConfigStore → Backup)
- 2026-02-24 (Cycle #4): 통합 테스트 + Vault 버그 수정
- 2026-02-24 (Cycle #5): Vault migrate dry_run (14 files 발견)
- 2026-02-24 (Auto #9): xapi 인프라 통합 — F1_SERVICES에 4개 추가 + proxy routes 활성화 (13 services healthy)
