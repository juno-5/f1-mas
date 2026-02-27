# Library Update Workflow

> 전사 참조 문서(Library)를 수집, 분류, 노션 페이지에 반영하는 워크플로우

---

## 폴더 구조 (4개 제품)

```
library/
├── supermembers/    # 슈퍼멤버스 (블로그 체험단)
├── superchart/      # 슈퍼차트 (인플루언서 마케팅 대행)
├── cosduck/         # 코스덕 (K-Beauty 틱톡샵)
└── commerce/        # 커머스 (자체 브랜드: HEEDA, KIMCHIP 등)
```

**규칙:**
- 모든 문서는 **제품 폴더** 기준으로 분류
- 슈퍼멤버스 문서가 다른 폴더에 들어가지 않도록 주의
- 애매한 항목(HR, 공통 등)은 확인 후 별도 폴더 생성

---

## 기록 양식

### 테이블 포맷

모든 references.md 파일은 아래 5컬럼 테이블을 사용합니다:

```markdown
| 문서명 | 링크 | 생성일 | 등록일 | 비고 |
|--------|------|--------|--------|------|
| 슈퍼멤버스 결제 프로세스 | [Notion](https://notion.so/...) | `2025-03-15` | `2026-02-25` | 결제 전체 플로우 |
| AE 리드 시트 | [GSheet](https://docs.google.com/...) | `2024-11-20` | `2026-02-25` | 리드→미팅→유료 전환율 |
```

| 컬럼 | 설명 | 예시 |
|------|------|------|
| **문서명** | 문서 제목 (간결하게) | 슈퍼멤버스 결제 프로세스 |
| **링크** | 소스 + URL `[Notion](url)` | [Notion](https://notion.so/...) |
| **생성일** | 원본 문서의 생성일 (API 자동 조회) | `2025-03-15` |
| **등록일** | 라이브러리에 추가된 날짜 | `2026-02-25` |
| **비고** | 문서 설명 (1줄) | 결제 전체 플로우 |

> **날짜 포맷**: 모든 날짜 필드는 `` `YYYY-MM-DD` `` (코드 블록)으로 감싼다.
> **생성일 자동 조회**: `scripts/fetch-creation-dates.py`로 Notion API / Google Drive API에서 일괄 조회

### 링크 소스 표기

| 소스 | 표기 | 아이콘 |
|------|------|--------|
| Notion | `[🅽 Notion](url)` | 🅽 |
| Notion DB | `[🅽 Notion DB](url)` | 🅽 |
| Google Sheets | `[Ⓖ Sheet](url)` | Ⓖ |
| Google Docs | `[Ⓖ Doc](url)` | Ⓖ |
| Google Slides | `[Ⓖ Slides](url)` | Ⓖ |
| Google Drive | `[Ⓖ Drive](url)` | Ⓖ |
| MD 변환 | `[💻 MD](url)` | 💻 |
| Slack 파일 | `[💬 Slack](url)` | 💬 |

### 업데이트 양식

문서 상태 변경 시 기존 행을 수정합니다:

```markdown
# 비공개 처리
| ~~문서명~~ | — | — | `2026-02-25` | 🔒 비공개 (매출 데이터) |

# 삭제 처리
| ~~문서명~~ | — | — | `2026-02-25` | 🗑 삭제 (오래됨/접근 불가) |

# 이동 처리
| ~~문서명~~ | — | — | `2026-02-25` | → supermembers/로 이동 |
```

### 새 문서 추가 절차

1. 해당 **제품 폴더** 확인 (supermembers / superchart / cosduck / commerce)
2. `references.md` 열기
3. 적절한 섹션의 테이블에 새 행 추가
4. **생성일**: Notion/Google API에서 조회 (없으면 `—`)
5. **등록일**에 오늘 날짜 기록 (`` `YYYY-MM-DD` `` 코드 포맷)
5. 노션 페이지 반영 (Step 4 참조)

---

## 업데이트 프로세스

### Step 1: 문서 수집 (Collect)

```bash
# ai1 서버에서 실행
ssh mayacrew@100.88.145.15
cd ~/.f1crew/scripts/mas

# Slack 채널 스캔
python3 library-scanner.py --mode=scan --limit=200

# 에이전트 워크스페이스 스캔
python3 library-scanner.py --mode=workspace

# 봇 메모리 수집
python3 library-scanner.py --mode=memory
python3 library-scanner.py --mode=memory-collect
```

### Step 2: 분류 (Classify)

```bash
python3 library-scanner.py --mode=fetch --input=scan-result.json
python3 library-scanner.py --mode=classify --input=fetched.json
```

**분류 기준:**
1. 제품명 키워드 (슈퍼멤버스, 슈퍼차트, 코스덕, HEEDA 등)
2. 채널명 패턴 (`supermembers` → 슈퍼멤버스, `cosduck-*` → 코스덕)
3. 컨텐츠 키워드 분석

### Step 3: references.md 업데이트 (Update)

- 로컬 `~/F1/f1-mas/library/{product}/references.md` 편집
- 기록 양식에 따라 등록일 포함
- 기존 내용 삭제 금지 (상태 표시로 처리)

### Step 4: 노션 페이지 반영 (Publish)

```bash
# 1. 라이브러리 → 서버 동기화
rsync -avz --include='*/' --include='*/references.md' --exclude='*' \
  ~/F1/f1-mas/library/ mayacrew@100.88.145.15:~/f1-mas/library/

# 2. 노션 페이지 업데이트
ssh mayacrew@100.88.145.15 \
  'source ~/.f1crew/credentials/.env && cd ~/f1-mas && python3 scripts/update-notion-library.py'
```

### Step 5: 피드백 반영 (Review)

| 피드백 유형 | 처리 |
|-------------|------|
| 분류 오류 | 올바른 제품 폴더로 이동 |
| 비공개 요청 | `~~제목~~` + `🔒 비공개` |
| 삭제 요청 | `~~제목~~` + `🗑 삭제` |
| 접근 불가 | `~~제목~~` + `🗑 삭제 (오래됨)` |
| 새 문서 추가 | 해당 제품 테이블에 추가 |
| 새 폴더 필요 | 사용자 확인 후 생성 |

---

## 자동화 (`/auto-library`)

Claude Code에서 자동 실행:
```
/auto-library
```

**자동 범위:** Slack 스캔 → 문서 fetch → 분류 → references.md 업데이트 → 메모리 수집
**수동 필요:** 비공개/삭제 판단, 분류 오류 수정, 노션 최종 반영

---

## 관련 파일

| 파일 | 위치 | 설명 |
|------|------|------|
| INDEX.md | `library/INDEX.md` | 라이브러리 구조 |
| library-scanner.py | `scripts/library-scanner.py` | 문서 수집 스크립트 |
| update-notion-library.py | `scripts/update-notion-library.py` | 노션 업데이트 스크립트 |

---

*Created: 2026-02-25*
