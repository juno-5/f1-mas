# Sequencer Academy 튜토리얼 — 전체 요약 & 분석

> 출처: https://sequencer.media/posts/tutorials  
> 수집일: 2026-02-22  
> 수집 방법: Googlebot UA 프리렌더링 콘텐츠 (14개 전체 본문 완전 수집)

---

## 목차

1. [Creating Viral Hooks](#1-creating-viral-hooks)
2. [Writing Good Stories for AI](#2-writing-good-stories-for-ai)
3. [Consistent Characters](#3-consistent-characters)
4. [Upscaling Videos to 4K](#4-upscaling-videos-to-4k)
5. [Virtual Staging Pipeline](#5-virtual-staging-pipeline)
6. [Blending Live Action Clips](#6-blending-live-action-clips)
7. [AI Voice Normalization](#7-ai-voice-normalization)
8. [Repositioning with 3D VFX](#8-repositioning-with-3d-vfx)
9. [JSON Prompting for Veo 3.1](#9-json-prompting-for-veo-31)
10. [Infinite AI Animation](#10-infinite-ai-animation)
11. [Realistic UGC Videos](#11-realistic-ugc-videos)
12. [Reference Image to Video](#12-reference-image-to-video)
13. [Seedance 2.0](#13-seedance-20)
14. [Product Commercials with AI Video](#14-product-commercials-with-ai-video)
15. [전체 분석](#전체-분석)

---

## 1. Creating Viral Hooks

**URL**: `/posts/tutorials/viral-hooks`  
**태그**: Creative / Strategy  

### 핵심 주제
1초 안에 시청자를 붙잡는 훅(Hook)의 구조와 원리. 클릭베이트가 아닌 진짜 약속을 전달하는 훅을 만드는 방법.

### 4가지 훅 유형
| 유형 | 원리 |
|------|------|
| **Visual Hook** | 첫 프레임에 움직임·극한 대비·불가능한 이미지 배치. 정지 화면은 즉시 실패 |
| **Audio Hook** | 베이스 음, 시네마틱 사운드로 의식 이전에 감정 자극. 비트와 시각 컷 동기화 |
| **Text Hook** | 5~8단어. 질문을 만들어 끝까지 보게 유도. 시각 후 0.3~0.5초 뒤 등장 |
| **Narrative Hook** | 결말 없는 오픈 루프. 위기·미스터리·변화의 암시. 복잡한 플롯 불필요 |

최고 성과는 **4가지를 동시에 스택**하는 영상.

### 효과적인 텍스트 훅 패턴
- **구체적 약속**: "I made $2,400 from a 30 second AI video" (수치로 신뢰도 확보)
- **역발상**: "Most AI tutorials teach the wrong workflow" (반론 유도)
- **오픈 루프**: "This one setting changes everything..." (미완성 문장)
- **공감 문제**: 대상 고통 포인트 직접 언급

### 피해야 할 실수
- 맥락으로 시작 ("Before we get into this...") → 훅 먼저, 맥락은 나중
- 정지 화면 오프닝 → 추한 움직임이 아름다운 정지보다 효과적
- 모호한 텍스트 ("This will blow your mind") → "This technique saved me 3 hours"
- 클릭베이트 → 알고리즘 신호 악화 + 재방문 불가

### 실제 사용 예시 (훔쳐쓰기 가능)
**Visual**: "Person stepping through a mirror into another world"  
**Audio**: "Deep bass hit synced to the first visual cut"  
**Text**: "They said this was impossible."  
**Narrative**: "A countdown timer starting at 10"

---

## 2. Writing Good Stories for AI

**URL**: `/posts/tutorials/writing-good-stories`  
**태그**: Creative / AI Storytelling

### 핵심 원리
기술은 바뀌어도 스토리의 마법은 불변. "누군가를 사랑하게 만들고 → 그 사람의 삶을 매우 힘들게 만들어라."

### 단편 AI 영상의 4비트 구조 (60초 기준)

| 비트 | 시간 | 역할 | 예시 |
|------|------|------|------|
| **Beat 1: Hook** | 0~3초 | 시청 권리 획득. 불가능한 이미지, 날것의 감정 | 빌딩이 뒤집히는 도시에 서 있는 여자 |
| **Beat 2: Build** | 3~30초 | 매 샷이 이전보다 강해야 함. 강도와 색상 고조 | 중력 변하는 도시를 달리는 장면 |
| **Beat 3: Peak** | 30~50초 | 기억에 남을 가장 강렬한 이미지 | 도시가 기하학적 빛 파편으로 부서지며 허공으로 도약 |
| **Beat 4: Resolution** | 50~60초 | 감정 착지. 서두르지 말고 여운 허용 | 꽃밭에 착지, 현실 재건 |

### AI 고유 능력 활용
- **스타일 모핑**: 포토리얼 → 애니메 → 유화를 한 샷에서 전환 (기존 VFX 수억 원)
- **불가능한 카메라**: 벽 관통, 원자 → 은하 줌, 인간 불가 속도 회전
- **추상 개념의 시각화**: 슬픔=비, 불안=현실 균열, 기억=바람에 날리는 페이지

### 단편 스토리의 황금 법칙
- 캐릭터 1명 + 변화 1개 = 완성된 스토리
- 복잡한 플롯 ❌, 복잡한 실행 ✅
- 60초에 앙상블 캐스트 ❌

---

## 3. Consistent Characters

**URL**: `/posts/tutorials/consistent-characters`  
**태그**: Technical / Story Mode / Characters

### 문제: 캐릭터 드리프트
AI는 각 프롬프트를 새로 시작으로 취급 → 같은 묘사라도 매번 다른 얼굴 생성. 눈 색, 턱선, 헤어가 미묘하게 달라지면 즉시 몰입 붕괴.

### 해결: Character Assets 시스템
캐릭터를 한 번 정의하면 `@캐릭터명` 태그 하나로 재사용.

**생성 방법**:
1. 캐릭터 라이브러리 열기
2. 새 캐릭터 생성 → 이름 설정
3. 레퍼런스 이미지 업로드 (깨끗한 정면 샷, 단순 배경)
4. 상세 묘사 작성 (나이, 머리색, 눈색, 체형, 특징, 기본 의상)
5. 프롬프트에서 `@캐릭터명` 입력 → 자동 주입

### 캐릭터 변형 (Variations)
```
@maya               → 기본
@maya:formalsuit    → 정장 착용
@maya:rainyday      → 비 오는 날 (젖은 머리, 우산)
@derek:angry        → 분노한 표정
@derek:sleepdeprived → 수면 부족 상태
```
얼굴 동일, 상황만 변경.

### 핵심 팁
- 레퍼런스 이미지: 중립 표정, 단순 배경, 고해상도 정면 샷
- 일찍 테스트: 전체 시퀀스 전에 몇 샷으로 검증
- 캐릭터 묘사 수정 시 → 에셋 한 번만 수정하면 모든 샷 자동 업데이트

---

## 4. Upscaling Videos to 4K

**URL**: `/posts/tutorials/video-upscaling`  
**태그**: Technical / Quality / Export

### AI 영상 업스케일 필요성
AI 생성 영상은 기본 720p~1080p 출력 → 소셜 직접 업로드 시 흐릿하고 압축됨.

### 방법 1: 단독 파일 업스케일
1. 대시보드 Video 탭 열기
2. 모델 셀렉터에서 **Topaz Video Upscale** 선택 (최고 품질, ~$0.80/초)
3. 파일 첨부 (MP4, MOV, WebM 지원)
4. Generate 클릭 → 30초 영상 약 2~3분 소요

### 방법 2: 프로젝트 익스포트 후 업스케일
1. 프로젝트 Export 버튼 → 포맷 선택 (MP4, CapCut, Premiere 등)
2. 렌더링 완료 후 업스케일 섹션에서 모델 선택
3. 업스케일 완료 후 4K + 원본 1080p 양쪽 다운로드 가능

### 모델 선택
| 모델 | 품질 | 속도 | 비용 | 추천 용도 |
|------|------|------|------|-----------|
| **Topaz** | 최고 | 느림 | $0.80/초 | 최종 출력, 광고 |
| **2x Upscale** | 중간 | 빠름 | 저렴 | 빠른 프리뷰, SNS |

### 팁
소스 영상 품질이 낮으면 업스케일도 한계 있음. 아티팩트가 심한 원본은 복구 불가.

---

## 5. Virtual Staging Pipeline

**URL**: `/posts/tutorials/real-estate-workflow`  
**태그**: Workflow / Real Estate / Advanced

### 문제
기존 가상 스테이징: 3D 아티스트 고용 → 모델링 → 렌더링 → 합성 (비싸고 느림)

### Sequencer 노드 파이프라인
```
Input Video → Extract Frames → Generate (per frame) → Stitch → Output
```

**4개 노드 연결:**

| 노드 | 역할 |
|------|------|
| Input Video | 빈 방 영상 입력 |
| Extract Frames | 키 프레임 추출 (10초 영상 → 3~5프레임) |
| Generate Video | 각 프레임을 스테이징 스타일로 변환 |
| Stitch | 모든 클립 합쳐 완성 영상 출력 |

### 스테이징 프롬프트 예시
```
Modern mid-century living room, beige sofa, sunlight streaming through windows, 
4k, interior design magazine style, wide angle
```

### 전문가 팁
- 촬영: 흔들림 없고 조명 균일한 빈 방 영상
- 모든 프레임에 동일 프롬프트 → 가구/색상 일관성 유지
- 완성된 워크플로우를 템플릿 저장 → 매 건물마다 재사용

---

## 6. Blending Live Action Clips

**URL**: `/posts/tutorials/blending-live-action`  
**태그**: Technical / Story Mode / Video

### 개념
두 실사 영상 사이에 AI가 중간 영상을 생성해 seamless 전환 구현.

```
Video A → [AI 생성 Transition] → Video B
```

### 3샷 셋업 방법
1. Video A 추가 (Shot Card)
2. `+ Add Shot` 으로 빈 샷 삽입
3. Video B 추가
4. 빈 샷의 **왼쪽 링크 버튼** → Video A 마지막 프레임 연결
5. **오른쪽 링크 버튼** → Video B 첫 프레임 연결
6. 전환 프롬프트 입력: "Smooth morphing transition" 또는 "Camera push in, seamless blend"
7. Video 버튼 클릭 → 생성

### 전환 길이 가이드
- **0.5~1초**: 에너지 넘치는 컷
- **2~3초**: 꿈 같은, 초현실적 전환

### 팁
두 클립이 시각적으로 비슷할수록(조명, 구도, 움직임 방향) 전환 품질 향상.

---

## 7. AI Voice Normalization

**URL**: `/posts/tutorials/ai-voice-normalization`  
**태그**: Workflow / Audio / Advanced

### 문제
AI 영상 멀티샷 → 같은 캐릭터지만 샷마다 목소리 톤·피치 달라짐 (Voice Drift)

### 6노드 파이프라인
```
Video → Extract Audio → Separate Vocals → LLM (Diarization) → Clone Voice → Mix Audio → Replace Audio
```

**각 노드 역할:**

1. **Extract Audio**: 영상에서 오디오 트랙 분리
2. **Separate Audio**: AI로 보컬과 배경음 분리 (배경음은 보존)
3. **Generate Text (LLM)**: Diarization 프롬프트로 화자·타임스탬프·대화 JSON 생성
4. **Clone Voice**: 화자 JSON + 보컬 + 타겟 음성 모델 → 새 음성 생성
5. **Mix Audio**: 새 AI 보컬 + 원본 배경음 믹싱
6. **Replace Audio**: 원본 영상에 믹싱된 오디오 교체

### Diarization 프롬프트 (LLM 노드용)
```
You are a specialized Audio Diarization Engine for AI video processing.
Context: AI-generated videos often exhibit "voice drift"...
Goal: Construct a precise script JSON with Speaker IDs, timestamps, dialogue.
Output schema: {"speakers": [...], "segments": [{speaker_id, start_time, end_time, text}]}
```

### 지원 음성 모델
- **Hume AI**
- **ElevenLabs**

### 팁
배경 음악이 강하면 보컬 분리 품질 저하. 조용한 배경에서 촬영한 소스가 최적.

---

## 8. Repositioning with 3D VFX

**URL**: `/posts/tutorials/3d-repositioning`  
**태그**: Workflow / VFX / Advanced

### 기존 편집의 한계
자르기, 크기 조절, 왜곡만 가능 → **공간적 제어 불가**

### 6노드 파이프라인 (2개 병렬 트랙)
```
트랙 1 (피사체): Image → Generate 3D → Render 3D → [Composite]
트랙 2 (배경):   Image → Mask → Erase → Clean Plate → [Composite]
```

**각 단계:**

**Step 1 - 3D 모델 추출**
- Image 노드 → Generate 3D 노드 (Trellis 모델)
- 단순 배경, 뚜렷한 피사체일수록 정확도 향상

**Step 2 - 카메라 앵글 재설정 (Render 3D)**
| 컨트롤 | 기능 |
|--------|------|
| Theta | 수평 회전 (좌우 궤도) |
| Phi | 수직 각도 (상하 궤도) |
| Radius | 거리 (줌) |
| FOV | 원근 왜곡 (낮을수록 망원, 높을수록 광각) |

**Step 3 - 클린 플레이트 생성**
- Mask 노드로 피사체 마스킹 → Erase 노드로 제거 → AI가 배경 복원

**Step 4 - 합성**
- Composite 노드: Layer 1 (배경) + Layer 2 (3D 렌더)
- 위치·크기·회전 자유 조정

**Step 5 (선택) - AI 정제**
- Inpaint 노드로 경계 엣지 부드럽게: "seamless blend, consistent lighting"

### 팁
조명 방향 맞추기가 핵심. 배경 빛과 3D 렌더 조명 방향 불일치 → 즉시 가짜 티남.

---

## 9. JSON Prompting for Veo 3.1

**URL**: `/posts/tutorials/json-prompting`  
**태그**: Technical / Prompting / Advanced

### Veo 3.1 기본 프롬프트 공식
```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
```

### JSON 프롬프팅이란?
자연어 단락 대신 키-값 쌍으로 각 요소를 개별 정의 → 정밀 제어.

### JSON 구조
```json
{
  "description": "전체 씬 서술",
  "style": "시각적 미학 (4K, CGI, 매크로 등)",
  "camera": "카메라 무브먼트 (dolly, probe lens, no cuts 등)",
  "lighting": "조명 묘사",
  "environment": "환경 전환 경로 (A → B → C)",
  "elements": ["요소1 (색상·재질 포함)", "요소2"],
  "motion": "움직임 묘사",
  "music": "사운드 디자인",
  "sequences": [
    {
      "sequence": 1,
      "timestamp": "00:00-00:08",
      "action": "카메라 액션 상세",
      "audio": "오디오 상세"
    }
  ]
}
```

### 사례: Nike Vaporfly 광고
신발 내부 무한 매크로 줌 (기존엔 probe lens + CGI 필요) → JSON 프롬프트 하나로 구현.

### 베스트 프랙티스
- **구체적 묘사**: "Nike Vaporfly 3 (White Flyknit upper, orange midsole)" — "a shoe" ❌
- **오디오 명시**: 앰비언트·음악·효과음까지 Veo 3.1이 동기 생성
- **시네마 용어**: "dolly", "probe lens", "macro zoom", "no cuts"
- **환경 전환 명시**: "Studio → Microscopic World → Concrete Wall"

---

## 10. Infinite AI Animation

**URL**: `/posts/tutorials/long-format-3d-animation`  
**태그**: Workflow / Infinite / Loopback

### 문제
Veo 3 = 8초 한계. Kling/기타 = 5초. 스토리는 8초에 끝나지 않음.

### 루프백(Loopback) 기법
```
Video A 마지막 프레임 → Video B의 Start Frame 입력
```
→ AI가 정확히 이어서 시작 → 8초 + 8초 + 8초... = 무한 확장

### 오디오 드리프트 문제 해결
같은 프롬프트라도 각 영상의 목소리가 미세하게 달라짐 → 몰입 파괴.

**해결: Voice Clone 노드 자기 참조**
```
Audio Track → Voice Clone (Input A: Source)
Audio Track → Voice Clone (Input B: Reference)  ← 같은 트랙을 양쪽에 연결
```
→ 모델이 음성을 안정화시켜 클립 간 편차 제거.

**최종 파이프라인**: 여러 영상 생성 → 각 루프백 연결 → 음성 정규화 → Stitch 합치기

---

## 11. Realistic UGC Videos

**URL**: `/posts/tutorials/realistic-ugc`  
**태그**: Workflow / UGC / Advanced

### 개념
AI 인플루언서가 실제 제품을 리뷰하는 영상 — 촬영 없이.

### 4단계 워크플로우

**Step 1: 제품 이미지 생성**
- Nano Banana PRO 사용 (깨끗한 배경, 자연스러운 블러)
- Veo가 인플루언서 손에 자연스럽게 합성

**Step 2: AI 크리에이터 생성**
- Nano Banana PRO로 포토리얼리스틱 인물 생성
- 필수 요소: 자연광, 홈 배경, 캐주얼 의상, 친근한 표정, 중간 클로즈업

**Step 3: JSON 프롬프트 작성**
```json
{
  "style": "Social media influencer style, 9:16 vertical aspect ratio",
  "camera": "Static tripod shot, eye-level, medium close-up",
  "sequences": [{
    "timestamp": "00:00-00:07",
    "action": "인플루언서 제품 들고 → 테스트 → 카메라에 설명",
    "audio": "Female voice + tapping sound + pump sound"
  }]
}
```

**Step 4: 워크플로우 연결**
- 제품 이미지 → Start Frame
- 크리에이터 이미지 → End Frame
- Veo 3.1, 8초, JSON 프롬프트 연결

### UGC 핵심 원칙
- 정적 카메라 (삼각대 느낌)
- 9:16 세로 포맷 필수
- 자연스러운 조명 조건 일치 (크리에이터 ↔ 제품)

---

## 12. Reference Image to Video

**URL**: `/posts/tutorials/reference-image-to-video`  
**태그**: Workflow / Video / Advanced

### 개념
최대 3개의 레퍼런스 이미지 → Veo 3.1이 스타일·재질·구도 학습 → 시네마틱 영상 생성

### 3단계 워크플로우

**Step 1**: Image 노드 3개 (드래그 앤 드롭) → 자동 Image 노드 생성

**Step 2**: Generate Video 노드
- 모델: Veo 3.1
- 모드: **Reference Images** (레퍼런스 입력 슬롯 3개 활성화)
- 각 Image 노드 → Reference Image 1/2/3 연결

**Step 3**: Text 노드로 프롬프트 연결 → Duration·Aspect Ratio 설정 → Run

### 루프백으로 무한 확장
```
생성된 영상 → Extract Image (마지막 프레임) → 새 Generate Video의 Reference Image
→ Stitch 합치기
```

### 팁
- 3개 이미지가 일관된 스타일(조명·색조·미학)을 공유할수록 결과 품질 향상
- 첫 프레임을 다른 프롬프트의 레퍼런스로 재사용 → 같은 DNA의 영상 패밀리 제작

---

## 13. Seedance 2.0

**URL**: `/posts/tutorials/seedance-2`  
**태그**: New Model / Video / AI

### 스펙
| 항목 | 값 |
|------|-----|
| 최대 길이 | 15초 |
| 이미지 입력 | 최대 9개 |
| 비디오 입력 | 최대 3클립 |
| 오디오 입력 | 최대 3클립 |
| 오디오 출력 | 동기화 |
| 개발사 | ByteDance |

### 핵심 기능 4가지
1. **시네마틱 카메라 제어**: 패닝, 트래킹, 컨트롤드 리빌. 카메라 로직 이해
2. **Temporal Stability**: 조명·텍스처·공간 관계가 클립 전체에서 일관성 유지
3. **멀티 피사체**: 여러 캐릭터/오브젝트 동시 상호작용 (아이덴티티 유지)
4. **물리 인식 모션**: 중력, 모멘텀, 유체 역학 정확 구현

### 멀티모달 입력 (경쟁 모델 대비 최대 강점)
```
텍스트 + 이미지(최대 9) + 비디오(최대 3) + 오디오(최대 3) → 단일 생성
```
영화 감독처럼 레퍼런스 푸티지·무드보드·사운드 디자인 함께 제공.

### 경쟁 모델 비교
Sora 2, Veo 3.1, Movie Gen 대비 **멀티모달 입력**이 핵심 차별점.

### 프롬프팅 팁
- 카메라 무브먼트 명시: "slow dolly-in, orbiting 45° clockwise, shallow DOF"
- 물리 현상 명시: "water droplets with realistic refraction", "fabric billowing"
- 멀티 피사체: 각 피사체 외형과 액션 분리 기술 후 상호작용 묘사

### 활용 사례
- 제품 광고 (물리 정확 매크로 촬영)
- 시네마틱 씬 생성 (멀티 캐릭터)
- 소셜 콘텐츠 대량 제작
- 스토리보드 → 영상 변환

---

## 14. Product Commercials with AI Video

**URL**: `/posts/tutorials/product-commercials`  
**태그**: Workflow / Video / Advanced

### 공식
```
시작 프레임 (제품 히어로샷) + JSON 프롬프트 + 종료 프레임 (브랜드 로고)
→ AI가 두 앵커 사이를 시네마틱하게 채움
```

### 3단계 워크플로우

**Step 1: 시작 프레임 생성**
- Image Editor → Nano Banana Pro 모델
- 1K 해상도로 빠른 반복 작업
- 예시 프롬프트: "A MacBook Air in Starlight aluminum floating among lush green fern fronds in a misty ancient forest..."

**Step 2: 종료 프레임 생성**
- 브랜드 로고를 시각적으로 연결된 환경에 배치
- 환경 연속성 예시: 숲 배경 제품 → 열대 섬 위의 로고
- 종료 프레임은 4K로 올려서 익스포트

**Step 3: JSON 프롬프트 작성**
```json
{
  "description": "고수준 내러티브 (1~2문장)",
  "style": "Apple Keynote aesthetic / high-end product cinematography",
  "camera": "slow orbital pan / smooth accelerated push-in",
  "lighting": "soft morning mist → clean studio lighting",
  "environment": "Misty Ancient Forest → Clean Interior → Tropical Island",
  "elements": ["Starlight Aluminum MacBook Air", "Matte black silicon"],
  "sequences": [
    {
      "timestamp": "00:00-00:04",
      "action": "카메라 액션",
      "audio": "사운드 디자인"
    }
  ]
}
```

### 1K → 4K 파이프라인
생성은 1K (빠른 반복) → 최종 익스포트 시 Topaz 업스케일 → 4K 방송용

---

## 전체 분석

### 카테고리 분포

| 카테고리 | 수 | 튜토리얼 |
|---------|---|---------|
| Workflow (파이프라인 구축) | 7 | 제품 광고, 레퍼런스→영상, UGC, 인피니트 애니, 3D VFX, 음성 정규화, 부동산 스테이징 |
| Technical (도구·기술) | 4 | JSON 프롬프팅, 라이브액션 블렌딩, 업스케일링, 일관 캐릭터 |
| Creative (전략·이론) | 2 | 바이럴 훅, AI 스토리 작성 |
| New Model (신모델 소개) | 1 | Seedance 2.0 |

### 기술 스택 등장 빈도

| 도구/모델 | 언급 수 | 주 용도 |
|---------|--------|--------|
| Veo 3.1 | 5개 | 영상 생성, Reference Mode, JSON |
| Nano Banana Pro | 3개 | 제품 이미지, UGC 크리에이터, 광고 |
| ElevenLabs / Hume AI | 2개 | 음성 클로닝 |
| Topaz | 2개 | 영상 업스케일 |
| Seedance 2.0 | 1개 | 멀티모달 영상 생성 |
| Trellis (3D) | 1개 | 이미지→3D 메시 추출 |

### 반복 등장 핵심 개념

**1. 루프백(Loopback)**
→ 8초 한계 우회 핵심 기법. 인피니트 애니, 레퍼런스 이미지→영상에서 공통 사용.

**2. JSON 프롬프팅**
→ 제품 광고, UGC, JSON 튜토리얼에서 공통 강조. "자연어보다 JSON이 훨씬 정확"

**3. 노드 기반 워크플로우**
→ 음성 정규화, 부동산 스테이징, 3D VFX, 인피니트 애니 모두 노드 파이프라인 사용.

**4. 1K → 4K 전략**
→ 빠른 반복은 1K, 최종 출력만 4K. 비용·시간 최적화.

**5. 오디오 퍼스트 설계**
→ Voice Normalization, 인피니트 애니, UGC 모두 오디오 동기화가 영상 품질 결정 요소.

### 학습 경로 (권장 순서)

```
입문
├── 업스케일링 (기본 출력 이해)
├── 바이럴 훅 (콘텐츠 전략)
└── AI 스토리 작성 (이론 기반)
    ↓
중급
├── Seedance 2.0 (최신 모델 파악)
├── 일관 캐릭터 (캐릭터 관리)
├── 라이브액션 블렌딩 (전환 기법)
└── 레퍼런스 이미지→영상
    ↓
고급
├── JSON 프롬프팅 (정밀 제어)
├── 인피니트 애니 (루프백)
├── 제품 광고 (풀 파이프라인)
├── UGC 영상
├── 음성 정규화
├── 부동산 스테이징
└── 3D VFX 리포지셔닝
```

### 비즈니스 활용 패턴

| 업종 | 활용 가능 튜토리얼 |
|------|------------------|
| 이커머스 | 제품 광고, UGC, 레퍼런스→영상 |
| 부동산 | 부동산 스테이징 파이프라인 |
| 소셜 마케터 | 바이럴 훅, UGC, 업스케일링 |
| 영상 크리에이터 | 인피니트 애니, 라이브액션 블렌딩, 일관 캐릭터 |
| VFX 아티스트 | 3D 리포지셔닝, JSON 프롬프팅 |
| 팟캐스트/내레이션 | 음성 정규화 |

### 전체 트렌드 시사점

1. **"생성"에서 "파이프라인"으로 진화**: 단순 텍스트→영상이 아니라, 노드를 연결한 자동화 파이프라인 중심. 콘텐츠 공장화.

2. **오디오 = 1등 시민**: 과거 영상 AI는 비주얼 중심. Sequencer는 음성 클로닝·오디오 싱크·사운드 디자인을 워크플로우 핵심에 배치.

3. **물리적 제약 해소**: 8초 한계(루프백), 촬영 필요(UGC·광고), 3D 아티스트(VFX), 방문 스테이징(부동산) — 모두 소프트웨어로 대체.

4. **JSON이 새 스크립트 언어**: 영상 감독의 콘티 역할을 JSON이 대체. 시각·오디오·카메라·타임스탬프를 코드처럼 정의.

5. **멀티모달 방향**: Seedance 2.0이 보여주듯, 텍스트+이미지+영상+오디오 동시 입력이 차세대 표준. 감독이 팀과 소통하는 방식을 AI에 그대로 적용.
