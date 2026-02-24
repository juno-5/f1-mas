# AI 영상 제작 자동화 워크플로우 설계

> 기반 자료: Sequencer Academy (14 tutorials) + NICOLA.AI Clone Workflow + Biggie AI TikTok Guide  
> 설계일: 2026-02-22

---

## 전체 구조 개요

```
[전략/기획]
    ↓
[에셋 생성] ─── 이미지 · 캐릭터 · 음성
    ↓
[영상 생성] ─── 모델 선택 · JSON 프롬프팅
    ↓
[후반 작업] ─── 음성 정규화 · 전환 · 업스케일
    ↓
[플랫폼 출력] ── 포맷 · 훅 삽입 · 배포
```

---

## Phase 1. 전략 기획

### 1-1. 콘텐츠 유형 결정

| 유형 | 목적 | 주 모델 | 예상 시간 |
|------|------|---------|---------|
| **제품 광고** | 브랜드/이커머스 | Veo 3.1 + Nano Banana Pro | 30~60분 |
| **UGC 콘텐츠** | SNS 바이럴 | Veo 3.1 + NanoBanana | 20~40분 |
| **AI 인플루언서** | 틱톡/릴스 채널 운영 | Gemini + Kling AI | 15~30분 |
| **시네마틱 쇼케이스** | 포트폴리오/고급 브랜드 | Seedance 2.0 or Veo 3.1 | 1~2시간 |
| **롱폼 애니메이션** | 유튜브/스토리 콘텐츠 | Veo 3 Loopback | 1~3시간 |

### 1-2. 스토리 구조 설계 (60초 기준 4비트)
```
Beat 1 (0~3s):   훅 — 시각적으로 불가능한 장면 or 극한 감정
Beat 2 (3~30s):  고조 — 매 샷이 이전보다 강해야 함
Beat 3 (30~50s): 피크 — 기억에 남을 가장 강렬한 이미지
Beat 4 (50~60s): 착지 — 감정 완결, 브랜드/CTA
```

### 1-3. 훅 유형 선택 (오프닝 1~3초)
```
Visual Hook  : 움직임 + 불가능한 이미지 (정지화면 ❌)
Audio Hook   : 베이스 히트 or 침묵 후 폭발
Text Hook    : 5~8단어, 0.3~0.5초 딜레이로 등장
Narrative Hook: 오픈 루프 — 결말 없는 긴장감
→ 이상적: 4가지 동시 스택
```

---

## Phase 2. 에셋 생성

### 2-1. 캐릭터/인물 이미지 생성

**도구**: Gemini (무료) / Nano Banana Pro (고품질)

```
[Gemini 프롬프트 구조]
A hyper-realistic, high-resolution photograph of [인물 묘사].
- 신체 비율 명시 (과장 금지)
- 얼굴 구조 정밀 기술 (눈 간격, 턱선, 입술 볼륨)
- 의상 + 배경 + 조명 + 카메라 각도 포함
- Ultra-photorealistic, no CGI, no stylization
```

**Sequencer 캐릭터 에셋 등록**
```
1. 캐릭터 라이브러리 → 새 캐릭터 생성
2. 레퍼런스 이미지 업로드 (정면, 단순 배경, 고해상도)
3. 상세 묘사 작성 (나이/머리색/눈색/체형/의상)
4. 프롬프트에서 @캐릭터명 으로 재사용
5. 변형: @캐릭터명:formalsuit / :angry / :rainyday
```

### 2-2. 제품 이미지 생성

**도구**: Nano Banana Pro

```
프롬프트 구조:
[제품명] in [환경/배경], [조명 묘사], [카메라 설정]
photorealistic product photography, shallow depth of field

예시:
A MacBook Air in Starlight aluminum floating among lush green fern fronds
in a misty ancient forest, soft morning light, gentle highlights on aluminum curves,
photorealistic product photography, shallow depth of field
```

**해상도 전략**: 생성 1K → 반복/수정 → 최종만 4K

### 2-3. 음성 클로닝 (선택)

**도구**: ElevenLabs / Hume AI (Sequencer Clone Voice 노드)

```
Voice Clone 프롬프트:
Clone this voice with warm, medium-deep clarity, natural micro-pauses,
clean accent, soft breathing, articulate pacing.
Preserve emotional tonality for [tutorials/business/social] speaking.
```

---

## Phase 3. 영상 생성

### 3-1. 모델 선택 기준

