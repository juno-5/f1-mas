# AI 퍼포먼스 마케팅 영상 제작 리서치

> 15개 튜토리얼/가이드를 분석하여 핵심 기법, 도구, 워크플로우를 정리.

---

## 1. 제작 파이프라인 전체 흐름

```
[1] 기획        → 훅 설계, 스토리 구조, 타겟 정의
[2] 에셋 준비   → 캐릭터 생성, 제품 이미지, 참조 이미지
[3] 영상 생성   → JSON 프롬프팅, I2V, 루프백 확장
[4] 후처리      → 음성 정규화, 3D 합성, 전환 효과
[5] 마감        → 4K 업스케일, 편집, 내보내기
```

---

## 2. 주요 AI 도구 & 모델

| 도구 | 용도 | 비고 |
|------|------|------|
| **Veo 3.1** | 영상 생성 (8초, JSON 프롬프트) | Google, 동기화된 오디오 지원 |
| **Seedance 2.0** | 영상 생성 (15초, 멀티모달) | ByteDance, 이미지/비디오/오디오 입력 |
| **Kling AI** | 모션 트랜스퍼, 댄스 영상 | 모션 컨트롤 / 캐릭터 정렬 모드 |
| **Nano Banana PRO** | 포토리얼 이미지 생성 | 제품 사진, 인물 생성 |
| **Topaz Video Upscale** | 4K 업스케일 | ~$0.80/초, 신경망 기반 |
| **Hume AI / ElevenLabs** | 음성 클로닝 | 음성 일관성 유지 |
| **Google Gemini** | AI 이미지 생성 + 프롬프트 작성 | 무료 티어, Gemini 3 Flash |
| **Trellis** | 이미지 → 3D 모델 변환 | 3D 재배치용 |
| **Higgsfield** | 포토리얼 인물 이미지 생성 | UGC 인플루언서 생성 |
| **Kling 3.0** | 비디오 생성 (15초, 멀티샷) | 6샷 스토리보드, Elements 3.0 레퍼런스, 네이티브 립싱크 |
| **Veed** | 토킹 아바타 애니메이션 | 음성 + 이미지 → 말하는 영상 |
| **Pletor** | AI 크리에이티브 워크플로우 플랫폼 | 노드 기반, Make/Zapier 연동, API 자동화 |
| **Sequencer** | 통합 AI 영상 제작 플랫폼 | 노드 에디터, 워크플로우 자동화 |

---

## 3. 핵심 기법 상세

### 3.1 바이럴 훅 (Viral Hooks)

**원칙**: 첫 1-2초가 모든 것을 결정한다.

**4가지 훅 유형** (모두 조합할 때 가장 효과적):

| 유형 | 핵심 | 예시 |
|------|------|------|
| Visual | 첫 프레임에서 시선 사로잡기 | 불가능한 장면, 극단적 대비 |
| Audio | 감정을 먼저 자극 | 깊은 베이스, 심장박동 |
| Text | 뇌가 처리할 것 제공 (5-8단어) | "이건 47번 시도했다" |
| Narrative | 긴장감 설정 | 카운트다운, 선택 상황 |

**효과적인 텍스트 패턴**:
- 구체적 약속: "30초 AI 영상으로 $2,400 벌었다"
- 역발상: "대부분의 AI 튜토리얼은 잘못된 방식을 가르친다"
- 미완성 루프: "이 하나의 설정이 모든 걸 바꾼다..."
- 공감 가능한 문제 제기

**피해야 할 것**: 맥락부터 시작, 정적인 오프닝, 모호한 텍스트, 클릭베이트

---

### 3.2 스토리 구조 (60초 기준)

| 구간 | 시간 | 목적 |
|------|------|------|
| Hook | 0-3초 | 시청자 주목 획득 |
| Build | 3-30초 | 강도 지속 상향 |
| Peak | 30-50초 | 기억할 최고 순간 |
| Resolution | 50-60초 | 감정적 마무리 |

**핵심**: 한 명의 캐릭터, 한 가지 변화에 집중. AI의 강점(예산/물리학 제약 없음)을 활용하여 이전에 본 적 없는 것을 보여줄 것.

