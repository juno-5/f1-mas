# Supermembers — Dev References

> 슈퍼멤버스 개발 관련 문서, 앱 설계, 이벤트 트래킹

## 앱 설계

| Resource | URL | 비고 |
|----------|-----|------|
| [Supermembers 앱 UX 설계 플로우](https://www.notion.so/Supermembers-UX-22b983e32b32812987c0e0c415f98429) | Notion | 슈퍼멤버스 앱 전체 UX 플로우 |

## 이벤트 트래킹

| Resource | URL | 비고 |
|----------|-----|------|
| [Mixpanel 앱 이벤트 명명 시트](https://docs.google.com/spreadsheets/d/1JOwxPZv74fS94kUDIRnbjGGoDrUmlpMsGrhweIUq/) | Google Sheets | 앱 이벤트명 정의 (impressionHome, viewCampaignDetail 등) |

## Analytics IDs

| 소스 | ID | 용도 |
|------|-----|------|
| GA4 앱 | 325653255 | 슈퍼멤버스 앱 (세션, 유저, 이탈률) |
| GA4 사장님사이트 | 283026891 | 어드민 포털 (세션, 체류시간) |
| Mixpanel | 3724416 | 퍼널 이벤트 트래킹 |
| Meta Ads | act_436422822012623 | 광고 성과 |

## 앱 성능 & API

| Resource | URL | 비고 |
|----------|-----|------|
| [슈퍼멤버스 앱 경로 정의](https://www.notion.so/23f983e32b3280e186e5d041fba51922) | Notion | 앱 라우팅 경로 전체 정의 |
| [슈퍼멤버스 앱 속도 개선](https://www.notion.so/23e983e32b3280538b83d776146dd139) | Notion | 앱 속도 개선 프로젝트 |
| [슈퍼멤버스 앱 홈 화면 UX 속도 20% 개선](https://www.notion.so/UX-20-22a983e32b3281c5b1d7f49a001bcd48) | Notion | 홈 화면 속도 최적화 |
| [슈퍼멤버스 매장 지도 리스트 로딩 속도 30% 개선](https://www.notion.so/30-223983e32b32816f9268ed3b18bcb8da) | Notion | 지도 로딩 최적화 |
| [슈퍼멤버스 앱 구 서버 API → 새 서버 API 교체 (2건)](https://www.notion.so/API-API-2-22a983e32b3281c5b6aff27b12ad14f2) | Notion | API 마이그레이션 #1 |
| [슈퍼멤버스 앱 구 서버 API → 새 서버 API 교체](https://www.notion.so/API-API-238983e32b3280478d10e8ffa48dcf90) | Notion | API 마이그레이션 #2 |

## 서버 인프라

| Resource | URL | 비고 |
|----------|-----|------|
| [AWS API Server : 구서버](https://www.notion.so/2be983e32b32813088b7c60090efbb52) | Notion | Express.js 기반, /api 디렉토리 구조 |
| [API Server : 신서버](https://www.notion.so/2be983e32b32816e8eb8e20f110b816f) | Notion | 슈퍼멤버스/슈퍼차트 백엔드 Express.js API 서버 |

## Slack 파일 업로드 (GDrive)

| Resource | URL | 비고 |
|----------|-----|------|
| [슈퍼멤버스 3.0 기획서](https://docs.google.com/spreadsheets/d/1HzzvkFPOBDH6x7mX8xjXUwHTWwwSua0fbHLnFDeumFg/) | development | 슈퍼멤버스 3.0 기획/설계 |
| [단계별 푸시발송 리스트](https://docs.google.com/spreadsheets/d/1_ettWTKoRohFYkxOiUOY30AJ3VwyxnrO6H58VDWMyFU/) | supermembers | 카카오 알림톡 템플릿 관리 (발송조건/대상/변수/버튼URL) |

## Slack Snippets (Ads_Payment 정합성)

| Resource | Source | 비고 |
|----------|--------|------|
| [Ads_Payment 관리 기능 기획서](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AG133MBQC/admin_features.md) | 슈퍼멤버스 | 결제 정합성 프로젝트 — 5개 핵심 기능 기획 (610줄) |
| [Ads_Payment & Channels 필드 레퍼런스](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AGAC9MMJ5/field_reference.md) | 슈퍼멤버스 | 결제 데이터 필드 및 규칙 정리 (331줄) |
| [Ads_Payment 테이블 수정 규칙](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AFR387VMH/payment_rule.md) | 슈퍼멤버스 | 결제 데이터 수정 판단 기준 (307줄) |
| [Ads_Payment 비정상 케이스 탐지 도구](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AGRNX3A4Q/readme.md) | 슈퍼멤버스 | 결제 규칙 위배 탐지 도구 README (218줄) |

---

*Last updated: 2026-02-24 (Cycle #41: 서버 인프라 동기화 +2)*