| 상황 | 추천 모델 | 이유 |
|------|---------|------|
| 정밀 제어 필요 (광고, 상업용) | Veo 3.1 + JSON | JSON 기반 완전 제어 |
| 멀티모달 입력 (이미지+영상+오디오) | Seedance 2.0 | 9이미지 + 3클립 + 3오디오 동시 입력 |
| 자연스러운 움직임, SNS 빠른 제작 | Kling AI | Motion Control, 텍스트 프롬프트만 |
| 댄스/모션 복제 | Kling AI Motion Control | 레퍼런스 영상 동작 복제 |
| 립싱크/말하는 영상 | PixVerse | 입 움직임 최강 |

### 3-2. JSON 프롬프트 표준 템플릿

```json
{
  "description": "전체 씬 서술 (1~2문장, 무드·페이싱·스토리)",
  "style": "Apple Keynote aesthetic / high-end product cinematography / 4K CGI",
  "camera": "slow orbital pan / smooth dolly-in / probe lens macro zoom",
  "lighting": "soft morning mist → clean studio lighting (환경별 전환 묘사)",
  "environment": "Location A → Location B → Location C",
  "elements": [
    "오브젝트1 (색상·재질 상세)",
    "오브젝트2 (색상·재질 상세)"
  ],
  "motion": "움직임 묘사 (physics-aware, 속도, 방향)",
  "text": "none / 표시할 텍스트",
  "music": "앰비언트 사운드 + 음악 + 효과음",
  "sequences": [
    {
      "sequence": 1,
      "timestamp": "00:00-00:08",
      "action": "카메라 액션 상세 묘사",
      "audio": "오디오 상세 묘사"
    }
  ]
}
```

### 3-3. 영상 유형별 실행 경로

#### 🎯 제품 광고 (Product Commercial)
```
Step 1: Nano Banana Pro → 시작 프레임 (제품 히어로샷, 1K)
Step 2: Nano Banana Pro → 종료 프레임 (브랜드 로고, 4K)
Step 3: JSON 프롬프트 작성
Step 4: Veo 3.1 Generate Video
        Start Frame → [JSON 프롬프트] → End Frame
Step 5: Export → Topaz 4K 업스케일
```

#### 📱 UGC 콘텐츠
```
Step 1: Nano Banana Pro → 제품 이미지 (중립 블러 배경)
Step 2: Nano Banana Pro → AI 크리에이터 (자연광, 홈 배경, 캐주얼)
Step 3: JSON 프롬프트 (9:16 세로, static 카메라, 자연스러운 제스처)
Step 4: Veo 3.1 → 제품=Start Frame, 크리에이터=End Frame
Step 5: 업스케일 → SNS 배포
```

#### 🕺 AI 인플루언서 (댄스/챌린지)
```
Step 1: Gemini → 캐릭터 이미지 생성
Step 2: TikTok/Reels에서 챌린지 영상 다운로드
Step 3: Kling AI Motion Control
        인물 이미지 + 모션 영상 업로드
        ※ "인물 방향 영상과 일치" = 격한 댄스 (얼굴 변형 가능)
        ※ "인물 방향 이미지와 일치" = 부드러운 움직임 (얼굴 보존)
Step 4: 반복 생성 → 최적본 선택
Step 5: 음악 + 자막 추가 → TikTok 업로드
```

#### 🎬 롱폼 / 무한 애니메이션
```
Step 1: 첫 8초 영상 생성
Step 2: Extract Image (마지막 프레임)
Step 3: 마지막 프레임 → 다음 Generate Video의 Start Frame
Step 4: 반복 (8초 × N = 무제한)
Step 5: 음성 드리프트 수정:
        Voice Clone 노드 (Source: 영상 오디오, Reference: 같은 오디오)
Step 6: Stitch 합치기 → 단일 영상 출력
```

---

## Phase 4. 후반 작업

### 4-1. 음성 정규화 (멀티샷 영상 필수)

```
노드 파이프라인:
Video → Extract Audio → Separate Vocals → LLM (Diarization) 
→ Clone Voice (Hume AI/ElevenLabs) → Mix Audio → Replace Audio

핵심: 배경음 보존 + 보컬만 교체
```

### 4-2. 클립 간 전환 (Blending)

```
Video A → [빈 샷 생성] → Video B
빈 샷: 왼쪽 링크 = Video A 마지막 프레임
       오른쪽 링크 = Video B 첫 프레임
프롬프트: "Smooth morphing transition"
전환 길이: 0.5~1초 (에너지) / 2~3초 (꿈 같은 분위기)
```

### 4-3. 4K 업스케일

