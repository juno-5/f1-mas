# STARVERSE Canon Policy

> 기억의 진실도(Canon) 등급과 관리 정책을 정의합니다.

---

## Canon 등급

| 등급 | 이름 | 설명 | 수정 가능성 |
|------|------|------|-------------|
| **A** | 확정 정사 (Confirmed Canon) | 공식 발표/앨범/MV에서 확인된 사실. SSOT(registry, agencies)에 기록됨. | 수정 불가. retcon 절차 필요. |
| **B** | 강추정 (Strong Inference) | 공식 자료에서 강하게 암시되지만 명시적 확인 없음. Easter Egg, VCR 암호 등. | 조건부 수정. A로 승격 또는 C로 강등 가능. |
| **C** | 루머/이론 (Rumor/Theory) | 팬덤 분석, 미확인 소문, 인터뷰 발언의 해석. | 자유 수정. 팬덤 신화(D)로 전환 가능. |
| **D** | 비정사/팬덤 신화 (Non-Canon/Fandom Myth) | 팬덤이 만든 서사. 공식과 무관하지만 팬덤 문화의 일부. | 정사에 영향 없음. 별도 관리. |

---

## Retcon (설정 수정) 절차

### A등급 수정 (매우 드묾)
1. 수정 사유를 `events/` 에 EVT 문서로 기록
2. 영향받는 모든 문서(registry, agencies, timelines, links) 목록 작성
3. 일괄 수정 + STARVERSE.md 포털에 "Retcon Log" 추가
4. 관련 노트의 canon 등급을 `A-retconned`로 변경 (삭제하지 않음)

### B등급 → A 승격
1. 공식 자료에서 확인 시 자동 승격
2. 노트의 canon 필드를 B → A로 변경
3. registry/groups.md 등 SSOT에 반영

### B등급 → C 강등
1. 공식 자료에서 부정 시 강등
2. 노트의 canon 필드를 B → C로 변경
3. "강등 사유" 메모 추가

### C등급 → D 전환
1. 오랫동안 미확인 + 팬덤에서 독자적 서사로 발전한 경우
2. 노트의 canon 필드를 C → D로 변경

---

## Canon 관리 규칙

1. **하나의 사실은 하나의 출처에서만 (SSOT)**
   - 그룹 팩트 → registry/groups.md
   - 소속사 팩트 → agencies/*.md
   - 시스템 규칙 → systems/*.md
   - 사건 기록 → events/*.md + memory/notes/

2. **표면 서사와 Frequency 진실을 분리 저장**
   - 모든 노트에 `surface_story`와 `frequency_trace`를 구분
   - "대중은 모른다" 설정이 시스템적으로 유지됨

3. **노트 간 자동 연결**
   - 같은 `entities` 태그를 공유하는 노트는 자동으로 관련 노트
   - `links` 필드로 명시적 연결 추가 가능

4. **시간 순서 보장**
   - 노트 파일명: `YYYY-MM-DD-{SLUG}.md`
   - timelines/global.md와 일관성 유지 필수

5. **삭제 금지**
   - Canon D도 삭제하지 않음 (팬덤 문화 기록)
   - retcon된 A도 삭제하지 않고 `A-retconned` 표시
