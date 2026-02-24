# Auto × Library — Summary

## Key Findings
1. 53개 Slack 채널에서 115개 문서 링크 발견 (GDrive 66, Notion 41, doc_url 8)
2. Notion 페이지 fetch 성공률 ~43% (API) / 89% (URL 건강도 — 브라우저 접근 가능)
3. growth 채널이 가장 풍부한 지식 소스 (틱톡 세미나 6개, AI 컨퍼런스 3개)
4. cosduck-app 채널이 commerce + marketers 크로스도메인 허브
5. **8/8 도메인 references.md 모두 populated** — 총 284 entries (top-level)
6. Notion workspace 직접 검색으로 700+ 페이지 탐색 (10+ keyword rounds)
7. 제네릭 Notion URL 문제 발견 → 실제 page ID로 수정 완료 (10+ URLs)
8. **슈퍼멤버스 집중 스캔**: Notion 검색으로 120+ 고유 페이지 발견, 6개 도메인에 110+ entries 분배
9. **Slack files.list API**: 40개 GDrive 파일 발견 (gsheet 34 + gdoc 6), 25개 신규
10. **GDrive CSV export fallback**: scanner 패치 후 84% fetch 성공률 (이전 18%)
11. **콘텐츠 기반 비고 검증**: 파일명 ≠ 실제 내용인 경우 4건 교정 (앰플리튜드→인력배정 등)
12. **Sub-product 동기화**: 14개 sub-product references.md에 53+ 건 추가
13. **Slack pins.list**: 54채널 46핀에서 10개 신규 GDrive URL 발견 (6건 등록)
14. **Notion 비고 보강**: API로 실제 내용 읽어 17건 generic 비고 → 구체적 설명 교체
15. **Notion 키워드 검색 10 rounds**: 물류/크리에이터/디자인/브랜딩/촬영/슈퍼차트/SOP/프로세스/전환율/리텐션/보고서/매출/분석/회의록/배포/서버/캐스팅/인플루언서/코딩 컨벤션 → 37+ 고가치 등록
16. **Placeholder 섹션 구축 5개**: Design System, Shooting Guidelines, Brand Guidelines, CS Operations, Infrastructure → 실제 내용으로 교체
17. **URL 건강도 검증**: 194개 Notion URL 중 89% 접근 가능, old-style UUID 5~8건만 진짜 접근 불가

## Rejected Hypotheses
- "Notion 80% fetch 가능" → 43-46% (Partial) — 통합 접근 권한이 일부 페이지만
- "GDrive 50%+ fetch 가능 (gog CLI)" → 18% (Rejected) — gog CLI 미설치
- "Google Drive API (서비스 계정)" → 0% (Rejected) — vegapunk-ga4 계정은 GA4 전용
- "DM 히스토리에서 문서 발견" → 0개 (Rejected) — DM은 봇 대화만, 문서 공유 없음
- "Slack bookmarks" → 0건 (Rejected) — 팀 미사용
- "채널 topic/purpose URL" → 0건 (Rejected)
- "미참여 채널 읽기" → 불가 (Rejected) — not_in_channel 에러
- "증분 스캔 (24-26h)" → 0건 × 2회 (Rejected) — 짧은 기간 활동 없음
- "코딩 표준 문서" → 0건 (Rejected) — 팀 내 Notion에 코딩 컨벤션 문서 없음

## Current Entry Counts (2026-02-24, Cycle #45)

| Domain | Top-level | Sub-products | Notes |
|--------|-----------|--------------|-------|
| developers | 46 | supermembers/dev 17 | 앱 성능, API, Infrastructure 구축, Ads_Payment |
| marketers | 56 | supermembers/mkt 17, superchart/mkt 16 | 틱톡, 릴스 알고리즘, 메타 분석, 인플루언서 가이드 |
| creatives | 13 | — | Creative Boost, 콘텐츠 가이드, 브랜드 가이드 |
| commerce | 76 | cosduck/mkt 22, cosduck/dev 9, cosduck/plan 5 | HEEDA, 틱톡샵, 물류, 콘텐츠 분석, 키워드 관리 |
| sales | 34 | supermembers/sales 16, superchart/sales 8 | AE 파이프라인, 이탈 분석, 퍼널, 정산 |
| uiux | 25 | — | UX 설계, 디자인 시스템, 블로거 탐색 |
| cx | 25 | supermembers/cx 9 | VOC SOP, CS Operations, 리텐션 템플릿 |
| models | 10 | — | 캐스팅, 촬영 가이드, 일본 MCN, 포트폴리오 DB |
| **Total** | **285** | **~119** | **≈ 404** |

