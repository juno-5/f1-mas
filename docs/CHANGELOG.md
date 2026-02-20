# MAS Changelog & Insights

운영하면서 축적되는 변경사항, 발견, 인사이트를 기록합니다.

---

## 2026-02-20: Zero 응답 속도 최적화

### 문제
Zero Slack 봇 응답이 평균 31초, 최대 103초까지 걸림.

### 원인 분석
| 원인 | 영향 | 비중 |
|------|------|------|
| 세션 컨텍스트 비대 (133K tokens, 1.4MB) | 매 요청마다 전체 전송 | **주범** |
| Extended thinking = low (기본값) | 매 응답마다 thinking 오버헤드 | 높음 |
| CLAUDE.md 5KB (장황한 라우팅 테이블) | 시스템 프롬프트 비대 | 낮음 |
| memorySearch.onSessionStart = true | Ollama 콜드스타트 700ms | 낮음 |
| Stale .deleted 세션 파일 6개 | 디스크 낭비 | 미미 |
| Stale auth profiles 13개 | 설정 파일 비대 | 미미 |

### 적용한 수정
1. **세션 리셋**: 1.4MB → 0 (아카이브 후 새 세션)
2. **thinkingDefault: "off"**: `agents.defaults.thinkingDefault` (f1crew.json)
3. **memorySearch.onSessionStart: false**: 세션 시작 시 Ollama 호출 제거
4. **CLAUDE.md 최소화**: 5KB → 803B (핵심 규칙만)
5. **IDENTITY.md 설정**: Zero 정체성 명시 (Maya 자칭 방지)
6. **Stale 데이터 정리**: .deleted 6개, auth profiles 10개, usageStats 10개

### 결과
| 지표 | Before | After |
|------|--------|-------|
| 평균 응답 | 31.3s | **11.3s** |
| thinking level | low | **off** |
| 세션 토큰 | 133K | 0 (fresh) |
| CLAUDE.md | 5KB | 803B |

### 인사이트

**세션 컨텍스트가 가장 큰 성능 킬러**
- CLAUDE.md 크기는 거의 영향 없음 (5KB vs 800B = 무시 가능)
- 세션 누적이 핵심: 133K tokens → 매 요청마다 전체 API 호출에 포함
- `compaction: "safeguard"`는 200K 근처에서만 동작 → 사실상 무방비
- 장기 대책: 주기적 세션 로테이션 cron 또는 크기 감시 필요

**thinkingDefault 설정 위치**
- `agents.defaults.thinkingDefault` (O) — f1crew.json agents.defaults 아래
- `agents.list[].thinkingDefault` (X) — 개별 에이전트에는 미지원
- `agents.defaults.model.think` (X) — 미인식 키로 거부됨
- 유효 값: `off | minimal | low | medium | high | xhigh`

**Zero가 "Maya"로 자칭한 원인**
- IDENTITY.md가 비어있어서 모델이 `mayacrew` 유저명에서 유추
- 해결: IDENTITY.md에 "Zero" 명시 + CLAUDE.md 첫 줄에 정체성 선언

**f1crew.json 수정 시 주의**
- 미인식 키 → 게이트웨이 즉시 크래시 (config validation strict)
- 반드시 재시작 전에 설정 검증
- `compaction.mode` 유효값: `"safeguard"` (다른 값 테스트 필요)

---

## 2026-02-20: 에이전트 설정 SSOT 구축

### 문제
에이전트 CLAUDE.md, IDENTITY.md, f1crew.json이 서버에서만 직접 수정됨.
git 관리 없어서 변경 추적/롤백 불가.

### 구조
```
f1-mas/
├── agents/           ← 에이전트별 CLAUDE.md, IDENTITY.md
│   ├── zero/
│   ├── dev-master/
│   ├── mkt-master/
│   ├── art-master/
│   ├── commerce-master/
│   ├── sales-master/
│   ├── uiux-master/
│   └── cx-master/
├── gateway/          ← f1crew.json agents 섹션 템플릿
│   ├── f1crew.agents.json
│   └── README.md
├── characters/       ← 페르소나 파일 (기존)
├── config/           ← MAS 런타임 설정 (기존)
└── deploy/           ← 배포 스크립트 (기존)
```

### 배포 규칙
- `f1crew.json`을 통째로 SCP **금지** (Slack 토큰 유실)
- `agents` 섹션만 in-place 머지
- CLAUDE.md는 `~/.f1crew/agents/*/agent/CLAUDE.md`로 복사

---

## 2026-02-20: f1-common 패키지 생성

f1-fas/f1-mas 중복 코드를 공용 패키지로 추출.
상세: `~/F1/f1-fas/docs/incidents/RELEASE-20260220-f1common-consumption.md`

### 모듈
- `io`: load_json, save_json_atomic
- `paths`: F1CREW_ROOT, agent_auth_profiles, agent_sessions_dir
- `cost`: COST_WEIGHTS, API_PRICES, effective_tokens
- `usage/sessions`: SessionIngestor (JSONL 증분 파싱)
- `usage/gateway`: parse_gateway_log, parse_gateway_consumption_jsonl
- `vector/qdrant`: HTTP helpers (SDK 제거)

---

## Pending / TODO

- [ ] 세션 자동 로테이션 (크기 기반 또는 시간 기반)
- [ ] P0-1 배포: gateway JSONL consumption 로그 (빌드됨, 미배포)
- [ ] P0-3: sessions.json repair tool
- [ ] deploy-ai1.sh에 에이전트 설정 sync 추가
- [ ] Slack 유저 추가 시 도구 제한 (blockedTools) 설정
