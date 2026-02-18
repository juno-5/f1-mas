# STARVERSE Agent Function Hierarchy

> 에이전트의 행동을 계층적으로 분류합니다.
> Functions(단발) → Skills(반복 루틴) → Abilities(상황 추론) → Projects(협업) → Agents(자율)

---

## Functions (단발 기능)

가장 작은 행동 단위. 한 번 실행하고 끝.

| ID | 이름 | 설명 | Agent |
|----|------|------|-------|
| F.01 | 티저 업로드 | 컴백 티저 공개 (Surface 노출) | Group |
| F.02 | 안무 시퀀스 실행 | 무대 퍼포먼스 1회 실행 | Group |
| F.03 | VCR 암호 삽입 | MV/VCR에 다른 그룹 상징 삽입 (Easter Egg) | Group |
| F.04 | 기사 배포 | Surface 루머/뉴스 컨트롤 | Agency |
| F.05 | 스트리밍 부스트 | 팬덤 집중 스트리밍 이벤트 | Fandom |
| F.06 | 응원봉 패턴 변경 | 콘서트 응원봉 색상/패턴 동기화 | Fandom |
| F.07 | Frequency 스캔 | 특정 영역의 이상징후 감지 | Group/Agency |
| F.08 | 연습생 평가 | 연습생 스탯 측정 | Agency |

## Skills (반복 루틴)

Functions의 조합. 정기적으로 반복 실행.

| ID | 이름 | 구성 Functions | 주기 | Agent |
|----|------|---------------|------|-------|
| SK.01 | 컴백 루틴 | F.01→F.03→F.02 (티저→암호→무대) | 시즌당 1~2회 | Group |
| SK.02 | 팬싸 루틴 | 팬미팅 + Fandom Sync 측정 | 월 1~2회 | Group+Fandom |
| SK.03 | 월드투어 운영 | 다수 F.02 + F.06 + 지역별 공명 측정 | 연 1회 | Group+Agency |
| SK.04 | 은폐 루틴 | F.04 + Frequency 흔적 소거 | 상시 | Agency |
| SK.05 | 팬덤 동원 | F.05 + F.06 + 투표 캠페인 | 컴백 시 | Fandom |

## Abilities (상황 추론 워크플로우)

예측 불가능한 상황에서 Skills를 조합하여 대응.

| ID | 이름 | 설명 | 관련 Skills |
|----|------|------|-------------|
| AB.01 | 스캔들 대응 + 공명 유지 | 멤버 논란 시 Surface 대응하면서 Frequency 안정성 유지 | SK.04 + SK.02 |
| AB.02 | 라이벌 → 콘텐츠 전환 | D 링크 긴장을 콘텐츠/이벤트로 승화 | SK.01 + F.03 |
| AB.03 | Void 이상징후 분석 후 봉합 | Vₚ 상승 감지 → 원인 분석 → 공연/콜라보로 공명 회복 | F.07 + SK.01 + SK.03 |
| AB.04 | 팬덤 분열 중재 | Split 상승 시 팬덤 내부 통합 이벤트 | SK.02 + SK.05 |
| AB.05 | 신규 그룹 데뷔 최적화 | 시장 타이밍 + Frequency 빈 영역 + 기존 Grid와의 Link 설계 | F.08 + SK.01 |

## Projects (복수 에이전트 협업)

여러 에이전트가 참여하는 대규모 이벤트. 크로스오버 Tier와 정렬.

| ID | 이름 | 참여 Agents | 크로스오버 Tier | 상태 |
|----|------|-------------|----------------|------|
| PJ.01 | DAWN BRIDGE | STARFALL + AKATSUKI + Fandom×2 | Tier 3 | 진행 중 |
| PJ.02 | Dream Garden | DREAM + EDEN + Fandom×2 | Tier 3 | 진행 중 |
| PJ.03 | JADE STAR × STARFALL MOU | JADE STAR + STARFALL | Tier 3 | 기획 중 |
| PJ.04 | Tower × Duality Arc | ZENITH + ECLIPSE + Fandom×2 | Tier 1→4 확장 중 | 진행 중 |
| PJ.05 | The Convergence | 전체 | Tier 5 | 미래 |

### Tier ↔ Project 규모 매핑
| Tier | 규모 | 최소 Agent 수 | 리스크 |
|------|------|---------------|--------|
| 1 | Easter Egg | 1 Group | 낮음 |
| 2 | Cameo | 2 Groups | 낮음 |
| 3 | Collaboration | 2+ Groups + 2+ Agencies | 중간 |
| 4 | Arc Crossover | 다수 + Fandom | 높음 |
| 5 | Convergence | 전체 | 극한 |
