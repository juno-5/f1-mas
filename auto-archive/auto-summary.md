# Auto × Library — Summary

## Key Findings
1. 153개 Slack 채널에서 115개 문서 링크 발견 (GDrive 66, Notion 41, doc_url 8)
2. Notion 페이지 fetch 성공률 ~43% — 접근 권한 부여 필요
3. growth 채널이 가장 풍부한 지식 소스 (틱톡 세미나 6개, AI 컨퍼런스 3개)
4. cosduck-app 채널이 commerce + marketers 크로스도메인 허브
5. **8/8 도메인 references.md 업데이트 완료** (총 200+ entries)
6. Notion workspace 직접 검색으로 112개 추가 페이지 발견 (uiux 43, models 35, creatives 34)
7. 제네릭 Notion URL 문제 발견 → 실제 page ID로 수정 완료 (10+ URLs)
8. GDrive fetch: gog CLI 미설치로 18% 성공률 → 서비스 계정 CLI 설치 필요
9. **슈퍼멤버스 집중 스캔**: Notion 검색으로 120+ 고유 페이지 발견, 6개 도메인에 110+ entries 분배

## Rejected Hypotheses
- "Notion 80% fetch 가능" → 43-46% (Partial) — 통합 접근 권한이 일부 페이지만
- "GDrive 50%+ fetch 가능" → 18% (Rejected) — gog CLI 미설치, public export만

## Change History
- 2026-02-23: marketers/references.md (30+ entries → URL fix 4 + 8 new → 슈퍼멤버스 17 new)
- 2026-02-23: commerce/references.md (Cosduck 5 → Supermembers 개요 8 + 제품 7 + 매장 7 + 결제 4 + 개밥먹기 4 = 30 new)
- 2026-02-23: developers/references.md (5 refs → 8 new → 슈퍼멤버스 22 new)
- 2026-02-23: sales/references.md (Lead 2 + AE 5 → 슈퍼멤버스 14 new)
- 2026-02-23: cx/references.md (Issue 4 → 슈퍼멤버스 16 new)
- 2026-02-23: creatives/references.md (콘텐츠 가이드 8 entries)
- 2026-02-23: uiux/references.md (UX 설계 6 + UI 개선 4 → 슈퍼멤버스 11 new)
- 2026-02-23: models/references.md (캐스팅 + 촬영 가이드 6 entries)

## Unresolved Hypotheses
1. ~~Google Drive 60개 문서 내용 fetch~~ → **기각**: gog CLI 미설치. 설치 시 재시도 가능
2. Notion 통합에 더 많은 페이지 공유 시 fetch 성공률 80%+ 달성 가능
3. ~~uiux, models 도메인은 Slack 채널에 문서 공유가 거의 없음~~ → **해결**: Notion workspace 직접 검색
4. DM 히스토리에서 추가 문서 발견 가능
5. ~~classifier 키워드 보강 필요~~ → **해결**: channel→domain 수동 매핑으로 93개 분류 완료
6. gog CLI 설치 후 GDrive 54개 private 문서 내용 fetch 가능
