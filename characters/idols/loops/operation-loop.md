# STARVERSE Operation Loop

> 매 컴백/콘서트/시즌마다 실행하는 운영 루프. 이 루프를 따르면 세계관이 일관되게 확장됩니다.

---

## 루프 개요

```
┌─────────────────────────────────────────────────────┐
│                  STARVERSE 운영 루프                   │
│                                                       │
│  ① Trigger 감지                                      │
│       ↓                                               │
│  ② Arc 선택                                          │
│       ↓                                               │
│  ③ Event 생성                                        │
│       ↓                                               │
│  ④ Memory 기록                                       │
│       ↓                                               │
│  ⑤ State 업데이트                                    │
│       ↓                                               │
│  ⑥ 정합성 검사                                       │
│       ↓                                               │
│  (① 으로 돌아감)                                      │
└─────────────────────────────────────────────────────┘
```

---

## ① Trigger 감지

어떤 조건이 루프를 시작시키는가?

| Trigger 유형 | 조건 | 예시 |
|-------------|------|------|
| **컴백 예정** | 소속사 에이전트의 시즌 전략 | "ZENITH Q1 컴백 확정" |
| **팬덤 Sync 상승** | Fandom Sy ≥ 80 | "팬덤 총공 성공" |
| **D 링크 긴장** | D Link LS ≥ 60 + Fandom Heat ≥ 70 | "PRISM vs AURORA 팬덤 대치" |
| **Void 잔향 증가** | V Link Rk ≥ 50 또는 그룹 Vₚ ≥ 50 | "VOID 해산 잔향이 SHADOW에 영향" |
| **E 링크 수렴** | E Link LS ≥ 70 | "ZENITH × ECLIPSE 세계관 접촉" |
| **Convergence 징조** | 3개 이상 동시 Resonance Event | "전조 관측" |
| **외부 이벤트** | 시상식, 페스티벌, 기념일 | "연말 시상식 시즌" |

---

## ② Arc 선택

이번 시즌의 메인 Link 타입을 결정.

| 질문 | 선택지 |
|------|--------|
| 이번 시즌 주요 서사는? | H(협력) / D(경쟁) / E(세계관 확장) / B(글로벌) / L(계승) / V(위기) |
| 메인 그룹은? | (1~3 그룹 선택) |
| Tier는? | 1(Easter Egg) ~ 5(Convergence) |
| 리스크 수준은? | 낮음 / 중간 / 높음 / 극한 |

### Arc 선택 가이드

| 상황 | 추천 Arc |
|------|---------|
| R 높고 S 높음 → 안정기 | E(세계관 확장) 또는 B(글로벌 진출) |
| R 높고 S 낮음 → 불안정 | H(협력으로 안정화) 또는 V(위기 아크) |
| R 낮고 S 높음 → 성장 필요 | D(경쟁으로 자극) 또는 SK.01(컴백) |
| R 낮고 S 낮음 → 위기 | V(Void 아크) + H(구원 콜라보) |
| Vₚ 급상승 | V(Void 대응) 최우선 |

---

## ③ Event 생성

선택한 Arc에 따라 이벤트를 설계.

```
MV (떡밥 삽입)
  → 티저 (암호/상징)
    → 무대 (공명 발생)
      → 후일담 (잔향 기록)
```

각 이벤트는 `events/` 폴더에 `templates/event.template.md` 형식으로 생성.

### 이벤트 설계 체크리스트
- [ ] Surface 서사 (대중이 보는 이야기)는 무엇인가?
- [ ] Frequency 진실 (세계관 내부)은 무엇인가?
- [ ] 어떤 Link가 영향받는가?
- [ ] 상태 변화 예측 (R/S/Vₚ/LS/Rk delta)
- [ ] 후속 떡밥은 무엇인가?

---

## ④ Memory 기록

이벤트 결과를 Memory 노트로 저장.

1. `memory/notes/YYYY/` 에 노트 파일 생성
2. `note-schema.md` 스키마 준수
3. `surface_story`와 `frequency_trace` 분리 기록
4. `effects` 에 상태 변화 기록
5. `links` 에 관련 노드 연결
6. `next_signals` 에 후속 떡밥 기록

---

## ⑤ State 업데이트

Memory 노트의 `effects`를 기반으로 상태값 갱신.

1. 관련 그룹의 `agents/stats/{GROUP}.md` 업데이트
2. 관련 링크의 `grid/links.md` 업데이트
3. `timelines/global.md` 에 주요 이벤트 추가
4. `registry/groups.md` 에 변경 사항 반영 (필요 시)

### 업데이트 순서
```
1. Group Agent Stats (R/S/Vₚ)
2. Link Stats (LS/Pub/Rk)
3. Fandom Stats (Sy/Ht/Sp)
4. Agency Agent Stats (ΣR/P_S/V_sh)
5. Global Timeline
```

---

## ⑥ 정합성 검사

업데이트 후 거버넌스 규칙 확인.

| 검사 항목 | 규칙 | 실패 시 |
|----------|------|---------|
| 네이밍 중복 | 그룹명 전체 유일 | 이름 변경 |
| 타임라인 충돌 | 날짜/순서 일관성 | 타임라인 수정 |
| Echo 과밀 | 같은 영역 3개 이상 → E Link 필수 | Link 추가 |
| Frequency 맵 충돌 | 같은 좌표에 2개 이상 | 좌표 조정 |
| Canon 충돌 | A등급 사실 간 모순 | Retcon 절차 |
| 임계값 초과 | Vₚ ≥ 70, R ≥ 90, S ≤ 30 | 자동 트리거 확인 |

---

## 예시: ZENITH ↔ ECLIPSE Arc 루프

### ① Trigger
- ZENITH Stratum 상승 → "이중성" 관측 빈도 증가
- E_ZEN_ECL Link LS 50 도달

### ② Arc 선택
- 메인 Link: E (Echo)
- 메인 그룹: ZENITH + ECLIPSE
- Tier: 1 → 4 확장 계획
- 리스크: 높음 (두 그룹 Vₚ 동시 상승 가능)

### ③ Event 생성
- ZENITH MV에 DUALITY 암호 삽입 (Tier 1)
- ECLIPSE 앨범에 Tower 상징 삽입 (Tier 1)
- 양측 팬덤에서 연결 발견 → 화제 (Tier 2 자연 발생)
- 양사 대표 회동 → 합동 프로젝트 기획 (Tier 3 준비)

### ④ Memory 기록
- `2025-01-15_ZENITH_LeapOfFaith_Stratum6.md` 작성
- `2025-02-01_ECLIPSE_DualityHint_MVAnalysis.md` 작성

### ⑤ State 업데이트
- ZENITH: R 85, S 62, Vₚ 28
- ECLIPSE: R 78, S 71, Vₚ 22
- E_ZEN_ECL: LS 50, Rk 20

### ⑥ 정합성 검사
- Echo 과밀 확인: ZEN-ECL-HOR 3개 → E Link 필수 ✅
- 타임라인 일관성 ✅
- Vₚ 임계 미도달 (28, 22) ✅ → 계속 모니터링

---

## 루프 주기

| 주기 | 내용 |
|------|------|
| **컴백 시** | 전체 루프 1회 실행 |
| **분기(시즌)** | 자동 갱신 (시즌 Delta 적용) + 전체 정합성 검사 |
| **연말** | 연간 총정리. 모든 노드 스탯 리뷰. 다음 해 Arc 계획. |
| **특수 이벤트** | 해산/위기/Convergence 징조 시 즉시 루프 |