---

### 3.3 캐릭터 일관성 (Consistent Characters)

**문제**: AI 모델은 각 프롬프트를 독립 처리 → 매 샷마다 다른 캐릭터 생성 (Character Drift)

**해결**: 캐릭터 에셋 시스템
1. 캐릭터 라이브러리에서 에셋 생성
2. 명확한 얼굴 참고 이미지 업로드
3. 상세 설명 (나이, 머리색, 체형, 의상)
4. 프롬프트에서 `@캐릭터이름` 태그 사용

**변형 문법**: `@maya:formalsuit`, `@derek:angry`

---

### 3.4 JSON 프롬프팅

자연어 대신 구조화된 JSON으로 영상의 모든 요소를 정밀 제어.

**기본 구조**:
```json
{
  "description": "영상의 전체 개념",
  "style": "시각 미학 (예: Apple Keynote aesthetic)",
  "camera": "카메라 움직임 (예: slow dolly in, orbital pan)",
  "lighting": "조명 변화",
  "environment": "장면/환경",
  "elements": "물체/재질 상세",
  "sequences": [
    { "timestamp": "0:00-0:02", "action": "...", "audio": "..." },
    { "timestamp": "0:02-0:05", "action": "...", "audio": "..." }
  ]
}
```

**팁**:
- 구체적으로: "신발" → "White Flyknit upper, orange midsole"
- 영화 용어 사용: dolly, macro zoom, probe lens
- 오디오까지 명시 (Veo 3.1이 동기화 음향 생성)
- 타임스탬프별 액션 시퀀싱

---

### 3.5 현실적 UGC 영상 (Realistic UGC)

**목표**: 실제 인플루언서가 촬영한 것처럼 보이는 제품 시연 영상

**워크플로우**:
1. **제품 이미지 생성** — Nano Banana PRO, 중립 배경, 자연스러운 구도
2. **콘텐츠 크리에이터 디자인** — 자연 조명, 캐주얼 의류, 친근한 표정
3. **JSON 프롬프트 작성** — 정적 카메라(삼각대), 자연 조명, 9:16 수직 포맷
4. **워크플로우 실행** — 제품 → Start Frame, 크리에이터 → End Frame

**핵심**: 과도하게 제작된 느낌 피하기. 정적 카메라 + 자연 조명 = 진정성.

---

### 3.6 제품 광고 (Product Commercials)

**4단계 워크플로우**:
1. 오프닝 프레임 (영웅 샷, 1K로 빠른 반복)
2. 엔딩 프레임 (브랜드 로고)
3. JSON 프롬프트 작성 (카메라/조명/음향/시퀀스)
4. 4K 내보내기 (최종 단계에서만 업스케일)

**프롬프팅 팁**:
- "테이블 위 노트북" → "고사리 사이에 떠있는 MacBook Air"
- 감각적 언어 (텍스처, 소리, 움직임)
- 장면 여정 맵핑

---

### 3.7 영상 확장: 루프백 기법 (Infinite Animation)

AI 모델의 시간 제한(8~15초)을 극복하는 방법.

```
영상 A 생성 → 마지막 프레임 추출 → 영상 B의 시작 프레임으로 사용 → 반복
```

- Veo 3.1 기본 8초 → 무한 확장 가능
- Voice Clone 노드로 음성 일관성 유지
- 프롬프트 일관성이 핵심

---

### 3.8 참조 이미지 → 영상 변환 (Reference Image to Video)

- Veo 3.1 Reference Image 모드
- 최대 3개 참조 이미지로 스타일/질감/환경 정의
- 이미지 순서는 무관
- Loopback으로 무제한 확장 가능

---

### 3.9 라이브 액션 블렌딩

두 실사 클립 사이에 AI 생성 전환 삽입.

```
비디오 A → [AI 전환 샷] → 비디오 B
```

- 전환 샷의 좌/우 링크 버튼으로 프레임 연결
- 지속 시간: 0.5-1초(에너지) ~ 2-3초(몽환적)
- 두 클립 간 조명/구도/움직임 방향 일치시 최적

