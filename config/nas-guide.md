# NAS (Node Agent System) 사용 가이드

## 개요

NAS는 PC 노드 관리 + 회사 문서 검색 시스템입니다.
xapi 게이트웨이(`localhost:7750/nas/`)를 통해 접근합니다.

---

## 1. 노드 관리

### 노드 목록 조회
```
GET /nas/nodes
GET /nas/nodes?status=online
```

### 노드 상세 조회
```
GET /nas/nodes/{node_id}
```
응답 예시:
```json
{
  "node_id": "ojunhoui-MacBookPro.local",
  "ip_address": "192.168.51.211",
  "status": "online",
  "os_info": "Darwin 24.3.0 (arm64)",
  "cpu_percent": 20.9,
  "mem_percent": 44.4,
  "disk_percent": 4.0
}
```

### 노드에서 명령 실행
```
POST /nas/nodes/{node_id}/exec
Content-Type: application/json

{"command": "ls -la ~/Desktop", "timeout": 30}
```
응답:
```json
{
  "task_id": "a1b2c3d4",
  "stdout": "...",
  "stderr": "",
  "exit_code": 0,
  "status": "completed",
  "duration_ms": 1250
}
```

---

## 2. 문서 검색

### 문서 목록
```
GET /nas/docs
GET /nas/docs?ext=.md
GET /nas/docs?tag=config&limit=20
```

### 키워드 검색
```
GET /nas/docs/search?q=마케팅
GET /nas/docs/search?q=deploy&ext=.md
```
응답:
```json
{
  "query": "마케팅",
  "count": 12,
  "docs": [
    {
      "doc_id": "doc-0042",
      "filename": "marketing-plan.md",
      "title": "2026 마케팅 전략",
      "preview": "Q1 목표: 브랜드 인지도 30% 향상...",
      "tags": ["marketing", "plans"]
    }
  ]
}
```

### 문서 내용 읽기
```
GET /nas/docs/{doc_id}
```

### 문서 메타데이터만
```
GET /nas/docs/{doc_id}/meta
```

---

## 3. 시스템 상태

### 헬스체크
```
GET /nas/health
```

### 상세 상태 (카운터, 이벤트 타임라인)
```
GET /nas/status
```

### Prometheus 메트릭
```
GET /nas/metrics
```

---

## 엔드포인트 요약

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/nas/health` | 헬스체크 |
| GET | `/nas/status` | 상세 상태 |
| GET | `/nas/metrics` | Prometheus 메트릭 |
| GET | `/nas/nodes` | 노드 목록 |
| GET | `/nas/nodes/{id}` | 노드 상세 |
| POST | `/nas/nodes/{id}/exec` | 원격 명령 실행 |
| GET | `/nas/docs` | 문서 목록 |
| GET | `/nas/docs/search?q=` | 문서 검색 |
| GET | `/nas/docs/{id}` | 문서 내용 |
| GET | `/nas/docs/{id}/meta` | 문서 메타 |
| POST | `/nas/docs/scan` | 수동 재스캔 |

---

## 현재 등록 노드

| node_id | OS | IP |
|---------|----|----|
| ojunhoui-MacBookPro.local | Darwin 24.3.0 (arm64) | 192.168.51.211 |

## 인덱싱 범위

- `/home/mayacrew/projects/mayacrew-f1crew/` — f1crew 프로젝트 전체
- `/home/mayacrew/.f1crew/shared/` — 런타임 설정/상태 파일
- 대상 확장자: `.md`, `.txt`, `.pdf`, `.json`, `.yaml`, `.csv`
- 총 1,275개 문서 인덱싱됨
- 5분마다 자동 재스캔
