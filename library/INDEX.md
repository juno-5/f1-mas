# MAS Library — Team Knowledge Base

> 각 팀의 레퍼런스 문서 + 실무 인사이트를 축적하는 지식 허브

## 제품별 라이브러리 (Primary)

| Product | Directory | 하위 구조 | 비고 |
|---------|-----------|----------|------|
| 슈퍼멤버스 | `supermembers/` | dev, marketing, sales, cx, uiux, operations, planning | 블로그 체험단 플랫폼 |
| 슈퍼차트 | `superchart/` | dev, marketing, sales, planning, cx | 인플루언서 마케팅 대행 |
| 코스덕 | `cosduck/` | dev, marketing, design, creative, planning, sales, cx | K-Beauty 틱톡샵 에이전시 |
| 커머스 | `commerce/` | heeda, kimchip, mapda, medihair | 자체 브랜드 이커머스 |

### 노션 디렉토리

[마야크루 팀별 폴더](https://www.notion.so/mayacrew/311983e32b3280788ac5c9d8ecb279d7) — 제품별로 정리된 전사 참조 문서

## 팀별 라이브러리 (에이전트 연동)

| Team | Directory | References | Insights |
|------|-----------|------------|----------|
| Developers | `developers/` | 아키텍처, API, 코딩 컨벤션 | 기술 의사결정, 트러블슈팅 노하우 |
| Marketers | `marketers/` | 플랫폼 정책, 브랜드 가이드 | 캠페인 러닝, 채널별 인사이트 |
| Creatives | `creatives/` | 크리에이티브 가이드라인, AI 도구 | 프로덕션 노하우, 프롬프트 팁 |
| Commerce | `commerce/` | 플랫폼 API, 정책 문서 | 운영 노하우, 매출 패턴 |
| Sales | `sales/` | 세일즈 방법론, CRM 가이드 | 딜 클로징 패턴, 협상 인사이트 |
| UIUX | `uiux/` | 디자인 시스템, 리서치 방법론 | 사용성 발견, 패턴 라이브러리 |
| CX | `cx/` | CS 운영 매뉴얼, SLA 기준 | VoC 트렌드, 이슈 대응 사례 |
| Models | `models/` | 촬영 가이드, 에이전시 정보 | 캐스팅 인사이트, 트렌드 |

> 팀별 디렉토리는 에이전트 시스템(마스터 봇)이 대화 중 인사이트를 자동 캡처하는 용도로 유지됩니다.
> 제품 특정 문서는 **제품별 라이브러리**에, 팀 공통 문서는 **팀별 라이브러리**에 보관합니다.

## 파일 컨벤션

각 팀 폴더는 세 파일로 구성:

- **`references.md`** — 외부 문서, 링크, 공식 가이드, 내부 SOP
- **`insights.md`** — 실제 직원 대화에서 축적된 도메인 지식 (자동 캡처)
- **`memory-insights.md`** — 봇 메모리에서 수집된 인사이트 카드 (auto-library 자동 수집)

## 인사이트 캡처 프로토콜

마스터 에이전트가 직원과 대화 중 아래 조건을 감지하면 자동으로 `insights.md`에 축적:

1. **도메인 지식 공유** — "우리는 이렇게 해", "이 플랫폼은 이렇게 작동해"
2. **의사결정 맥락** — "이걸로 결정한 이유는...", "A 대신 B를 쓰는 이유"
3. **실무 노하우** — "이럴 때는 이렇게 해야 해", "주의할 점은..."
4. **정책/환경 변화** — "최근에 바뀌었어", "새로운 정책이..."
5. **수치/데이터** — 구체적 KPI, 벤치마크, 성과 수치

### 캡처 포맷

```markdown
### [YYYY-MM-DD] 제목
- **Source**: {agent_id} × {employee_name_or_channel}
- **Context**: 대화 맥락 한 줄
- **Insight**: 핵심 인사이트 (2-3문장)
- **Tags**: #tag1 #tag2
```

---

*Created: 2026-02-23*