```
단일 파일: Video 탭 → Topaz Video Upscale → Generate
프로젝트: Export → 완료 후 Upscale 섹션 → Topaz 선택

비용: ~$0.80/초 (Topaz)
소요: 30초 영상 → 약 2~3분
```

### 4-4. 3D VFX 리포지셔닝 (선택)

```
Image → Generate 3D (Trellis) → Render 3D (카메라 앵글 조정)
병렬: Image → Mask → Erase → Clean Plate
→ Composite (Layer 1: 배경, Layer 2: 3D 렌더)
→ Inpaint (경계 정제, "seamless blend, consistent lighting")
```

---

## Phase 5. 플랫폼 출력

### 5-1. 포맷별 스펙

| 플랫폼 | 비율 | 해상도 | 길이 | 특이사항 |
|--------|------|--------|------|---------|
| TikTok | 9:16 | 1080×1920 | 15~60초 | 첫 1초 훅 필수 |
| Instagram Reels | 9:16 | 1080×1920 | 15~90초 | 자막 필수 |
| YouTube Shorts | 9:16 | 1080×1920 | 최대 60초 | 썸네일 중요 |
| YouTube 일반 | 16:9 | 3840×2160 | 자유 | 4K 권장 |
| 광고 소재 | 16:9 / 1:1 | 4K | 15~30초 | 방송 품질 필수 |

### 5-2. 훅 삽입 체크리스트

```
✅ 오프닝 1~3초: 움직임 있는 화면 (정지 ❌)
✅ 텍스트 훅: 0.3~0.5초 딜레이 후 등장, 5~8단어
✅ 오디오: 첫 프레임과 동기화된 임팩트 사운드
✅ 약속 이행: 훅에서 한 약속은 영상에서 반드시 전달
✅ 클릭베이트 ❌ → 구체적 약속 ✅
```

---

## 자동화 우선순위 & 반복 가능 테플릿

### 🔁 일일 SNS 콘텐츠 자동화 (AI 인플루언서)
```
1. 트렌딩 챌린지 영상 모니터링 (TikTok/Reels)
2. Gemini → 캐릭터 이미지 (1회 생성 후 재사용)
3. Kling AI Motion Control (10~15분)
4. 자막/음악 추가
5. 업로드
→ 하루 1~3개 영상, 완전 자동화 가능
```

### 🛒 이커머스 제품 광고 자동화
```
1. 제품 이미지 인풋
2. Nano Banana Pro → 히어로샷 (1K)
3. JSON 프롬프트 (제품별 템플릿화)
4. Veo 3.1 생성
5. Topaz 4K 업스케일
→ 제품당 30~60분, 템플릿 재사용으로 단축
```

### 📺 롱폼 브랜드 영상 자동화
```
1. 스크립트 작성 (4비트 구조)
2. Seedance 2.0 (멀티모달: 무드보드 이미지 + 레퍼런스 클립)
3. 루프백으로 무한 확장
4. 음성 정규화 (6노드 파이프라인)
5. 전환 블렌딩
6. 4K 업스케일
→ 60초~5분 영상, 제작 1~3시간
```

---

## 도구 스택 요약

| 역할 | 1순위 | 2순위 | 비고 |
|------|-------|-------|------|
| 이미지 생성 | Nano Banana Pro | Gemini | NanoBanana = 고품질, Gemini = 무료 |
| 영상 생성 (정밀) | Veo 3.1 | Seedance 2.0 | JSON 제어 여부 |
| 영상 생성 (빠른) | Kling AI | PixVerse | Motion Control / 립싱크 |
| 음성 클로닝 | ElevenLabs | Hume AI | Sequencer 통합 |
| 업스케일 | Topaz Video | 2x Upscale | $0.80/초 vs 빠름 |
| 3D 처리 | Trellis (Sequencer) | - | 3D 메시 추출 |
| 파이프라인 | Sequencer 노드 에디터 | - | 6~10노드 연결 |

---

## 다음 단계 (Action Items)

- [ ] Sequencer 계정 세팅 + 공개 워크플로우 Fork (루프백, 음성 정규화, UGC)
- [ ] Nano Banana Pro 모델 접근 확인
- [ ] ElevenLabs 음성 라이브러리 구축 (타겟 음성 클로닝)
- [ ] 캐릭터 에셋 라이브러리 구축 (상황별 변형 포함)
- [ ] 제품 유형별 JSON 프롬프트 템플릿 라이브러리화
- [ ] Google 시트 링크 관리 연동
- [ ] 플랫폼별 배포 자동화 (TikTok, Reels, YouTube)
