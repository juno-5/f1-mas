# Auto × Library — Summary

## Key Findings
1. 53개 Slack 채널에서 115개 문서 링크 발견 (GDrive 66, Notion 41, doc_url 8)
2. Notion 페이지 fetch 성공률 ~43% — 접근 권한 부여 필요
3. growth 채널이 가장 풍부한 지식 소스 (틱톡 세미나 6개, AI 컨퍼런스 3개)
4. cosduck-app 채널이 commerce + marketers 크로스도메인 허브
5. **8/8 도메인 references.md 모두 populated** — 총 234 entries (top-level)
6. Notion workspace 직접 검색으로 112개 추가 페이지 발견 (uiux 43, models 35, creatives 34)
7. 제네릭 Notion URL 문제 발견 → 실제 page ID로 수정 완료 (10+ URLs)
8. **슈퍼멤버스 집중 스캔**: Notion 검색으로 120+ 고유 페이지 발견, 6개 도메인에 110+ entries 분배
9. **Slack files.list API**: 40개 GDrive 파일 발견 (gsheet 34 + gdoc 6), 25개 신규
10. **GDrive CSV export fallback**: scanner 패치 후 84% fetch 성공률 (이전 18%)
11. **콘텐츠 기반 비고 검증**: 파일명 ≠ 실제 내용인 경우 4건 교정 (앰플리튜드→인력배정 등)
12. **Sub-product 동기화**: 14개 sub-product references.md에 35건 추가
13. **Slack pins.list**: 54채널 46핀에서 10개 신규 GDrive URL 발견 (6건 등록)
14. **Notion 비고 보강**: API로 실제 내용 읽어 17건 generic 비고 → 구체적 설명 교체

## Rejected Hypotheses
- "Notion 80% fetch 가능" → 43-46% (Partial) — 통합 접근 권한이 일부 페이지만
- "GDrive 50%+ fetch 가능 (gog CLI)" → 18% (Rejected) — gog CLI 미설치
- "Google Drive API (서비스 계정)" → 0% (Rejected) — vegapunk-ga4 계정은 GA4 전용
- "DM 히스토리에서 문서 발견" → 0개 (Rejected) — DM은 봇 대화만, 문서 공유 없음
- "Slack bookmarks" → 0건 (Rejected) — 팀 미사용
- "채널 topic/purpose URL" → 0건 (Rejected)
- "미참여 채널 읽기" → 불가 (Rejected) — not_in_channel 에러
- "증분 스캔 (26h)" → 0건 (Rejected) — 짧은 기간 활동 없음

## Current Entry Counts (2026-02-24, Cycle #25)

| Domain | Top-level | Sub-products | Notes |
|--------|-----------|--------------|-------|
| developers | 41 | supermembers/dev 15 | 앱 성능, API, Ads_Payment snippets |
| marketers | 47 | supermembers/mkt 11, superchart/mkt 13 | 틱톡, 데이바우처, YouTube 광고비 |
| creatives | 12 | — | Creative Boost, 콘텐츠 가이드 |
| commerce | 59 | cosduck/mkt 19, cosduck/dev 5 | HEEDA, 틱톡샵, 키워드 관리 |
| sales | 29 | supermembers/sales 15, superchart/sales 5 | AE 파이프라인, 정산, 전환 |
| uiux | 21 | — | UX 설계, 블로거 탐색 |
| cx | 20 | supermembers/cx 6 | VOC SOP, CS 운영, VOC 시트 |
| models | 5 | — | 캐스팅, 촬영 가이드 |
| **Total** | **234** | **~89** | |

## Change History
- 2026-02-23 (Cycles #1-11): 초기 스캔, 8 도메인 population, scanner 4 patches
- 2026-02-23 (Cycle #12): GDrive CSV export 검증 — AE 시트 5건 비고 개선
- 2026-02-23 (Cycle #14): Slack files.list — 25개 신규 GDrive 문서 → 6 도메인에 +28
- 2026-02-23 (Cycle #15): GDrive CSV fetch 21/25 (84%) — 22건 비고 정확도 개선
- 2026-02-24 (Cycle #16): Sub-product 동기화 — 7개 sub-product에 32건 추가
- 2026-02-24 (Cycle #17): auto-summary.md 전체 리라이트
- 2026-02-24 (Cycle #18): Slack snippets — Ads_Payment 4 entries
- 2026-02-24 (Cycle #19): 증분 Slack 스캔 — 0 new links (Rejected)
- 2026-02-24 (Cycle #20): Notion fetch → 비고 보강 17건 (5개 도메인)
- 2026-02-24 (Cycle #21): Sub-product 비고 동기화 3건
- 2026-02-24 (Cycle #22): Slack pins.list → 6건 추가 (4개 도메인)
- 2026-02-24 (Cycles #23-25): bookmarks/topic/미참여채널 — 모두 Rejected

## Infrastructure
- **library-scanner.py** (ai1 `~/.f1crew/scripts/mas/`): 4 patches 적용
  - Patch 1: URL persistence in state
  - Patch 2: `--since` flag override
  - Patch 3: GDrive spreadsheet/presentation CSV/TXT export fallback
  - Patch 4: Auto-save results to file
- **google-api-python-client** 서버 설치 완료 (GA4 서비스 계정만, 문서 접근 불가)

## Unresolved / Future
1. Notion 통합에 더 많은 페이지 공유 시 fetch 성공률 80%+ 달성 가능
2. 99개 미참여 채널에 봇 초대 시 추가 문서 발견 가능 (수동 작업 필요)
3. 주기적 증분 스캔으로 신규 문서 자동 발견 (cron 설정 가능)

## Explored Data Sources

| Source | API | Result |
|--------|-----|--------|
| Slack messages | conversations.history | 115 links (core source) |
| Slack files | files.list | 40 GDrive files, 25 new |
| Slack pins | pins.list | 46 pins, 10 new URLs |
| Slack bookmarks | bookmarks.list | 0 (unused) |
| Slack topic/purpose | conversations.list | 0 URLs |
| Slack DMs | conversations.history | 0 links |
| Slack snippets | files.list (filetype=snippet) | 57 total, 4 high-value |
| Notion workspace | search API | 112+ pages |
| GDrive CSV export | public export URL | 84% success |
| Non-member channels | conversations.history | blocked (not_in_channel) |
