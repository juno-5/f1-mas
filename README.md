# MAS — Master Agent System

158명의 전문가 페르소나를 조율하는 오케스트레이터

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
| Creatives | 5 | `characters/creatives/` — Five Senses art directors |
| **Total** | **158** | |

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
│   ├── mas_server.py      # HTTP API (port 7720)
│   ├── mas_orchestrator.py
│   ├── mas_agent_runner.py
│   ├── mas_persona_index.py
│   ├── mas_config.py      # Config loader with hot-reload
│   ├── mas_conversation.py
│   ├── mas_templates.py
│   ├── mas_constitution.py
│   ├── mas_state.py
│   ├── mas_metrics.py
│   └── mas_slack.py
├── characters/            # 158 persona files
│   ├── INDEX.md
│   ├── developers/
│   ├── marketers/
│   ├── models/
│   └── creatives/
├── config/
│   ├── persona-registry.md   # Searchable registry
│   ├── selection-rules.md    # Selection heuristics
│   ├── task-templates.md     # Prompt templates
│   └── mas-config.json       # Runtime config (deployed to server)
├── deploy/
│   └── deploy-ai1.sh         # Deploy to ai1 server
└── systemd/
    └── mas.service            # Systemd user service
```

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
| `config/*.md` | `~/projects/mayacrew-f1crew/f1-mas/config/` |
| `systemd/mas.service` | `~/.config/systemd/user/mas.service` |

## Quick Start (Claude Code)

1. `cd ~/F1/f1-mas/`
2. Launch Claude Code — CLAUDE.md auto-loads
3. Request (e.g. "백엔드 아키텍처 리뷰해줘")
4. MAS selects optimal persona → spawns → returns result

## Dependencies

- `token-manager` (port 7700) — API key management
- `model-router` (port 7710) — Model selection