---

### 3.10 음성 정규화 (Voice Normalization)

AI 영상의 "Voice Drift" 문제 해결.

| 단계 | 작업 |
|------|------|
| 1 | 비디오에서 오디오 추출 |
| 2 | 음성/배경음 AI 분리 |
| 3 | LLM으로 화자 식별 & 타임스탬프 분석 |
| 4 | 원본 타이밍에 맞춰 새 음성 생성 (클로닝) |
| 5 | 새 음성 + 배경음 믹싱 |
| 6 | 최종 비디오 합성 |

---

### 3.11 3D 재배치 (3D VFX Repositioning)

이미지에서 3D 모델 추출 → 임의 카메라 각도로 렌더링 → 합성.

**카메라 제어**: Theta(수평), Phi(수직), Radius(줌), FOV(원근)

---

### 3.12 4K 업스케일

- Topaz Video Upscale: 최고 품질, ~$0.80/초
- 1K에서 반복 작업 → 최종 단계에서만 4K 업스케일 (크레딧 절약)
- 깨끗한 원본 소스 필수 (압축 아티팩트 없어야)

---

### 3.13 Seedance 2.0 (ByteDance)

**특징**: 멀티모달 입력 (텍스트 + 이미지 9개 + 비디오 3개 + 오디오 3개) → 15초 영상

**강점**:
- 영화적 카메라 제어
- 물리 기반 모션 (중력, 유체 역학)
- 다중 피사체 처리
- 시간적 안정성 (조명/텍스처 일관성)

---

### 3.14 AI 댄스 영상 (모션 트랜스퍼)

**도구**: Google Gemini (이미지) + Kling AI (모션 컨트롤)

**워크플로우**:
1. Gemini로 AI 캐릭터 이미지 생성
2. Kling AI 모션 컨트롤에 캐릭터 이미지 + 참조 댄스 영상 업로드
3. 모드 선택: Motion Control(역동적) vs Character Alignment(얼굴 일관성)
4. 생성 & 내보내기

---

### 3.15 AI 클론 아바타 (NICOLA.AI 워크플로우)

> 출처: Google Docs — NICOLA.AI Full AI Clone Workflow Manual

실제 사람 없이 포토리얼 AI 아바타로 지속적 콘텐츠 생산하는 6단계 파이프라인.

| 단계 | 작업 | 도구 |
|------|------|------|
| 1. Face Creation | 포토리얼 초상 생성 | NanoBanana Pro (정체성 정확도), Flux 2.0 (시네마틱), Seedrem 4 (텍스처) |
| 2. Dataset Building | 10-20장 다양한 포즈/의상/각도/환경 이미지 생성 | 위 도구 반복 |
| 3. Upscaling | 4K-8K 해상도 업스케일 (필수) | OpenArt, Magnific, Lupa AI |
| 4. Voice Cloning | 톤, 호흡, 감정 전달까지 복제 | ElevenLabs, MathCare |
| 5. Motion Generation | 정적 이미지에 모션 부여 | VEO 3.1 (시네마틱 JSON), Kling AI (자연스러운 인체), PixVerse (입 동기화) |
| 6. Final Assembly | 비디오 + 음성 + 캡션 결합 → 일일 콘텐츠 시스템 | 편집 도구 |

**핵심**: 각 단계의 품질이 다음 단계에 직접 영향. Face Creation → Dataset → Upscale 순서가 특히 중요.

---

### 3.16 롱폼 UGC 영상 (~45초) — Pletor AI 워크플로우

