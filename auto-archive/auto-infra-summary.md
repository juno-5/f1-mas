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
6. **Backup size_bytes=0 버그** — 6/7 rsync targets가 size_bytes=0 보고. 원인: `_backup_rsync()`에 --stats 미사용 + `rsync_backup()`이 "Total transferred file size" (delta) 파싱. 수정: --stats 추가 + "Total file size:" 파싱.
7. **Backup 실제 용량** — Total 564 MB (shared-config 16.4M, agent-profiles 22.6M, qdrant 525.4M). Vault/EventBus/ConfigStore/Logs 각 <1KB (deployed but minimal usage).

## Bug Fixes

- `f1-vault/vault/models.py`: `SecretRequest.path` 기본값 `""` 추가 (기존: 필수 필드)
- `f1-backup/backup/scheduler.py`: `_backup_rsync()`에 `--stats` 추가 + "Total file size:" 파싱 (size_bytes=0 fix)
- `f1-backup/backup/rsync.py`: "Total transferred file size:" → "Total file size:" 파싱 변경 (delta→total)

## Production Usage Audit (Cycle #8-10)

| Service | Production Usage | Memory RSS | Status |
|---------|-----------------|-----------|--------|
| EventBus | ZERO | 52 MB | Standby |
| LogBus | ZERO (Token Manager's F1_SERVICE not set) | 45 MB | Standby |
| Vault | ZERO | 50 MB | Standby |
| ConfigStore | ZERO | 55 MB | Standby |
| **Total** | | **202 MB** (0.3% of 62GB) | |

- Architecture ready (f1common clients, xapi proxy routes, fallback mechanisms)
- Integration NOT executed — all data is test residue from Cycle #4
- Standby 유지 합리적 (202MB는 무시 가능, 향후 통합 시 재배포 불필요)

## Pending Actions

1. Vault plaintext → encrypted 마이그레이션 (14 files, 사용자 승인 필요)
2. ~~Backup 첫 실행 테스트~~ — Cycle #6-7 완료, size_bytes 수정 확인
3. ~~xapi 인프라 프록시~~ — Auto #9에서 활성화 완료 (13 services healthy)
4. f1common 클라이언트 → 인프라 서비스 연동 (Token Manager F1_SERVICE 환경변수 추가가 첫 단계)
5. EventBus well_known topics에 대한 실제 구독 설정

## Change History

- 2026-02-24 (Cycle #1-2): 인프라 미배포 상태 발견, 코드 배포 가능 확인
- 2026-02-24 (Cycle #3): 5개 서비스 전체 배포 (EventBus → LogBus → Vault → ConfigStore → Backup)
- 2026-02-24 (Cycle #4): 통합 테스트 + Vault 버그 수정
- 2026-02-24 (Cycle #5): Vault migrate dry_run (14 files 발견)
- 2026-02-24 (Auto #9): xapi 인프라 통합 — F1_SERVICES에 4개 추가 + proxy routes 활성화 (13 services healthy)
- 2026-02-24 (Cycle #6-7): Backup size_bytes=0 버그 발견 및 수정. Total 564 MB 확인.
- 2026-02-24 (Cycle #8-10): Production usage audit — 4개 서비스 전부 idle (test data only). 202MB RSS standby 유지 결정.
