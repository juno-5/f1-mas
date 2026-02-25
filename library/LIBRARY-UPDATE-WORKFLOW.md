# Library Update Workflow

> 전사 참조 문서(Library)를 수집, 분류, 노션 페이지에 반영하는 워크플로우

## 개요

Library는 Slack 채널, Notion, Google Drive에 흩어진 전사 문서를 **도메인별로 정리**한 지식 허브입니다.
MAS(Master Agent System)의 AI 에이전트가 대화 중 인사이트를 자동 캡처하고, Auto×Library가 주기적으로 문서를 수집·분류합니다.

### 구성 요소

| 구분 | 파일 | 설명 |
|------|------|------|
| 참조 문서 | `references.md` | 외부 문서 링크, 내부 SOP, 가이드 |
| 대화 인사이트 | `insights.md` | 마스터 에이전트가 직원 대화에서 자동 캡처 |
| 봇 메모리 인사이트 | `memory-insights.md` | 34개 에이전트 메모리에서 수집된 인사이트 카드 |
| 노션 페이지 | [Files](https://www.notion.so/mayacrew/311983e32b3280788ac5c9d8ecb279d7) | 전사 공개용 라이브러리 (references.md 기반) |

### 도메인 구조

```
library/
├── INDEX.md                    # 라이브러리 구조 정의
├── CAPTURE-PROTOCOL.md         # 인사이트 캡처 규칙
├── LIBRARY-UPDATE-WORKFLOW.md  # 이 문서
├── developers/                 # 개발팀
├── marketers/                  # 마케팅팀
├── creatives/                  # 크리에이티브팀
├── commerce/                   # 커머스팀
├── sales/                      # 세일즈팀
├── uiux/                       # UI/UX팀
├── cx/                         # CX팀
├── models/                     # 모델팀
└── supermembers/operations/    # 슈퍼멤버스 운영
```

---

## 업데이트 프로세스

### Step 1: 문서 수집 (Collect)

세 가지 소스에서 새로운 문서를 수집합니다.

#### A. Slack 히스토리 스캔
```bash
# ai1 서버에서 실행
ssh mayacrew@100.88.145.15
cd ~/.f1crew/scripts/mas

# 전체 채널 스캔 (최근 200개 메시지)
python3 library-scanner.py --mode=scan --limit=200

# 특정 채널만 스캔
python3 library-scanner.py --mode=scan --channel=C0xxx --limit=500

# 이전 스캔 이후만 (증분)
python3 library-scanner.py --mode=scan --since=1740000000
```

#### B. 에이전트 워크스페이스 스캔
```bash
# 마스터 에이전트가 생성한 문서 발견
python3 library-scanner.py --mode=workspace

# 특정 에이전트만
python3 library-scanner.py --mode=workspace --agent=dev-master

# 발견된 문서를 library로 복사
python3 library-scanner.py --mode=workspace-collect
```

#### C. 봇 메모리 스캔
```bash
# 34개 에이전트 메모리에서 인사이트 수집
python3 library-scanner.py --mode=memory

# 고품질만 (relevance >= 0.70)
python3 library-scanner.py --mode=memory --min-relevance=0.70

# 도메인별 memory-insights.md 생성
python3 library-scanner.py --mode=memory-collect
```

### Step 2: 분류 (Classify)

수집된 문서를 도메인별로 자동 분류합니다.

```bash
# 링크 문서 내용 가져오기
python3 library-scanner.py --mode=fetch --input=scan-result.json

# 도메인 분류
python3 library-scanner.py --mode=classify --input=fetched.json
```

**분류 기준 (3-tier):**
1. 채널명 기반 (`#development` → developers, `#growth` → marketers)
2. 채널명 패턴 매칭 (`cosduck-*` → commerce, `supermembers` → 제품별)
3. 컨텐츠 키워드 분석 (API, 코드 → developers / 광고, 캠페인 → marketers)

### Step 3: references.md 업데이트 (Update)

분류된 문서를 각 도메인의 `references.md`에 추가합니다.

```bash
# 자동 렌더링 (도메인별)
python3 library-scanner.py --mode=render --domain=developers --input=classified.json
```

**수동 업데이트 시 규칙:**
- 로컬 `~/F1/f1-mas/library/{domain}/references.md` 편집
- 기존 내용 절대 삭제 금지 (append only)
- 비공개 항목: `~~제목~~` + `🔒 비공개` 표시
- 삭제된 항목: `~~제목~~` + `🗑 삭제` 표시
- 오래된 항목: `~~제목~~` + `🗑 삭제 (오래됨/접근 불가)` 표시

**테이블 포맷:**
```markdown
| Resource | URL | 비고 |
|----------|-----|------|
| [문서 제목](https://notion.so/...) | Notion | 설명 |
| ~~비공개 문서~~ | — | 🔒 비공개 (사유) |
```

### Step 4: 노션 페이지 반영 (Publish)

업데이트된 references.md를 노션 Files 페이지에 반영합니다.

```bash
# 1. 라이브러리 파일을 서버에 동기화
rsync -avz --include='*/' --include='*/references.md' --exclude='*' \
  ~/F1/f1-mas/library/ mayacrew@100.88.145.15:~/f1-mas/library/

# 2. 노션 업데이트 스크립트 실행
ssh mayacrew@100.88.145.15 \
  'source ~/.f1crew/credentials/.env && cd ~/f1-mas && python3 scripts/update-notion-library.py'
```

**스크립트 동작:**
1. 기존 노션 페이지 블록 삭제
2. 8개 도메인 + 제품별 references.md 파싱
3. 비공개/삭제 표시된 항목 자동 제외
4. 노션 블록으로 변환 후 업로드

### Step 5: 피드백 반영 (Review)

팀원 피드백을 받아 수정합니다.

**피드백 유형 및 처리:**

| 유형 | 처리 방법 |
|------|----------|
| 분류 오류 | 해당 항목을 올바른 도메인 references.md로 이동 |
| 비공개 요청 | `~~제목~~` + `🔒 비공개` 표시 |
| 삭제 요청 | `~~제목~~` + `🗑 삭제` 표시 |
| 접근 불가 | `~~제목~~` + `🗑 삭제 (오래됨/접근 불가)` 표시 |
| 새 문서 추가 | 해당 도메인 references.md 테이블에 추가 |

피드백 처리 후 **Step 4**를 다시 실행하여 노션에 반영합니다.

---

## 자동화 (Auto×Library)

Claude Code의 `/auto-library` 스킬이 위 프로세스를 자동으로 수행합니다.

```
/auto-library
```

**자동화 범위:**
- Slack 채널 스캔 → 새 링크 발견
- Notion/Google Drive 문서 내용 fetch
- 도메인 자동 분류
- references.md 자동 업데이트
- 봇 메모리 인사이트 수집

**수동 필요:**
- 비공개/삭제 판단 (팀원 피드백 필요)
- 분류 오류 수정
- 노션 페이지 최종 업로드 확인

---

## 문서 관리 규칙

### 추가 기준
- Notion, Google Drive, Slack에서 공유된 업무 문서
- 팀 공통으로 참조하는 가이드, SOP, 정책 문서
- 외부 API 문서, 플랫폼 정책

### 제외 기준
- 개인 메모, 임시 파일
- 매출/비용 등 민감한 재무 데이터가 포함된 문서
- 접근 불가하거나 폐기된 문서
- 비공개 크레덴셜이 포함된 문서

### 업데이트 주기
- **자동 수집**: 주 1~2회 (Auto×Library)
- **노션 반영**: 수집 후 즉시 또는 피드백 반영 후
- **전체 리뷰**: 월 1회 (팀원 피드백 수렴)

---

## 관련 파일

| 파일 | 위치 | 설명 |
|------|------|------|
| INDEX.md | `library/INDEX.md` | 라이브러리 구조 정의 |
| CAPTURE-PROTOCOL.md | `library/CAPTURE-PROTOCOL.md` | 인사이트 캡처 규칙 |
| library-scanner.py | `scripts/library-scanner.py` | 문서 수집 스크립트 |
| update-notion-library.py | `scripts/update-notion-library.py` | 노션 페이지 업데이트 스크립트 |
| auto-library 스킬 | Claude Code `/auto-library` | 자동화 스킬 |

---

*Created: 2026-02-25*
