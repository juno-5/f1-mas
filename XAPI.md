# xapi Integration Guide — MAS

xapi 게이트웨이(`https://xapi.so`)를 통해 MAS 관련 서비스에 접근.

## SDK 설치

```bash
pip install -e ~/F1/xapi
```

## 인증

외부 접근(`https://xapi.so`)은 API 키 필수. ai1 localhost는 인증 불필요.

```python
from xapi.client import XAPIClient
x = XAPIClient()                          # XAPI_KEY 환경변수 자동 사용
x = XAPIClient(api_key="your-key")        # 직접 전달
```

```bash
# 외부
curl -s -H "X-API-Key: $XAPI_KEY" https://xapi.so/mas/status

# ai1 로컬 (인증 불필요)
curl -s http://localhost:7750/mas/status
```

## MAS 엔드포인트 (11개)

```python
from xapi.client import XAPIClient
x = XAPIClient()

# MAS 상태 (personas_loaded, uptime, version)
status = x.mas.status()

# 페르소나 목록 (60초 캐시, 필터링 가능)
all_personas = x.mas.personas()
devs = x.mas.personas(domain="developer")
kr = x.mas.personas(locale="ko-KR")

# 페르소나 검색 (dry-run selection)
results = x.mas.search("kernel")
results = x.mas.search("코드 리뷰")

# 페르소나 캐릭터 상세 (토큰 효율적)
char = x.mas.character("kernel")
print(char["character_content"])

# 태스크 제출 (비동기 — 202 반환)
result = x.mas.request("이 코드를 리뷰해줘", personas=["kernel"])

# 태스크 제출 (동기 — 완료까지 대기)
result = x.mas.request("마케팅 카피 작성", sync=True, timeout=60)

# 태스크 결과 조회
full = x.mas.request_status("req_abc123")            # 전체 (기본)
brief = x.mas.request_status("req_abc123", format="brief")  # output 제외
raw = x.mas.request_status("req_abc123", format="raw")      # upstream 원본

# 요청 취소
x.mas.cancel("req_abc123")

# 집계 통계 (success_rate, by_pattern, cost)
stats = x.mas.stats()

# 편의 래퍼 (submit + wait)
result = x.mas.quick_request("간단한 분석해줘")
```

### 응답 필드

모든 request 결과에 포함:
- `total_cost_usd`: 에이전트 비용 합계 (FAS Gateway 사용 시 0.0)
- `agents[].cost_usd`: 개별 에이전트 비용
- `agents[].duration_ms`: 실행 시간

## Inference (LLM 직접 호출)

MAS 내부에서 에이전트 실행에 사용. MAS 바이패스로 직접 호출도 가능:

```python
# 동기 호출
response = x.inference.chat(
    messages=[{"role": "user", "content": "분석해줘"}],
    model="claude-sonnet-4-6",
    user="mas:direct",
    max_tokens=4096,
)
print(response["content"])

# 스트리밍
for line in x.inference.chat_stream(
    messages=[{"role": "user", "content": "설명해줘"}],
    model="claude-sonnet-4-6",
    user="mas:stream",
):
    print(line)
```

## FAS 토큰 관리

```python
# MAS 소비자 토큰 상태
consumer = x.fas.consumer("mas")

# 전체 토큰 풀
pool = x.fas.pool()

# 비용 확인
cost = x.fas.cost()
cost_daily = x.fas.cost("daily")
```

## Model Router

```python
# 현재 라우팅 상태 (어떤 모델로 라우팅되는지)
router = x.model_router.status()
print(router["tier_models"])
```

## Async (서비스 내부)

```python
from xapi.client import AsyncXAPIClient

async with AsyncXAPIClient() as x:
    status, personas, pool = await asyncio.gather(
        x.mas.status(),
        x.mas.personas(),
        x.fas.pool(),
    )
```

## curl 레퍼런스

```bash
BASE="https://xapi.so"

# 상태/페르소나
curl -s "$BASE/mas/status"
curl -s "$BASE/mas/personas"
curl -s "$BASE/mas/personas?domain=developer"
curl -s "$BASE/mas/personas/search?q=kernel"
curl -s "$BASE/mas/personas/kernel/character"

# 태스크 제출 (비동기)
curl -s -X POST "$BASE/mas/request" \
  -H "Content-Type: application/json" \
  -d '{"query":"리뷰해줘","personas":["kernel"]}'

# 태스크 제출 (동기 — 완료까지 대기)
curl -s -X POST "$BASE/mas/request?sync=true&timeout=60" \
  -H "Content-Type: application/json" \
  -d '{"query":"리뷰해줘","personas":["kernel"]}'

# 결과 조회 (full / brief / raw)
curl -s "$BASE/mas/request/req_abc123"
curl -s "$BASE/mas/request/req_abc123?format=brief"
curl -s "$BASE/mas/request/req_abc123?format=raw"

# 요청 취소
curl -s -X POST "$BASE/mas/cancel" \
  -H "Content-Type: application/json" \
  -d '{"request_id":"req_abc123"}'

# 통계
curl -s "$BASE/mas/stats"

# 최근 요청 목록
curl -s "$BASE/mas/requests"

# Inference (LLM 직접)
curl -s -X POST "$BASE/inference/chat" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-6","messages":[{"role":"user","content":"hello"}],"user":"mas:test","max_tokens":100}'
```

## 포트 매핑

| 기존 (직접 연결) | xapi 경유 |
|---|---|
| `localhost:7720` (MAS) | `/mas/*` (11 endpoints) |
| `localhost:7700` (Token Manager) | `/fas/*` (11 endpoints) |
| `localhost:7710` (Model Router) | `/model-router/*` |
| `localhost:18789` (Gateway) | `/inference/*` |

## MAS 내부 xapi 사용

MAS 에이전트 실행은 xapi inference 경유:
```
# 단일 에이전트
mas_agent_runner.py → POST /inference/chat → FAS Gateway

# 멀티에이전트 (배치 — 기본값)
mas_agent_runner.py → POST /inference/batch → xapi asyncio.gather → FAS Gateway (병렬)
```

- 설정: `mas-config.json`의 `xapi_url` (기본값: `http://localhost:7750`)
- 모델: `claude_model: "sonnet"` → `claude-sonnet-4-6` 자동 매핑
- user 필드: `"mas:{callsign}"` (에이전트), `"mas:synthesis"` (합성)
- 배치: `use_batch_inference: true` (기본) — 단일 HTTP 호출로 병렬 실행, 실패 시 ThreadPool 폴백
- 커넥션 풀: httpx.Client 공유 (max_connections=10, keepalive=5)
- 프로그레시브 합성: 일부 에이전트 실패해도 성공 결과만으로 합성 진행

### Batch Inference curl

```bash
# 직접 배치 호출 (MAS 바이패스)
curl -s -X POST "$BASE/inference/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"model":"claude-sonnet-4-6","messages":[{"role":"user","content":"hello"}],"user":"test:1","max_tokens":100},
      {"model":"claude-sonnet-4-6","messages":[{"role":"user","content":"world"}],"user":"test:2","max_tokens":100}
    ],
    "timeout_per_request": 120
  }'
```

### SDK 파라미터 참고

`x.mas.personas()` 파라미터:
- `domain` 또는 `category` → MAS 카테고리 필터 (단수/복수 모두 가능: `developer` = `developers`)
- `q` → 키워드 검색
- `locale` → 그대로 전달
- `tag` → 태그 필터
