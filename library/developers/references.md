# Developers — References

> 개발팀 참조 문서, 가이드, 도구 링크

## Architecture & Standards

- [ ] 코딩 컨벤션 가이드
- [ ] API 설계 표준 (REST/GraphQL)
- [ ] Git 브랜치 전략
- [ ] 코드 리뷰 체크리스트

## Infrastructure

| Resource | URL | 비고 |
|----------|-----|------|
| [AWS API Server : 구서버](https://www.notion.so/2be983e32b32813088b7c60090efbb52) | Notion | Express.js 기반, /api 디렉토리 구조, bin/www 진입점 |
| [API Server : 신서버](https://www.notion.so/2be983e32b32816e8eb8e20f110b816f) | Notion | 슈퍼멤버스/슈퍼차트 백엔드 Express.js API 서버 — 서비스 설명, 서버 정보 |
| [TikTok API 서버 Observability 가이드](https://www.notion.so/239983e32b3280b3ba46f8d800f6fa97) | Notion | TikTok API 서버 모니터링 아키텍처 구현 가이드 |
| [영상 업로드시 API서버 에러 코드 목록](https://www.notion.so/23f983e32b3280b7a140f0b3b5c71030) | Notion | 코스덕 리뷰 영상 업로드 에러 (CONTRACT_NOT_FOUND, PERMISSION_DENIED 등) |
| [Cosduck Agency 페이지별 데이터 매핑](https://www.notion.so/2b5983e32b328059963af107f56edcfb) | Notion | TikTok Shop + Amazon 통합 대시보드 — CSV 컬럼→페이지 데이터 매핑 |

## Internal Tools

| Tool | URL | 용도 |
|------|-----|------|
| release-note 채널 | Slack #release-note | 릴리즈 노트 공유 |
| chats-dev 채널 | Slack #chats-dev | 개발 토론 |

## External References

| Resource | URL | Source | 비고 |
|----------|-----|--------|------|
| [React Decorator & HOC Factory](http://seoul.reactjs.kr/assets/slides/react_decorator_hoc_factory/) | 읽을거리 | React 패턴 |
| [Storybook Driven Development](http://seoul.reactjs.kr/assets/slides/storybook_driven_development/) | 읽을거리 | 컴포넌트 개발 |
| [Embedded React Application](http://seoul.reactjs.kr/assets/slides/embedded_react_application/) | 읽을거리 | React 임베딩 |
| [코스덕 어필리에이트 시스템](https://www.notion.so/mayacrew/) | cosduck-app | Affiliate PMF, 기술 아키텍처 |
| [Development 스프레드시트](https://docs.google.com/spreadsheets/d/1Pct6TMAW1dQsU3dZBg9EFW6kRTW1ZQRzaaRWAf77Is8/) | development | 개발 트래킹 |
| [앱 버전 관리 페이지](https://www.notion.so/mayacrew/4d9de4f2f6304b0ca7e93eca2365ac6d) | operation | 배포 버전 + 변경 사항 기록 |
| [onSnapshot 코드 모음](https://www.notion.so/mayacrew/index-js-425a8e97eb9f42a38986656a00d2853b) | chats-dev | Firestore onSnapshot 코드 레퍼런스 |
| [MongoDB Reference 콜렉션 필드](https://www.notion.so/mayacrew/49debd04075d446eaf580413b087d947) | chats-dev | MongoDB 콜렉션 스키마 참조 |
| [웹/앱 이벤트 리스트](https://docs.google.com/spreadsheets/d/1KkynHWxDB6JC_xDMDDiEEY2rJ7bGE9JhsCzhscoTl58/) | chats-dev | 슈퍼차트/슈퍼멤버스 웹·앱 이벤트 정의 |
| [유튜브 관련 데이터 구조](https://docs.google.com/spreadsheets/d/14cMzqMA7ZKwKmyKmvbyTjvqTO0tfWfU9d1v7SA3M-3o/) | chats-dev | YouTube 데이터 구조 정의 |
| [SEO 오픈그래프 태그 요청](https://docs.google.com/spreadsheets/d/1VRNRDY0Z_KCviTUgw3hbXrimYnyz4OytRnvTmHthL1o/) | chats-dev | 슈퍼차트 메인 페이지 SEO 메타 태그 |
| [온라인 강의 리스트](https://docs.google.com/spreadsheets/d/1Wt2QofgOyK7NW-z1YQ-MjIL66wsahf5YjPRAhORtZ20/) | chats-dev | 개발팀 온라인 학습 리소스 |
| [React Native slides](http://seoul.reactjs.kr/assets/slides/react_native.pdf) | 읽을거리 | React Native 소개 |

## 슈퍼멤버스 개발

### 앱 성능 & 아키텍처

| Resource | URL | 비고 |
|----------|-----|------|
| [슈퍼멤버스 앱 경로 정의](https://www.notion.so/23f983e32b3280e186e5d041fba51922) | Notion | 앱 라우팅 경로 전체 정의 |
| [슈퍼멤버스 앱 속도 개선](https://www.notion.so/23e983e32b3280538b83d776146dd139) | Notion | 앱 속도 개선 프로젝트 |
| [슈퍼멤버스 앱 홈 화면 UX 속도 20% 개선](https://www.notion.so/UX-20-22a983e32b3281c5b1d7f49a001bcd48) | Notion | 홈 화면 속도 최적화 |
| [슈퍼멤버스 매장 지도 리스트 로딩 속도 30% 개선](https://www.notion.so/30-223983e32b32816f9268ed3b18bcb8da) | Notion | 지도 로딩 최적화 |

### API 마이그레이션

| Resource | URL | 비고 |
|----------|-----|------|
| [슈퍼멤버스 앱 구 서버 API → 새 서버 API 교체 (2건)](https://www.notion.so/API-API-2-22a983e32b3281c5b6aff27b12ad14f2) | Notion | API 마이그레이션 #1 |
| [슈퍼멤버스 앱 구 서버 API → 새 서버 API 교체](https://www.notion.so/API-API-238983e32b3280478d10e8ffa48dcf90) | Notion | API 마이그레이션 #2 |
| [Supermembers Console API Server](https://www.notion.so/Supermembers-Console-API-Server-2be983e32b3281638c53d63c4cc7208c) | Notion | 콘솔 API 서버 구조 |

### AI & 자동화

| Resource | URL | 비고 |
|----------|-----|------|
| [슈퍼멤버스 앱 내 블로그 포스팅 AI 초안 작성](https://www.notion.so/AI-23e983e32b328083bb1bfebb694eb75e) | Notion | AI 블로그 포스팅 (이전 구현 이력, API 비용으로 비활성화) |
| [슈퍼멤버스 블로그 부정적인 리뷰 감지](https://www.notion.so/23e983e32b32805db0b9cc9455468b0c) | Notion | 리뷰 감지 시스템 |
| [supermembers-rag](https://www.notion.so/supermembers-rag-2e8983e32b328001a5f5da3c2acb9186) | Notion | RAG 시스템 설계 |

### 챗봇 & 인수인계

| Resource | URL | 비고 |
|----------|-----|------|
| [슈퍼멤버스 챗봇 콘솔 인수인계서 (1)](https://www.notion.so/1-2fc983e32b3280af9bfec994039cc6b8) | Notion | 챗봇 콘솔 5개 영역 구조, CX팀 KPI 대시보드 (Analytics), 첫 응대 시간 지표 |
| [슈퍼멤버스 챗봇 인수인계서](https://www.notion.so/1-2fc983e32b3280499a07dfcf4dbb92a8) | Notion | QA_DB 3단 구조 (카테고리→세부질문→답변), 챗봇 시스템 추적/보완 가이드 |
| ~~[슈퍼멤버스 인수인계 내역](https://www.notion.so/22b983e32b328096a246fd5ccbd3dc44)~~ | — | → supermembers/operations로 이동 (개발 아닌 운영 문서) |

### 분석 & 테스트

| Resource | URL | 비고 |
|----------|-----|------|
| [믹스패널 SDK 설치 (슈퍼멤버스 앱)](https://www.notion.so/SDK-200983e32b3280f9abbbdb132d93bd5d) | Notion | 앱 Mixpanel SDK 설치 |
| [믹스패널 SDK 설치 (슈퍼멤버스 웹)](https://www.notion.so/SDK-200983e32b32803daac3d6ac40445afe) | Notion | 웹 Mixpanel SDK 설치 |
| [슈멤 APP 문제점](https://www.notion.so/2b6983e32b32802c8424f20c1bfcd3f2) | Notion DB | 앱 이슈 트래커 |
| [슈퍼멤버스 프로젝트 우선순위 설정](https://www.notion.so/23e983e32b32803698cae0b4c4b62926) | Notion | 개발 우선순위 |

### 인프라 & 설정

| Resource | URL | 비고 |
|----------|-----|------|
| [슈멤 테스트 매장 생성 방법](https://www.notion.so/193983e32b32807db5bfef2ad42e9cf3) | Notion | 테스트 매장 세팅 가이드 |
| [슈퍼멤버스 테스트 가맹점 열람 가능한 계정 전환](https://www.notion.so/55c9e5b12d084392be4736c536e426d8) | Notion | 테스트 계정 설정 |
| [ceo.supermembers.co.kr](https://www.notion.so/ceo-supermembers-co-kr-7d11940be518402faa9cef02be097b20) | Notion | 사장님 사이트 기술 스펙 |
| [슈멤앱 > ip 블락](https://www.notion.so/ip-124373cdcc9d4c70891a72dc18d740e5) | Notion | IP 차단 정책/구현 |

## Slack 파일 업로드 (GDrive)

| Resource | Source | 비고 |
|----------|--------|------|
| [슈퍼멤버스 3.0 기획서](https://docs.google.com/spreadsheets/d/1HzzvkFPOBDH6x7mX8xjXUwHTWwwSua0fbHLnFDeumFg/) | development | 슈퍼멤버스 3.0 기획/설계 |
| [앰플리튜드 (데이터바우처 인력)](https://docs.google.com/spreadsheets/d/1FVptHbgepKpoagv-VNMHD4PybqLZRYZb8ZfOZ3Jh22o/) | supermembers | 데이터바우처 참여인력 구분 및 업무 배정 |
| [단계별 푸시발송 리스트](https://docs.google.com/spreadsheets/d/1_ettWTKoRohFYkxOiUOY30AJ3VwyxnrO6H58VDWMyFU/) | supermembers | 카카오 알림톡 템플릿 관리 (발송조건/대상/변수/버튼URL) |

## Slack Snippets (Ads_Payment 정합성)

| Resource | Source | 비고 |
|----------|--------|------|
| [Ads_Payment 관리 기능 기획서](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AG133MBQC/admin_features.md) | 슈퍼멤버스 | 결제 정합성 프로젝트 — 5개 핵심 기능 기획 (610줄) |
| [Ads_Payment & Channels 필드 레퍼런스](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AGAC9MMJ5/field_reference.md) | 슈퍼멤버스 | 결제 데이터 필드 및 규칙 정리 (331줄) |
| [Ads_Payment 테이블 수정 규칙](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AFR387VMH/payment_rule.md) | 슈퍼멤버스 | 결제 데이터 수정 판단 기준 (307줄) |
| [Ads_Payment 비정상 케이스 탐지 도구](https://supermembers.slack.com/files/U0AG2SSK7NV/F0AGRNX3A4Q/readme.md) | 슈퍼멤버스 | 결제 규칙 위배 탐지 도구 README (218줄) |

---

*Last updated: 2026-02-24 (Cycle #41: Infrastructure 섹션 구축 +5)*