> 출처: [Pletor AI](https://pletor-ai.notion.site/make-a-long-form-ugc-video-with-ai-) — Raphael Guilhem

8초짜리 원클릭 UGC가 아닌, **구조화된 워크플로우로 45초 이상의 고품질 UGC** 영상을 ~20분에 제작하는 방법.

**입력 (Context)**:
- 인플루언서 설명, 훅, 스크립트, 영상 구조, 제품 팩샷, B-roll 지시

#### Phase 1: 인플루언서 생성
| 단계 | 도구 | 작업 |
|------|------|------|
| 프롬프트 작성 | Gemini 3 Flash | 브랜드에 맞는 포토리얼 UGC 인플루언서 프롬프트 생성 |
| 이미지 생성 | Higgsfield | 인플루언서 이미지 생성 |
| 피부 보정 | Enhancor | 스킨 텍스처 개선 |

**프롬프트 가이드라인**: "Photorealistic editorial photograph..." 시작, 카메라(35mm/85mm), 조명, 텍스처, 분위기 포함. 브랜드 요소가 있으면 통합하되 과장 금지.

#### Phase 2: 토킹 아바타 프레임 (3프레임)
| 단계 | 도구 | 작업 |
|------|------|------|
| 프레임별 프롬프트 | Gemini 3 Flash | 스크립트 기반 3개 시작 이미지 프롬프트 생성 |
| 분기 | Split + List 노드 | 3개 브랜치로 워크플로우 분할 |
| 이미지 생성 | Nano Banana Pro | 제품 유/무에 따라 프레임별 비주얼 생성 |
| 음성 생성 | Claude Haiku → ElevenLabs v3 | Haiku가 감정/쉼표 지시 포함 프롬프트 작성 → ElevenLabs 음성 생성 |
| 애니메이션 | Veed | 각 프레임을 음성과 함께 애니메이션 |

**음성 대안**: ElevenLabs에서 직접 음성 클로닝 (인스타 영상 또는 AI 생성 영상에서)

**비디오 대안**:
- Veo 3.1 / Seedance 1.5 단독 → 리얼리즘 ↑, 음성 일관성 ↓
- Veo 3.1 + Sync Lipsync → 리얼리즘 + 음성 일관성 모두 확보 (얼굴 가림 주의)

#### Phase 3: B-roll (3개)
| 단계 | 도구 | 작업 |
|------|------|------|
| B-roll 프롬프트 | Gemini 3 Flash | 사용자 지시 기반 B-roll별 프롬프트 |
| 분기 | Split + List 노드 | 3개 브랜치 |
| 시작 이미지 | Nano Banana Pro | 제품 + 캐릭터 일관성 유지 이미지 |
| 비디오 프롬프트 | Gemini 3 Flash | 시네마틱 B-roll 프롬프트 (샷 스타일, 카메라 모션, 액션) |
| 애니메이션 | Kling 2.5 | 이미지 → 비디오 변환 |

**B-roll 프롬프트 구조**: Shot Style → Description + Context → Action → Camera Motion → Cinematic Qualities → Guardrails

**B-roll 핵심 규칙**:
- 스마트폰이 보이지 않도록 프롬프트에서 모호함 제거
- 프레임 간 조명/환경/모델 일관성 (같은 날 촬영 느낌)
- 텍스트 오버레이, 모션 이펙트 미포함

#### 비용/효율 비교

| 항목 | Pletor AI 워크플로우 | 전통 방식 |
|------|---------------------|-----------|
| 제작 시간 | ~20분 | 수일~수주 |
| 비용 | <$10/영상 | $2K-$50K/월 |
| 24시간 내 | 수백 개 생성 가능 | 불가 |
| API 자동화 | Make/Zapier 연동 | 불가 |

---

### 3.17 Kling 3.0 가이드 (ai.favmag)

> 출처: [Canva — ai.favmag](https://www.canva.com/design/DAHBTK0BcV0/)

Higgsfield로 생성한 AI 캐릭터를 Kling 3.0으로 애니메이션하는 워크플로우.

**파이프라인**: Higgsfield (이미지 생성) → Kling 3.0 (비디오 생성)

**Kling 3.0 핵심 기능**:

| 기능 | 설명 |
|------|------|
| **멀티 샷 & 스토리보드 3.0** | 최대 6개 샷 한 번에 생성, 샷–리버스–샷·크로스컷 자연 구현 |
| **네이티브 1080p, 최대 15초** | 3-15초 Full HD 연속 영상, 다중 플롯 가능 |
| **지속형 서브젝트 레퍼런스 (Elements 3.0)** | 이미지/영상 레퍼런스로 캐릭터 외형·아이덴티티 안정 유지 |
| **업그레이드 오디오 엔진** | 다국어 자연 립싱크, 정확한 음성 매칭 |
| **시네마틱 카메라·물리·텍스트** | 올인원 AI 디렉팅 시스템 |

**프롬프트 예시**:
```
자연스럽게 웃으면서 정면을 바라본다.
대사: "저 진짜 사람 같나요? 사실 AI예요."
```

**UGC 활용 포인트**: Elements 3.0의 지속형 레퍼런스로 캐릭터 일관성 확보 + 네이티브 립싱크로 대사 포함 영상 생성 가능.

---

## 4. 퍼포먼스 마케팅 영상 유형별 추천 파이프라인

### 4.1 UGC 스타일 제품 리뷰 (가장 전환율 높음)
```
캐릭터 에셋 → Nano Banana PRO(제품) → JSON 프롬프트(UGC) → Veo 3.1 → 음성 정규화 → 4K 업스케일
```

### 4.2 제품 시네마틱 광고
```
제품 이미지 → 오프닝/엔딩 프레임 → JSON 프롬프트(시네마틱) → Veo 3.1/Seedance 2.0 → 4K 업스케일
```

### 4.3 숏폼 소셜 콘텐츠 (Reels/TikTok)
```
바이럴 훅 설계 → 캐릭터 일관성 에셋 → 60초 4박자 구조 → 루프백 확장 → 9:16 수직 내보내기
```

### 4.4 AI 인플루언서 댄스/트렌드
```
Gemini(캐릭터) → Kling AI(모션 트랜스퍼) → 트렌딩 댄스 적용 → 수직 내보내기
```

### 4.5 AI 아바타 기반 반복 콘텐츠 (장기 운영)
```
NanoBanana/Flux(얼굴) → 20장 데이터셋 → 4K 업스케일 → ElevenLabs(음성) → VEO 3.1/Kling(모션) → 일일 콘텐츠 시스템
```

---

## 5. 소스 목록

1. [Viral Hooks](https://sequencer.media/posts/tutorials/viral-hooks)
2. [Writing Good Stories](https://sequencer.media/posts/tutorials/writing-good-stories)
3. [Consistent Characters](https://sequencer.media/posts/tutorials/consistent-characters)
4. [Video Upscaling](https://sequencer.media/posts/tutorials/video-upscaling)
5. [Real Estate Workflow](https://sequencer.media/posts/tutorials/real-estate-workflow)
6. [Blending Live Action](https://sequencer.media/posts/tutorials/blending-live-action)
7. [AI Voice Normalization](https://sequencer.media/posts/tutorials/ai-voice-normalization)
8. [3D Repositioning](https://sequencer.media/posts/tutorials/3d-repositioning)
9. [JSON Prompting](https://sequencer.media/posts/tutorials/json-prompting)
10. [Long Format 3D Animation](https://sequencer.media/posts/tutorials/long-format-3d-animation)
11. [Realistic UGC](https://sequencer.media/posts/tutorials/realistic-ugc)
12. [Reference Image to Video](https://sequencer.media/posts/tutorials/reference-image-to-video)
13. [Seedance 2.0](https://sequencer.media/posts/tutorials/seedance-2)
14. [Product Commercials](https://sequencer.media/posts/tutorials/product-commercials)
15. [AI 인플루언서 댄스 영상 가이드](https://slashpage.com/biggie-ai/qrx6zk258ezv6mv314y5) (biggie-ai)
16. [NICOLA.AI Full AI Clone Workflow](https://docs.google.com/document/d/1bseN2g2MRYqCUT2_VqEUMUylE_3DpF-syy0wlC1lF2c/) — AI 아바타 6단계 파이프라인
17. [Pletor AI — Long-form UGC](https://pletor-ai.notion.site/make-a-long-form-ugc-video-with-ai-) — 45초 UGC 제작 워크플로우
18. [Kling 3.0 Guide by ai.favmag](https://www.canva.com/design/DAHBTK0BcV0/) — Higgsfield + Kling 3.0 파이프라인
