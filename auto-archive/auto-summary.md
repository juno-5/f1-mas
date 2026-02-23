# Auto×xapi Summary

## 시작
- 세션 4: 2026-02-21
- 이전 세션: Cycle #22까지 (xapi v2 배포, AMM surface 필드 수정, SDK 확장)

## 주요 발견

### Session 3 (Cycle #20-#22)
- xapi v2 배포: 44→46 endpoints (inference, qdrant, model-router, scaffold)
- AMM surface field mismatch 수정: query→message, persona→agent
- SDK 확장: fas.lease/release, mas.character, request_and_wait

### Session 5 (Cycle #28-)
- Auto 스킬 dashboard 파싱 버그: `v.get("healthy")` → `v.get("status")` 수정 (2 files)
- 전체 서비스 8/8 OK 확인 (MAS 178 personas, AMM 19133 memories, Qdrant v1.16.3)

### Session 4 (Cycle #23-#27)
- MAS character endpoint: callsign→F1-ID 자동 변환 (forge→F1-02)
- SDK 확장: amm.pipeline(), fas.lease/release, mas.character
- 서버 420KB 중복 디렉토리 정리
- 46/46 엔드포인트 전수 검증 완료
- Qdrant text search 정상 동작 확인 (TEI bge-m3 임베딩)

## 기각된 가설
- (없음)

## 미해결 가설
- 서버에 중복 디렉토리 존재: `xapi/xapi/xapi/` (낭비)
- `/amm/pipeline` 엔드포인트 — 언제 추가되었는지, 동작 확인 필요

## 변경 이력
| 파일 | 커밋 | 설명 |
|------|------|------|
| xapi v2 전체 | 81d822a | 46 endpoints, SDK expansion |
| f1-fas/XAPI.md | a64bd4a | lease/release + TODO |
| f1-mas/XAPI.md | 30f0732 | character + TODO |
