# Compact State

- **Time**: 2026-02-24 11:14:36
- **Trigger**: auto
- **Session**: f5e57a60-0de7-485d-a180-072c184b641f
- **CWD**: /Users/juno/F1/f1-mas
- **Transcript**: /Users/juno/.claude/projects/-Users-juno/f5e57a60-0de7-485d-a180-072c184b641f.jsonl

## Recent Activity
- ## Cycle #48 — AI 도메인 regex substring 오탐 수정
- Cycle #47에서 brand query `brand strategy against competitors performance`의 함수 오탐은 수정했지만, 도메인은 여전히 `['developers', 'marketers']`로 잘못 감지됨. "against"의 "ai" 서브스트링이 `AI` 패턴에 매칭.
- ## Cycle #49 — `training` 키워드 context-bound 수정
- Cycle #48의 AI 수정 이후, 같은 도메인 패턴의 `training`도 standalone 사용 중. "sales training program for new hires" → `domains: ['developers', 'sales']`, `functions: ['ml_training']` 오탐 확인.
- 3. 구조적 패턴: Cycle #47(performance)과 동일한 패턴 — 한국어(학습)는 단의어, 영어(training)는 다의어

*Auto-saved by pre-compact hook at 2026-02-24 11:14:36*
