# xapi Integration Guide — MAS

xapi 게이트웨이(`http://100.88.145.15:7750`)를 통해 MAS 관련 서비스에 접근.

## SDK 설치

```bash
pip install -e ~/F1/xapi
```

## MAS 엔드포인트

```python
from xapi.client import XAPIClient
x = XAPIClient()

# MAS 상태 (personas_loaded, uptime, version)
status = x.mas.status()

# 페르소나 목록 (필터링 가능)
all_personas = x.mas.personas()
devs = x.mas.personas(domain="developer")
kr = x.mas.personas(locale="ko-KR")

# 페르소나 검색 (dry-run selection)
results = x.mas.search("kernel")
results = x.mas.search("코드 리뷰")

# 태스크 제출
result = x.mas.request("이 코드를 리뷰해줘", persona="kernel")
result = x.mas.request("마케팅 카피 작성", persona="brand-master")

# 태스크 결과 조회
status = x.mas.request_status("req_abc123")

# 페르소나 캐릭터 상세 (토큰 효율적)
char = x.mas.character("kernel")
print(char["character_content"])
```

## Inference (LLM 직접 호출)

MAS 바이패스로 직접 LLM 호출이 필요할 때:

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
```

## Model Router

```python
# 현재 라우팅 상태 (어떤 모델로 라우팅되는지)
router = x.model_router.status()
print(router["tier_models"])
# → {"simple": "claude-opus-4-6", "medium": "...", "complex": "..."}
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
BASE="http://100.88.145.15:7750"

curl -s "$BASE/mas/status"
curl -s "$BASE/mas/personas"
curl -s "$BASE/mas/personas?domain=developer"
curl -s "$BASE/mas/personas/search?q=kernel"
curl -s -X POST "$BASE/mas/request" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"리뷰해줘","persona":"kernel"}'
curl -s "$BASE/mas/request/req_abc123"
curl -s "$BASE/mas/personas/kernel/character"
curl -s "$BASE/inference/chat" \
  -X POST -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-6","messages":[{"role":"user","content":"hello"}],"user":"mas:test","max_tokens":100}'
```

## 포트 매핑

| 기존 (직접 연결) | xapi 경유 |
|---|---|
| `localhost:7720` (MAS) | `/mas/*` |
| `localhost:7700` (Token Manager) | `/fas/*` |
| `localhost:7710` (Model Router) | `/model-router/*` |
| `localhost:18789` (Gateway) | `/inference/*` |

## TODO — 미구현 엔드포인트

xapi에 아직 프록시되지 않은 MAS 엔드포인트:

| 엔드포인트 | 설명 | 우선순위 |
|-----------|------|---------|
| `GET /mas/health` | 간단한 헬스 체크 | P3 (status로 대체 가능) |
| `GET /mas/metrics` | Prometheus 메트릭 | P2 (모니터링) |

### SDK 파라미터 참고

`x.mas.personas()` 파라미터:
- `domain` → 라우터에서 `category`로 매핑
- `function` → 라우터에서 `q`로 매핑
- `locale` → 그대로 전달
