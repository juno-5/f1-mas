# Gateway Agent Configuration

이 디렉토리에는 f1crew-gateway의 에이전트 설정 템플릿이 있습니다.

## 파일

- `f1crew.agents.json` — `agents` 섹션 템플릿 (f1crew.json에 머지)

## 배포

서버의 `~/.f1crew/f1crew.json`에는 Slack 토큰 등 민감정보가 포함되어 있어
직접 덮어쓰면 안 됩니다. `agents` 섹션만 선택적으로 업데이트:

```bash
# deploy/deploy-ai1.sh 에서 자동 처리됨
python3 -c "
import json
with open('$HOME/.f1crew/f1crew.json') as f: cfg = json.load(f)
with open('gateway/f1crew.agents.json') as f: agents = json.load(f)
cfg['agents'] = agents
with open('$HOME/.f1crew/f1crew.json', 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False); f.write('\n')
"
```

## 주의

- `f1crew.json`을 통째로 SCP하지 마세요 (Slack 토큰, botToken 등 유실됨)
- `agents` 섹션만 in-place 업데이트하세요
