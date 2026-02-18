# STARVERSE — 통합 아이돌 유니버스

> *"모든 별은 같은 하늘 아래 있다. 다만 빛나는 방식이 다를 뿐."*

---

## 이 문서의 역할

이 문서는 STARVERSE 프로젝트의 **포털(진입점)**이다.

- 전체 구조를 빠르게 파악하고
- 원하는 문서로 바로 이동할 수 있도록
- 핵심 설정만 요약하고 디테일은 모듈 파일에 위임한다

---

## 핵심 설정 (1문단 요약)

STARVERSE는 우리 현실과 99% 동일한 패러렐 월드. 유일한 차이: **이 세계에서 음악은 물리적 힘을 가진다.** 세계는 Surface(현실) / Frequency(음악의 힘) / Void(침묵)의 3계층으로 구성되며, K-pop 소속사들이 (의식적/무의식적으로) Frequency의 핵심 관리자 역할을 한다. 궁극적 목표인 The Convergence는 영원히 도달하지 않는 지평선 — 그 과정에서 무한한 이야기가 탄생한다.

→ 상세: [systems/cosmology.md](systems/cosmology.md)

---

## 프로젝트 구조

```
starverse/
├── STARVERSE.md              ← 이 문서 (포털)
│
├── systems/                  # 불변 법칙 · 프레임워크
│   ├── cosmology.md          # 3계층 우주 (Surface/Frequency/Void)
│   ├── resonance-grid.md     # 노드/링크 규칙 + Grid 다이어그램
│   ├── frequency-map.md      # 2축 영역 맵 (빛↔어둠 × 질서↔자유)
│   └── crossover-tiers.md    # Tier 1~5 크로스오버 규칙
│
├── agencies.md               # 소속사 인덱스 (표 1개 + 링크)
├── agencies/                 # 소속사별 상세
│   ├── STARFALL.md
│   ├── NOVA.md
│   ├── ORBIT.md
│   ├── PULSE.md
│   ├── DREAM.md
│   ├── PHANTOM.md
│   ├── EDEN.md
│   ├── AKATSUKI.md
│   ├── JADE-STAR.md
│   └── GLOBAL-ONE.md
│
├── registry/                 # SSOT (Single Source of Truth)
│   └── groups.md             # 전체 그룹 팩트 데이터 원본
│
├── grid/                     # Resonance Grid 상세
│   ├── nodes.md              # 노드 코드 표준
│   ├── links.md              # 링크 인덱스
│   └── links/                # 링크별 상세 파일
│       └── H_STF_AKA_DAWN_BRIDGE.md
│
├── timelines/                # 연대기
│   └── global.md             # 글로벌 타임라인
│
├── events/                   # 사건 기록 (여러 노드가 참조하는 단위)
├── arcs/                     # 메타 아크
│   ├── meta_THE_CONVERGENCE.md
│   └── meta_THE_FIRST_RESONANCE.md
│
├── agents/                   # A(Agent) 레이어 — AMM
│   ├── agent-types.md        # 5종 Agent 정의
│   ├── functions-skills.md   # Functions→Skills→Abilities→Projects 계층
│   └── stats/                # 그룹별 스탯 (R/S/Vₚ)
│       ├── ZENITH.md
│       ├── ECLIPSE.md
│       └── HORIZON.md
│
├── memory/                   # M(Memory) 레이어 — AMM
│   ├── canon-policy.md       # Canon 등급 (A/B/C/D) + retcon 절차
│   ├── note-schema.md        # 노트 스키마 정의
│   └── notes/2025/           # 사건 노트
│       └── 2025-01-15_ZENITH_LeapOfFaith_Stratum6.md
│
├── mechanics/                # M(Mechanics) 레이어 — AMM
│   ├── state-values.md       # 노드/링크 상태값 정의
│   ├── update-rules.md       # 이벤트→상태 변화 규칙
│   └── event-protocol.md     # 사건 타입 사전
│
├── loops/                    # 운영 루프
│   └── operation-loop.md     # Trigger→Arc→Event→Memory→Update→Check
│
├── templates/                # 확장 템플릿
│   ├── agency.template.md
│   ├── link.template.md
│   └── event.template.md
│
├── characters/               # 캐릭터 파일
│   ├── korea/                # 한국 아이돌 + 그룹 유니버스
│   ├── japan/                # 일본
│   ├── china/                # 중국
│   ├── western/              # 서양
│   └── southeast-asia/       # 동남아
│
└── CLAUDE.md                 # 프로젝트 규칙
```

