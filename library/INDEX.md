# MAS Library — Team Knowledge Base

> 제품별로 정리된 전사 참조 문서 + AI 에이전트 인사이트 지식 허브

## 제품별 라이브러리 (Primary)

| 제품 | 폴더 | 설명 |
|------|------|------|
| **슈퍼멤버스** | `supermembers/` | 블로그 체험단 플랫폼 — 운영, 개발, 마케팅, 세일즈, CX, UX |
| **슈퍼차트** | `superchart/` | 인플루언서 마케팅 대행 — 개발, 마케팅, 세일즈, 데이터바우처 |
| **코스덕** | `cosduck/` | K-Beauty 틱톡샵 에이전시 — 틱톡샵, 크리에이티브, 디자인, 물류 |
| **커머스** | `commerce/` | 자체 브랜드 이커머스 — HEEDA, KIMCHIP, MAPDA, Medihair |

### 노션 페이지

[마야크루 팀별 폴더](https://www.notion.so/mayacrew/311983e32b3280788ac5c9d8ecb279d7) — 제품별로 정리된 전사 참조 문서

### 구조

```
library/
├── INDEX.md                    # 이 문서
├── CAPTURE-PROTOCOL.md         # 인사이트 캡처 규칙
├── LIBRARY-UPDATE-WORKFLOW.md  # 업데이트 워크플로우 & 기록 양식
│
├── supermembers/               # 슈퍼멤버스
│   ├── references.md           # 통합 참조 문서 (모든 팀 포함)
│   ├── dev/                    # 개발
│   ├── marketing/              # 마케팅 (워크스페이스 문서 포함)
│   ├── sales/                  # 세일즈
│   ├── cx/                     # CX
│   ├── uiux/                   # UX/UI
│   ├── operations/             # 운영
│   └── planning/               # 기획
│
├── superchart/                 # 슈퍼차트
│   ├── references.md           # 통합 참조 문서
│   ├── dev/                    # 개발
│   ├── marketing/              # 마케팅
│   └── sales/                  # 세일즈
│
├── cosduck/                    # 코스덕
│   ├── references.md           # 통합 참조 문서
│   ├── dev/                    # 개발
│   ├── marketing/              # 마케팅
│   ├── creative/               # 크리에이티브
│   ├── design/                 # 디자인
│   ├── planning/               # 기획
│   └── sales/                  # 세일즈
│
├── commerce/                   # 커머스 (자체 브랜드)
│   └── references.md           # 통합 참조 문서
│
└── _agents/                    # 에이전트 자동 캡처 (하위 호환)
    ├── developers/             # insights.md, memory-insights.md
    ├── marketers/
    ├── creatives/
    ├── sales/
    ├── uiux/
    ├── cx/
    └── models/
```

> **주의**: `supermembers/` 콘텐츠가 다른 상위 폴더에 들어가지 않도록 분류 시 주의

## 파일 컨벤션

### 제품 폴더 (Primary)
- **`references.md`** — 제품별 통합 참조 문서 (모든 팀 문서 포함)
- 하위 폴더별 `references.md` — 팀별 상세 문서 (워크스페이스 문서 등)

### 에이전트 폴더 (_agents/)
- **`insights.md`** — 직원 대화에서 자동 캡처된 도메인 지식
- **`memory-insights.md`** — 봇 메모리에서 수집된 인사이트 카드

### 기록 양식

모든 참조 문서 테이블은 아래 4컬럼을 사용:

```markdown
| 문서명 | 링크 | 등록일 | 비고 |
|--------|------|--------|------|
| 슈퍼멤버스 결제 프로세스 | [Notion](https://notion.so/...) | 2026-02-25 | 결제 전체 플로우 |
```

### 상태 표시
- 비공개: `~~문서명~~` + `🔒 비공개 (사유) — YYYY-MM-DD`
- 삭제: `~~문서명~~` + `🗑 삭제 (사유) — YYYY-MM-DD`
- 이동: `~~문서명~~` + `→ {new_folder}로 이동 — YYYY-MM-DD`

---

## 인사이트 캡처 프로토콜

마스터 에이전트가 직원과 대화 중 아래 조건을 감지하면 자동으로 `insights.md`에 축적:

1. **도메인 지식 공유** — "우리는 이렇게 해", "이 플랫폼은 이렇게 작동해"
2. **의사결정 맥락** — "이걸로 결정한 이유는...", "A 대신 B를 쓰는 이유"
3. **실무 노하우** — "이럴 때는 이렇게 해야 해", "주의할 점은..."
4. **정책/환경 변화** — "최근에 바뀌었어", "새로운 정책이..."
5. **수치/데이터** — 구체적 KPI, 벤치마크, 성과 수치

---

*Updated: 2026-02-25 (제품 중심 4폴더 구조 재편)*
