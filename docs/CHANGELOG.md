# MAS Changelog & Insights

운영하면서 축적되는 변경사항, 발견, 인사이트를 기록합니다.

---

## 2026-02-23: Context Limit 방지 — Compaction 최적화

### 문제
Art Master가 "Context limit exceeded" 에러로 대화 초기화됨.
- `agent:art-master:main`: 199,216 tokens / 200,000 ctx, compactionCount=11
- `agent:art-master:openai:49fa...`: 199,716 tokens, compactionCount=1
- 원인: 도구 출력(CDP 브라우저 텍스트 등)이 무거워 20턴만으로도 200K 돌파

### 적용한 수정

**1. Compaction 튜닝 (f1crew.json)**
| 설정 | Before | After | 효과 |
|------|--------|-------|------|
| `compaction.maxHistoryShare` | 0.5 (기본) | **0.35** | 히스토리 최대 70K (200K의 35%) |
| `compaction.reserveTokensFloor` | 20000 (기본) | **25000** | 요약용 토큰 예약 확대 |
| `slack.dmHistoryLimit` | 20 | **10** | DM 턴 수 절반 축소 |
| `slack.historyLimit` | 20 | **15** | 채널 히스토리도 축소 |

**2. 세션 정리**
- art-master: main 세션 토큰 카운터 초기화 + stale openai 세션 9개 삭제
- 전 에이전트: stale openai 세션 16개 일괄 삭제

### 인사이트
- **`dmHistoryLimit: 20`은 도구 출력이 무거운 에이전트에겐 과다**: CDP text 출력 한 번에 5K~20K tokens. 10턴이면 충분
- **safeguard 모드의 `maxHistoryShare`가 핵심**: 기본 0.5 (100K tokens)는 도구 출력 무거운 경우 부족. 0.35로 낮추면 70K 한도 → overflow 전에 자동 정리
- **stale openai 세션 누적**: Gateway API 호출마다 생성되는 세션이 정리 안 됨. 주기적 cleanup 필요

---

## 2026-02-23: Chrome CDP 기반 브라우저 제어

### 변경
AppleScript JS 실행 방식에서 Chrome DevTools Protocol (CDP) 기반으로 전환.
macbookpro에 Chrome을 `--remote-debugging-port=9222`로 상시 실행 (LaunchAgent).

### 수정 파일
- `f1-nas/agent/chrome-cdp.py` — CDP 헬퍼 (navigate, text, html, eval, click, tabs, url)
- `f1-nas/agent/chrome-cdp-start.sh` — Chrome CDP 실행 스크립트
- `f1-nas/agent/com.f1crew.chrome-cdp.plist` — macOS LaunchAgent (로그인 시 자동 실행)
- `f1crew-mayacrew/src/agents/tools/nodes-tool.ts` — 도구 설명을 CDP 패턴으로 변경
- `f1-mas/agents/*/IDENTITY.md` — 8개 에이전트 모두 CDP 브라우저 제어 가이드로 교체

### 핵심 아키텍처
```
Slack 에이전트 → nodes tool (run) → NAS exec API → SSH → macbookpro
  → python3 chrome-cdp.py text/eval/navigate/click → Chrome CDP (port 9222) → DOM
```

### 브라우저 제어 전략
1. **DOM 텍스트 우선**: `text`로 페이지 내용 파악, `eval`로 JS 실행
2. **스크린샷 금지**: camera_snap, screen_record 사용 안 함
3. **SPA 대응**: JS eval + 네트워크 API 직접 호출
4. **Chrome v145+ 제약**: `--user-data-dir` 필수 → `~/.chrome-cdp` 전용 프로필 사용

### 인사이트
- **macOS SSH ↔ GUI 격리**: SSH에서 실행한 Chrome은 WindowServer 접근 불가 → LaunchAgent (gui/501) 필요
- **Chrome v145**: `--remote-debugging-port` 사용 시 `--user-data-dir` 명시 필수 (non-default)
- **`open --args` 한계**: Chrome 세션 복원 시 `--args` 플래그 무시됨 → LaunchAgent로 바이너리 직접 실행

---

## 2026-02-23: Gateway nodes 도구 → NAS 연동

### 변경
Gateway의 `nodes` 도구를 NAS (Node Agent System) HTTP API로 라우팅하도록 수정.
기존 Chrome Extension 페어링 방식 대신, NAS exec SSH를 통해 원격 PC를 직접 제어.

### 수정 파일 (f1crew-mayacrew)
- `src/agents/tools/nodes-tool.ts` — NAS HTTP 라우팅 (status/describe/run)
- `src/config/types.gateway.ts` — `GatewayNodesConfig`에 `nasUrl`, `nasApiKey` 추가
- `src/config/zod-schema.ts` — Zod 스키마에 `nasUrl`, `nasApiKey` 추가
- `src/config/schema.labels.ts`, `schema.help.ts` — 라벨/도움말 추가

### 설정 (f1crew.json)
```json
"gateway": {
  "nodes": {
    "nasUrl": "http://localhost:7730",
    "nasApiKey": "<NAS API key>"
  }
}
```

### 동작 방식
1. `nasUrl`이 설정되면 `nodes` 도구가 NAS 모드로 전환
2. `status` → `GET /nodes` (노드 목록)
3. `describe` → `GET /nodes/{id}` (노드 상세)
4. `run` → `POST /nodes/{id}/exec` (원격 명령 실행, SSH 경유)
5. `nasUrl` 미설정 시 기존 게이트웨이 페어링 방식 유지 (하위 호환)

### 테스트 결과
8개 마스터 에이전트 모두 NAS 경유 노드 제어 성공:
- zero, dev-master, mkt-master, art-master, commerce-master, sales-master, uiux-master, cx-master
- 브라우저 열기, 앱 목록 조회, 디스크 사용량 확인 등 검증 완료

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
- IDENTITY.md는 `~/.f1crew/agents/*/agent/IDENTITY.md`로 복사

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
