# STARVERSE Memory Note Schema

> 모든 사건/관측/떡밥은 이 스키마를 따르는 노트로 기록됩니다.
> 저장 위치: `memory/notes/YYYY/YYYY-MM-DD-{SLUG}.md`

---

## 노트 스키마

```yaml
---
note_id: "{YYYY-MM-DD}_{ENTITY}_{SLUG}"
canon: "A|B|C|D"
type: "event|observation|signal|retcon"
date: "YYYY-MM-DD"

# 표면 / Frequency 이중 기록
surface_story: "(Surface에서 보이는 이야기 — 기사, 팬 반응)"
frequency_trace: "(Frequency에서 실제로 일어난 일)"

# 분류
tags: [태그1, 태그2, ...]
entities: [관련 그룹/소속사 코드]

# 연결
links:
  - type: "H|D|E|B|L|V"
    target: "대상 노드 코드"
    reason: "연결 사유"

# 상태 변화 (Mechanics 연동)
effects:
  resonance_delta: "+N 또는 -N"
  stability_delta: "+N 또는 -N"
  void_delta: "+N 또는 -N"
  link_changes:
    - link_id: "링크 ID"
      ls_delta: "+N"
      rk_delta: "+N"

# 후속
next_signals: ["다음에 주시할 떡밥/질문"]
---
```

## 노트 본문 구조

```markdown
## 요약
(1~3문장 핵심)

## 관측 (Surface)
- (기사/팬 반응/콘텐츠/SNS)

## 진실 (Frequency)
- (세계관 내부에서 실제로 일어난 일)

## 상태 변화
- (어떤 노드/링크가 어떻게 변했는지)

## 후속 떡밥
- (다음 노트로 연결될 질문 2~3개)
```

---

## Memory 3층 분류

| 층 | 이름 | type 값 | 설명 |
|----|------|---------|------|
| **Canon Memory** | 정사 기억 | `event` | 레지스트리/설정/확정 이벤트. canon A/B |
| **Episodic Memory** | 사건 로그 | `observation` | 컴백/콘서트/루머/사고/실험. canon A~C |
| **Signal Memory** | 징조/떡밥 | `signal` | 미완의 실마리. "NEXUS 2087", "DUALITY" 등. canon B~C |

---

## 파일명 규칙

```
memory/notes/
└── 2025/
    ├── 2025-01-15_ZENITH_LeapOfFaith_Stratum6.md     (event, canon A)
    ├── 2025-02-01_ECLIPSE_DualityHint_MVAnalysis.md   (signal, canon B)
    ├── 2025-02-10_STFXAKA_DawnBridge_Winter.md        (event, canon A)
    └── 2025-02-15_FANDOM_ZenEcl_CrossoverDemand.md   (observation, canon C)
```

---

## 검색/조회 기준

노트를 찾을 때 사용하는 키:
1. **entities**: 어떤 그룹/소속사가 관련?
2. **tags**: 어떤 키워드?
3. **canon**: 확정? 추정? 루머?
4. **type**: 사건? 관측? 신호?
5. **date**: 언제?
6. **links.target**: 어떤 노드와 연결?
