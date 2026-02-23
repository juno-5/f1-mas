# MAS — Master Agent System

204명의 전문가 페르소나를 조율하는 오케스트레이터

## Architecture

```
User → MAS (CLAUDE.md) → Persona Selection → Task Spawn → Result Synthesis
```

| Level | Component | Description |
|-------|-----------|-------------|
| 0 | User | |
| 1 | MAS | Vanilla Claude Code orchestrator |
| 2 | Persona Agents | Character files as system prompt |
| 3 | Tool Agents | Bash, Read, Write, etc. |

## Persona Pool

| Category | Count | Directory |
|----------|-------|-----------|
| Developers | 33 | `characters/developers/` — F1 Korea (23) + Falcon Global (10) |
| Marketers | 60 | `characters/marketers/` — KR (30) + US (30) |
| Models | 60 | `characters/models/` — KR (20) + JP (10) + US (20) + EU (10) |
| Creatives | 11 | `characters/creatives/` — Five Senses (5) + Art Master Squad (6) |
| Commerce | 10 | `characters/commerce/` — E-commerce specialists |
| Sales | 10 | `characters/sales/` — Sales strategists |
| UIUX | 10 | `characters/uiux/` — UI/UX designers |
| CX | 10 | `characters/cx/` — Customer experience experts |
| **Total** | **204** | |

## Service

| Item | Value |
|------|-------|
| Port | 7720 |
| Service | `systemctl --user {start,stop,status} mas` |
| Health | `curl http://localhost:7720/health` |
| Personas | `curl http://localhost:7720/personas` |

## Directory Structure

```
f1-mas/
├── CLAUDE.md              # MAS brain (selection/spawn/synthesis protocol)
├── README.md              # This file
├── mas/                   # Python package
│   ├── mas_server.py      # HTTP API (port 7720, startup chain validation)
│   ├── mas_orchestrator.py # Multi-agent orchestration + function-priority selection
│   ├── mas_agent_runner.py # Agent execution via xapi (per-request sessions)
│   ├── mas_persona_index.py # Persona registry + function detection (regex)
│   ├── mas_config.py      # Config loader with hot-reload (30s interval)
│   ├── mas_conversation.py # Conversation state + AMM memory
│   ├── mas_templates.py   # Task prompt templates + synthesis truncation
│   ├── mas_constitution.py
│   ├── mas_state.py       # Persistent state (interrupted request recovery)
│   ├── mas_metrics.py     # Prometheus metrics (p50/p95, per-pattern)
│   ├── mas_performance.py # Performance JSONL recording
│   ├── mas_scoring.py     # Persona scoring (usage stats)
│   ├── mas_insight_capture.py # Insight auto-capture from conversations
│   └── mas_slack.py
├── org/                   # Organization structure
│   ├── functions.yaml     # Function detection patterns + persona priority
│   ├── domains.yaml       # Domain definitions
│   ├── tribes.yaml        # Tribe definitions (cross-domain teams)
│   └── squads.yaml        # Squad definitions (functional teams)
├── scripts/               # Operational scripts
│   └── cleanup-sessions.sh # Gateway session cleanup (daily cron)
├── agents/                # Slack bot agent configs (8 masters)
├── characters/            # 204 persona files
│   ├── INDEX.md
│   ├── developers/        # 33 (F1 Korea 23 + Falcon Global 10)
│   ├── marketers/         # 60 (KR 30 + US 30)
│   ├── models/            # 60 (KR 20 + JP 10 + US 20 + EU 10)
│   ├── creatives/         # 11 (Five Senses 5 + Art Master 6)
│   ├── commerce/          # 10 e-commerce specialists
│   ├── sales/             # 10 sales strategists
│   ├── uiux/              # 10 UI/UX designers
│   └── cx/                # 10 customer experience experts
├── library/               # Team knowledge base (auto-populated)
│   ├── INDEX.md           # Library master index
│   ├── CAPTURE-PROTOCOL.md # Insight capture format
│   ├── {team}/references.md  # External docs & links
│   └── {team}/insights.md    # Auto-captured from conversations
├── docs/                  # Additional documentation
│   └── MAS-Tribe-Squad-Org.md # Tribe/Squad organization guide
├── config/
│   ├── persona-registry.md   # Searchable registry
│   ├── selection-rules.md    # Selection heuristics
│   ├── task-templates.md     # Prompt templates
│   ├── tribe-registry.md     # Tribe/Squad registry
│   ├── nas-guide.md          # NAS integration guide
│   └── mas-config.json       # Runtime config (deployed to server)
├── deploy/
│   └── deploy-ai1.sh         # Deploy to ai1 server
└── systemd/
    └── mas.service            # Systemd user service (TimeoutStopSec=90)
```

## Library — Team Knowledge Base

직원 대화에서 도메인 지식을 자동 캡처하여 팀별 `insights.md`에 축적.

- 마스터 에이전트가 `[INSIGHT]...[/INSIGHT]` 블록을 응답에 태깅
- `mas_insight_capture.py`가 블록을 파싱 → `library/{domain}/insights.md`에 append
- Slack으로 전달되는 최종 응답에서는 블록 자동 제거

| Config Key | Default | Description |
|------------|---------|-------------|
| `insight_capture_enabled` | `true` | 인사이트 캡처 활성화 |
| `library_base_dir` | (characters 기준 자동) | library 폴더 절대 경로 |

## Deploy

```bash
./deploy/deploy-ai1.sh
ssh mayacrew@100.88.145.15 'systemctl --user restart mas'
```

### Server Paths

| Local | Server |
|-------|--------|
| `mas/*.py` | `~/.f1crew/scripts/mas/` |
| `config/mas-config.json` | `~/.f1crew/shared/mas-config.json` |
| `characters/` | `~/projects/mayacrew-f1crew/f1-mas/characters/` |
| `library/` | `~/projects/mayacrew-f1crew/f1-mas/library/` |
| `config/*.md` | `~/projects/mayacrew-f1crew/f1-mas/config/` |
| `org/*.yaml` | `~/.f1crew/scripts/mas/org/` |
| `scripts/*.sh` | `~/.f1crew/scripts/mas/scripts/` |
| `systemd/mas.service` | `~/.config/systemd/user/mas.service` |

## Quick Start (Claude Code)

1. `cd ~/F1/f1-mas/`
2. Launch Claude Code — CLAUDE.md auto-loads
3. Request (e.g. "백엔드 아키텍처 리뷰해줘")
4. MAS selects optimal persona → spawns → returns result

## Key Features

- **Startup chain validation**: `/inference/capacity` → Gateway + Token 가용 확인 후 서빙 시작
- **Per-request sessions**: 요청별 독립 Gateway 세션 (90%+ 토큰 비용 절감)
- **Function-priority selection**: `org/functions.yaml` regex 패턴으로 페르소나 자동 매칭
- **Tribe/Squad system**: 크로스도메인 팀 구성 + 함수별 전문가 우선순위
- **Performance tracking**: 요청별 성능 JSONL 기록 + 페르소나 스코어링
- **Session cleanup**: Gateway 세션 파일 자동 정리 (일일 cron)
- **Interrupted request recovery**: 비정상 종료 시 running 요청 → failed 복원

## Dependencies

- `xapi` (port 7750) — Unified API gateway (inference, batch, capacity)
- `f1crew-gateway` (port 18789) — FAS Gateway (token routing, session management)
- `token-manager` (port 7700) — API key management
- `model-router` (port 7710) — Model selection
- `amm-surfacer` (port 7800) — AMM memory injection (optional, graceful degradation)