---

## 10개 소속사 요약

| 코드 | 소속사 | 지역 | Frequency 접근법 | 파일 |
|------|--------|------|-----------------|------|
| STF | STARFALL | 한국 | The Tower — 구조적 탐구 | [상세](agencies/STARFALL.md) |
| NOV | NOVA | 한국 | 감정 극대화 — 직관적 접근 | [상세](agencies/NOVA.md) |
| ORB | ORBIT | 한국 | 퍼포먼스 — 물리적 접근 | [상세](agencies/ORBIT.md) |
| PLS | PULSE | 한국 | Raw Energy — 스트릿 문화 | [상세](agencies/PULSE.md) |
| DRM | DREAM | 한국 | 순수한 꿈 — 자연적 발현 | [상세](agencies/DREAM.md) |
| PHT | PHANTOM | 한국 | 어둠과 예술 — 심미적 접근 | [상세](agencies/PHANTOM.md) |
| EDN | EDEN | 한국 | 치유와 조화 — 균형적 접근 | [상세](agencies/EDEN.md) |
| AKA | AKATSUKI | 일본 | 미학 + 사계절 리듬 | [상세](agencies/AKATSUKI.md) |
| JDS | JADE STAR | 중국 | 고대 철학 + 거대 서사 | [상세](agencies/JADE-STAR.md) |
| GOE | GLOBAL ONE | 글로벌 | 다문화 혼합 — 무경계 실험 | [상세](agencies/GLOBAL-ONE.md) |

→ 전체 그룹 목록: [registry/groups.md](registry/groups.md)

---

## AMM 레이어 요약

STARVERSE는 3개의 AMM 레이어로 운영된다:

### Agent (행동 주체)
5종 에이전트가 세계를 움직인다:
- **Group Agent** — 각 아이돌 그룹. R(공명)/S(안정)/Vₚ(Void 접근) 스탯
- **Agency Agent** — 소속사. 전략적 의사결정
- **Fandom Agent** — 팬덤. 연료 공급 (Sync/Heat/Split)
- **Member Agent** — 핵심 멤버 (선택적)
- **Phenomenon Agent** — Void/Resonance Event. 환경 변수

→ 상세: [agents/agent-types.md](agents/agent-types.md) | [agents/functions-skills.md](agents/functions-skills.md)

### Memory (기억)
3층 Memory로 세계관 정합성 유지:
- **Canon Memory** (A/B) — 확정 사실
- **Episodic Memory** (A~C) — 사건 로그
- **Signal Memory** (B~C) — 떡밥/징조

→ 상세: [memory/canon-policy.md](memory/canon-policy.md) | [memory/note-schema.md](memory/note-schema.md)

### Mechanics (규칙)
상태값과 업데이트 규칙으로 세계가 일관되게 진화:
- 노드 스탯: R / S / Vₚ / Sc / Alignment
- 링크 스탯: LS / Publicity / Risk
- 이벤트 → 상태 변화 함수

→ 상세: [mechanics/state-values.md](mechanics/state-values.md) | [mechanics/update-rules.md](mechanics/update-rules.md)

### 운영 루프
```
① Trigger 감지 → ② Arc 선택 → ③ Event 생성
→ ④ Memory 기록 → ⑤ State 업데이트 → ⑥ 정합성 검사 → ①
```

→ 상세: [loops/operation-loop.md](loops/operation-loop.md)

---

## 거버넌스 규칙 (요약)

1. **네이밍**: 그룹명은 전체 STARVERSE에서 유일
2. **SSOT**: 같은 팩트를 2곳에 쓰지 않음. 하나의 원본 + 링크
3. **이중 서사**: 모든 사건은 Surface 서사 + Frequency 진실로 분리
4. **Canon 등급**: A(확정) > B(강추정) > C(루머) > D(팬덤 신화)
5. **Convergence**: 절대 도달하지 않음. 과정이 곧 이야기

→ 상세: [memory/canon-policy.md](memory/canon-policy.md)

---

## 수치 요약

```
10개 소속사 = Resonance Grid의 10개 노드
38개 그룹   = Frequency의 38개 영역
87명 아이돌 = 별의 공명을 만드는 사람들

목표: The Convergence (영원히 도달하지 않는 지평선)
```

> *"별은 혼자 빛나지 않는다. 별과 별 사이의 빈 공간이 있기에, 각자의 빛이 의미를 가진다."*
> *— STARVERSE 공식 태그라인*
