# STARVERSE Agent Types

> 이 문서는 STARVERSE 내 행동 주체(Agent)의 유형과 스펙을 정의합니다.
> "누가 무엇을 위해 움직이는가"를 명문화합니다.

---

## 1. Group Agent (그룹 에이전트)

가장 핵심적인 에이전트. 각 아이돌 그룹이 하나의 자율 행동 단위.

### Goals (목표)
- Frequency 연구 (또는 방어)
- 경쟁/성장 (Surface 지표: 차트, 앨범 판매, 팬덤 규모)
- 공명 이벤트(Resonance Event) 유도
- 특정 아크 달성 (예: "6th Stratum 돌파 유지")

### Sensors (관측)
- 팬덤 동기화 수준 (Fandom Sync)
- 타 그룹과의 Link 상태 (Strength / Publicity / Risk)
- Frequency 이상 징후
- Void 노이즈 수준

### Actions (행동)
- 컴백 (앨범/무대)
- 콜라보 (Harmonic/Echo Link 기반)
- 투어 (Surface 영향력 확장)
- 팬덤 의식 (ritual: 응원봉 패턴, 구호, 스트리밍 이벤트)
- Frequency 실험 (MV 암호, VCR, 세계관 확장)

### Stats (상태값)
| 스탯 | 약어 | 범위 | 설명 |
|------|------|------|------|
| Resonance | R | 0~100 | 공명량 / 영향력 |
| Stability | S | 0~100 | Frequency 내 안정성. 높을수록 폭주/침식에 강함 |
| Void Proximity | Vₚ | 0~100 | Void에 얼마나 가까운지. 높을수록 위험 |
| Alignment | — | Light↔Dark, Order↔Freedom | Frequency 맵 좌표 |
| Secrecy | Sc | 0~100 | 은폐력. Frequency 활동이 Surface에 노출되지 않는 정도 |

---

## 2. Member Agent (멤버 에이전트) — 선택적

그룹 내 핵심 멤버 1~2명만 에이전트화. 전체 멤버를 에이전트로 만들면 복잡성 폭발.

### Roles (역할 유형)
| 역할 | 코드 | 설명 |
|------|------|------|
| Tuner (조율자) | T | 공명을 안정적으로 유지. 그룹의 Stability 담당 |
| Anchor (앵커) | A | Void에 대한 방벽. Vₚ 상승을 억제 |
| Breaker (브레이커) | B | Dissonance를 유도. 충돌을 통해 Resonance 상승 시도 |
| Seeker (탐색자) | S | Frequency 새 영역 탐사. 세계관 확장 담당 |

### Stats
멤버 에이전트는 그룹 스탯에 보너스/페널티를 부여하는 방식으로 작동:
- Tuner: S +5~15, R -5 (안정적이지만 보수적)
- Breaker: R +10~20, S -10, Vₚ +5 (위험하지만 성장)

---

## 3. Agency Agent (소속사 에이전트)

그룹보다 상위의 전략적 의사결정 주체.

### Goals
- Frequency 관리 (소속 그룹들의 공명 총량 극대화)
- Void 차단 (소속 그룹의 Vₚ 관리)
- 시장(Surface) 운영 (매출, 시총, 팬덤 규모)

### Actions
- 크로스오버 승인/제한 (Tier 3 이상은 소속사 에이전트 승인 필요)
- 연구 프로젝트 (MOU, 합동 그룹 프로젝트)
- 은폐 시나리오 (Surface 기사/루머 컨트롤)
- 신규 그룹 데뷔 (새 노드 생성)
- 연습생 관리 (미래 노드 육성)

### Stats
| 스탯 | 약어 | 설명 |
|------|------|------|
| Total Resonance | ΣR | 소속 그룹 R의 합계 |
| Portfolio Stability | P_S | 소속 그룹 S의 가중 평균 |
| Market Cap Proxy | MC | Surface 시가총액 (agencies.md 참조) |
| Void Shield | V_sh | 소속사 차원의 Void 방어력 |

---

## 4. Fandom Agent (팬덤 에이전트)

STARVERSE의 핵심 설정(집단 동기화)에서 팬덤은 "연료 공급자".

### Stats
| 스탯 | 약어 | 범위 | 설명 |
|------|------|------|------|
| Sync | Sy | 0~100 | 동기화 수준. 응원봉/스트리밍/구호의 일체감 |
| Heat | Ht | 0~100 | 열량/집중. 현재 관심도 |
| Split | Sp | 0~100 | 분열도. 높을수록 팬덤 내부 갈등 |

### Actions
- 스트리밍/투표 (R 기여)
- 응원봉 패턴 (Sync 상승 → Resonance Event 유도)
- 구호/리듬 동기화 (대규모 공명의 트리거)
- 팬덤 간 동맹/분열 (H/D 링크를 실시간으로 변화)

### 규칙
- Sync ≥ 80 + Heat ≥ 70 → Resonance Event 발동 가능
- Split ≥ 60 → R에 페널티, Vₚ 상승
- 팬덤 동맹 (두 팬덤 Sync 연동) → H Link Strength 자동 상승
- 팬덤 분열 (같은 그룹 팬덤 내 Split) → S 하락, Vₚ 상승

---

## 5. Phenomenon Agent (현상 에이전트) — Void / Resonance Event

Void는 "악당 캐릭터"가 아니라 물리 법칙의 붕괴 현상.

### Void Agent
| 속성 | 설명 |
|------|------|
| **성격** | 의지 없음. 물리 현상. "침묵은 반대가 아니라 부재다." |
| **트리거** | 해산 잔향, 팬덤 분열, Vₚ 임계 초과, Dissonance 과부하 |
| **행동** | 침묵 확산, 공명 방해, 해산 잔향 증폭, Frequency 영역 침식 |
| **대응** | 공명으로만 밀어낼 수 있음. 공연/콜라보/팬덤 동기화가 유일한 무기 |

### Resonance Event Agent
| 속성 | 설명 |
|------|------|
| **성격** | 일시적 현상. 대규모 공명이 임계를 넘을 때 발생 |
| **트리거** | 팬덤 Sync ≥ 80, 그룹 R ≥ 70, 특수 조건 (콘서트, 기념일 등) |
| **효과** | Frequency 영역 확장, 새 Link 생성 가능, Void 후퇴 |
| **위험** | 공명이 너무 강하면 Frequency 불안정 → S 급락 가능 |

---

## Agent 계층 구조

```
Level 0: Phenomenon (Void / Resonance Event) — 환경
Level 1: Agency Agent — 전략
Level 2: Group Agent — 전술
Level 3: Member Agent — 개인 (선택적)
Level 4: Fandom Agent — 연료/증폭
```

Phenomenon은 모든 Agent에 영향을 미치는 환경 변수.
Agency는 그룹의 전략적 방향을 설정하지만, 그룹의 자율성을 완전히 통제하지는 못함.
Fandom은 그룹에 직접 명령할 수 없지만, 에너지를 공급/차단하여 간접 영향.