## Change History
- 2026-02-23 (Cycles #1-11): 초기 스캔, 8 도메인 population, scanner 4 patches
- 2026-02-23 (Cycle #12): GDrive CSV export 검증 — AE 시트 5건 비고 개선
- 2026-02-23 (Cycle #14): Slack files.list — 25개 신규 GDrive 문서 → 6 도메인에 +28
- 2026-02-23 (Cycle #15): GDrive CSV fetch 21/25 (84%) — 22건 비고 정확도 개선
- 2026-02-24 (Cycle #16): Sub-product 동기화 — 7개 sub-product에 32건 추가
- 2026-02-24 (Cycle #18): Slack snippets — Ads_Payment 4 entries
- 2026-02-24 (Cycle #20): Notion fetch → 비고 보강 17건 (5개 도메인)
- 2026-02-24 (Cycle #22): Slack pins.list → 6건 추가 (4개 도메인)
- 2026-02-24 (Cycle #26): Notion 검색 (물류/크리에이터) → commerce +6, creatives +2
- 2026-02-24 (Cycle #28): Notion 검색 (디자인/브랜딩/촬영) → uiux +5, marketers +4, models +4
- 2026-02-24 (Cycle #31): Notion 검색 (슈퍼차트) → superchart +4, sales +1
- 2026-02-24 (Cycle #32): 중복 URL 정리 → -3
- 2026-02-24 (Cycle #33): Notion 검색 (SOP/프로세스) → cx +3, commerce +6
- 2026-02-24 (Cycle #35): Notion 검색 (전환율/리텐션) → sales +1, commerce +2, cx +1
- 2026-02-24 (Cycle #38): Notion 검색 (보고서/매출/분석) → marketers +3, commerce +3, sales +1
- 2026-02-24 (Cycle #41): Notion 검색 (배포/서버/DB) → developers +5 (Infrastructure 구축)
- 2026-02-24 (Cycle #42): Notion 검색 (캐스팅/인플루언서) → models +1, marketers +1
- 2026-02-24 (Cycle #44): URL 건강도 검증 — 194 URLs, 89% accessible

## Notion Keyword Search Rounds

| Round | Keywords | Pages Found | Registered | Cycle |
|-------|----------|-------------|------------|-------|
| 1 | 슈퍼멤버스 | 120+ | 110+ | #1-11 |
| 2 | 물류, 크리에이터 | 103 | 8 | #26 |
| 3 | 디자인, 브랜딩, 촬영 | 110 | 13 | #28 |
| 4 | 슈퍼차트, superchart | 89 | 5 | #31 |
| 5 | SOP, 온보딩 가이드, 정산 프로세스 | 68 | 9 | #33 |
| 6 | 전환율, 리텐션, A/B 테스트 | 89 | 4 | #35 |
| 7 | 보고서, 매출, 분석, 회의록 | 119 | 7 | #38 |
| 8 | 배포, 서버, 데이터베이스, 테스트 | 57 | 5 | #41 |
| 9 | 캐스팅, 포트폴리오, 인플루언서 | 42 | 2 | #42 |
| 10 | 코딩 컨벤션, 코드 리뷰, API 설계, QA | 54 | 0 | #43 |

## Infrastructure
- **library-scanner.py** (ai1 `~/.f1crew/scripts/mas/`): 4 patches 적용
  - Patch 1: URL persistence in state
  - Patch 2: `--since` flag override
  - Patch 3: GDrive spreadsheet/presentation CSV/TXT export fallback
  - Patch 4: Auto-save results to file
- **google-api-python-client** 서버 설치 완료 (GA4 서비스 계정만, 문서 접근 불가)

## Bot Memory Collection (Cycle #46, 2026-02-24)

- **34개 에이전트** 워크스페이스의 메모리 파일 전체 스캔
- **1,750개 인사이트 카드** 수집 → 8개 도메인별 `memory-insights.md` 생성
- 분류: developers 1,116 | marketers 145 | creatives 111 | sales 92 | cx 86 | uiux 80 | commerce 70 | models 50
- 총 크기: ~899KB (10,556줄)
- library-scanner.py에 `--mode=memory`, `--mode=memory-collect` 추가
- auto-library.md 스킬에 소스 B (봇 메모리 스캔) 추가

## Unresolved / Future
1. Notion 통합에 더 많은 페이지 공유 시 fetch 성공률 80%+ 달성 가능
2. 99개 미참여 채널에 봇 초대 시 추가 문서 발견 가능 (수동 작업 필요)
3. 주기적 증분 스캔으로 신규 문서 자동 발견 (cron 설정 가능)
4. 남은 placeholder 섹션: Architecture & Standards (코딩 컨벤션 문서 팀 미작성), Research Methods, Agencies 등
5. Notion 키워드 추가 탐색 가능하나 수확 체감 (Round #10에서 0건)
6. memory-insights.md 도메인 분류 정확도 개선 가능 (dev personas의 비기술 연구 정밀 분류)

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
| Notion workspace | search API | 800+ pages (10 keyword rounds) |
| GDrive CSV export | public export URL | 84% success |
| Non-member channels | conversations.history | blocked (not_in_channel) |
