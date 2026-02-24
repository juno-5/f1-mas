# 슈퍼멤버스 광고 영상 — 프로덕션 레디 스크립트

> 기반: Meta 광고 성과 분석 상위 소재  
> 작성일: 2026-02-22  
> 상태: 노드 연결 즉시 제작 가능

---

# 기획안 1 — "이번 달 폐업 신고서 뽑아봤습니다"

**참고 소재**: 마케팅업체속지말기 (CTR 10.27%) + 광고비줄이고매출올린비밀  
**예상 CTR**: 10~15%  
**타겟**: 매출 위기 자영업자 (식당/카페/뷰티샵)  
**길이**: 30초

---

## 인물 디자인

**주인공: 자영업자 사장님 (남성)**

```
Grok / Nano Banana Pro 프롬프트:

A Korean man in his mid-40s, tired and weathered face showing years of hard work. 
Slight dark circles under eyes, unshaven stubble 2-3 days old. 
Medium build, slightly slumped posture showing exhaustion.
Wearing a casual dark navy t-shirt with a small logo apron over it.
Hair slightly disheveled, not styled.
Expression: deeply troubled, staring into the distance, then slowly looks at camera.
Realistic iPhone-quality selfie style photo.
Background: empty Korean restaurant interior at night, wooden tables with no customers, 
warm dim lighting from overhead lamps, rain visible through window.
Ultra-photorealistic, no CGI, authentic documentary feel.
Shot on iPhone 15 Pro, natural ambient light only.
```

**보조 화면용: 슈퍼멤버스 앱 UI 목업**
```
Smartphone screen showing a Korean local business review app.
Multiple 5-star reviews appearing in rapid succession.
Notification badges: "새 리뷰 +1", "새 리뷰 +1", "새 리뷰 +1"
Clean Korean UI, white background, orange/red accent colors.
```

---

## 전체 스크립트

### [0~2초] 훅
```
화면: 텅 빈 저녁 매장. 혼자 테이블에 앉은 사장님. 창밖엔 비.
      카메라를 인식하고 천천히 고개를 든다.

사운드: 빗소리 + 카페 BGM 흐르다가 뚝 끊김

텍스트 오버레이 (굵은 폰트, 흰색):
  "이번 달 폐업 신고서 뽑아봤습니다"
```

### [2~12초] 빌드
```
화면: 사장님 미디엄 클로즈업. 카메라 정면.
      손가락으로 테이블을 두드리며 말함.

대사:
  "임대료 350만원.
   직원 월급 280만원.
   이번 달 매출... 480만원이에요.
   계산해보세요."

텍스트 오버레이 (순차 등장):
  Line 1: "임대료 350만원"
  Line 2: "+ 직원 월급 280만원"
  Line 3: "─────────────"
  Line 4: "지출 630만원"
  Line 5: (빨간색) "매출 480만원"
  Line 6: (깜빡임) "💸 이번 달 -150만원"

사운드: 계산기 소리 효과
```

### [12~23초] 반전
```
화면: 사장님 스마트폰 알림음 연속으로 울림 (화면 전환)
      폰 화면: 슈퍼멤버스 앱에 리뷰 알림이 쏟아짐
      사장님 표정이 처음으로 살짝 밝아짐

대사:
  "근데 한 달 전부터 이상하게 예약이 들어오기 시작하더라고요.
   슈퍼멤버스라는 앱으로 진짜 손님들 리뷰가 쌓이면서
   네이버 검색 순위가 올라간 거예요."

텍스트 오버레이:
  "⭐ 리뷰 +47개 (30일)"
  "네이버 플레이스 순위 ↑"
  "이번 주 예약 🔴 완료"

사운드: 알림음 연속 (띵띵띵) + 긍정적 전환 BGM
```

### [23~30초] CTA
```
화면: 사장님 살짝 미소. 뒤로 손님 한두 명 들어오는 모습.
      마지막엔 슈퍼멤버스 로고 화면.

대사:
  "폐업 생각하기 전에... 이거 먼저 해보세요.
   저처럼 늦지 마시고."

텍스트 오버레이:
  "👇 무료로 시작하기 (카드 등록 없음)"
  "지금 바로 → supermembers.co.kr"

사운드: 따뜻한 BGM 마무리
```

---

## Veo 3.1 JSON 프롬프트

```json
{
  "description": "A desperate Korean small business owner in his mid-40s sitting alone in his empty restaurant at night. He reveals his financial crisis through specific numbers, then discovers a review platform that saves his business. Emotional arc: despair → crisis → unexpected hope.",
  "style": "Authentic documentary-style vertical video, 9:16, iPhone quality, Korean local business ad, no filters, raw and real",
  "camera": "Static medium close-up, eye-level, very slight handheld shake for authenticity, occasional slow zoom-in during emotional moments",
  "lighting": "Dim warm restaurant ambient lighting only, overhead lamps, dark shadows, rain visible through window — moody and real",
  "environment": "Empty Korean restaurant interior at night, wooden tables, no customers, rain on window, tired atmosphere",
  "elements": [
    "Korean man mid-40s, tired face, dark circles, stubble, navy apron, slumped posture",
    "Empty wooden tables and chairs in background",
    "Rain visible through restaurant window",
    "Smartphone showing review notifications"
  ],
  "motion": "Minimal movement — finger tapping table, slow head movements, tired gestures. Phone raised to show screen at midpoint.",
  "music": "Rain ambiance cuts to silence at 0s. Faint tense underscore 2-12s. Notification sounds 12-23s. Warm hopeful resolution 23-30s.",
  "sequences": [
    {
      "sequence": 1,
      "timestamp": "00:00-00:02",
      "action": "Man stares at empty restaurant, slowly raises eyes to camera as if noticing it for the first time",
      "audio": "Rain and ambient silence, then BGM cuts"
    },
    {
      "sequence": 2,
      "timestamp": "00:02-00:12",
      "action": "Direct camera address, finger tapping table counting expenses. Visible exhaustion and stress.",
      "audio": "Clear tired Korean male voice listing numbers: 임대료 350, 직원 월급 280, 매출 480"
    },
    {
      "sequence": 3,
      "timestamp": "00:12-00:23",
      "action": "Phone notification sounds, man's expression shifts from despair to cautious surprise as he shows phone screen",
      "audio": "Rapid notification dings, voice explains SuperMembers discovery, tone lifts slightly"
    },
    {
      "sequence": 4,
      "timestamp": "00:23-00:30",
      "action": "Subtle smile, customers visible entering in background, man looks directly at camera with sincerity",
      "audio": "Warm sincere voice: 폐업 생각하기 전에 이거 먼저 해보세요"
    }
  ]
}
```

---
---

# 기획안 2 — "AI가 3일 만에 제 가게를 1위로 만들었어요"

**참고 소재**: 30일간상위노출실험 (CTR 3.87%), 돈안날리는상위노출  
**예상 CTR**: 8~12%  
**타겟**: 네이버 검색 신경 쓰는 자영업자  
**길이**: 40초

---

## 인물 디자인

**주인공: 여성 카페 사장님**

```
Grok / Nano Banana Pro 프롬프트:

A Korean woman in her late 30s, bright and slightly surprised expression, 
showing a "can you believe this?" energy. 
Natural makeup, hair in casual ponytail, wearing a light beige linen apron 
over a white collared shirt.
Holding a smartphone with both hands, showing it to camera excitedly.
Expression: genuine shock mixed with delight, eyebrows raised, slight open mouth smile.
Realistic iPhone-quality selfie, standing in a modern Korean cafe interior.
Background: bright airy cafe, coffee equipment visible, morning light through windows.
Ultra-photorealistic, warm morning light, natural and authentic.
Shot on iPhone 15 Pro.
```

---

## 전체 스크립트

### [0~3초] 훅
```
화면: 카페 사장님이 폰 화면을 카메라에 들이밀며 등장
      폰 화면에 "네이버 플레이스 1위" 화면 보임

대사: "저 오늘 네이버 1위 찍었어요. 3일 만에요."

텍스트 오버레이:
  "🥇 네이버 검색 1위"
  "단 3일 만에"

사운드: 성취 효과음 (띵!) + 밝은 BGM 시작
```

### [3~20초] 빌드
```
화면: 폰 화면 클로즈업 — 순위 변화 화면들
      Day 1, Day 2, Day 3 순으로 컷 전환

대사:
  "원래 저 네이버 검색하면 27위였거든요.
   손님들이 저희 카페 찾지도 못했어요.
   
   근데 슈퍼멤버스 쓴 첫날부터 리뷰가 쌓이기 시작했고,
   3일 만에 1위로 올라왔어요.
   AI가 진짜 손님들 데이터를 분석해서
   언제 어떤 리뷰가 필요한지 자동으로 잡아준 거예요."

텍스트 오버레이:
  "Day 1: 27위 → 리뷰 시작"
  "Day 2: 11위"  
  "Day 3: 🥇 1위"

사운드: 순위 올라갈 때마다 상승음 효과
```

### [20~33초] 피크
```
화면: 카페 안 손님들로 가득 찬 모습 (비포-애프터 느낌)
      예약 알림 화면

대사:
  "지금 이번 주 예약이 꽉 찼어요.
   솔직히 처음엔 반신반의했는데
   직접 해보니까 진짜더라고요."

텍스트 오버레이:
  "이번 주 예약 🔴 마감"
  "대기 17명"
```

### [33~40초] CTA
```
화면: 사장님 카메라 보며 폰 들어서 보여줌

대사:
  "저처럼 27위에서 답답하신 분들
   일단 무료로 3일만 써보세요. 진짜로요."

텍스트 오버레이:
  "👇 3일 무료 체험"
  "지금 시작 → supermembers.co.kr"
```

---
---

# 기획안 3 — "손님한테 이런 말 들을 줄 몰랐어요"

**참고 소재**: 머니멘터리_자동화마케팅 (CTR 12.77%, CPL 9,221원)  
**예상 CTR**: 10~14%  
**타겟**: 리뷰/평판 신경 쓰는 자영업자  
**길이**: 35초

---

## 인물 디자인

**주인공: 치킨집/분식집 남성 사장님**

```
Grok / Nano Banana Pro 프롬프트:

A Korean man in his early 50s, cheerful and warm grandfather-like energy.
Round friendly face, slight wrinkles from smiling, warm brown eyes.
Wearing a bright red polo shirt with a small restaurant logo.
Slightly chubby build, confident and relaxed posture.
Expression: genuine happy surprise, hand on chest "I can't believe this" gesture.
Realistic iPhone-quality photo, standing behind restaurant counter.
Background: busy Korean local restaurant, food prep visible, warm lighting.
Ultra-photorealistic, authentic local business feel.
Shot on iPhone 15 Pro, warm kitchen lighting.
```

---

## 전체 스크립트

### [0~3초] 훅
```
화면: 사장님이 폰 화면 들고 카메라 앞으로 다가옴
      굉장히 신난 표정

대사: "손님이 저한테 이런 문자를 보냈어요."

텍스트 오버레이 (카카오톡 메시지 스타일):
  💬 "사장님, 저 리뷰 잘 쓰고 싶어서 다시 왔어요"

사운드: 카카오톡 알림음
```

### [3~20초] 빌드
```
화면: 사장님 인터뷰 스타일 직접 카메라 응시

대사:
  "원래 저 리뷰 관리 안 했거든요.
   그냥 맛있게만 만들면 되겠지 했는데...
   
   슈퍼멤버스 쓰고 나서부터
   진짜 손님들이 리뷰 쓰러 다시 온다고요.
   
   그게 또 다른 손님을 불러오고,
   그 손님이 또 리뷰 쓰고.
   
   선순환이 생겼어요."

텍스트 오버레이:
  "진짜 손님 → 진짜 리뷰"
  "진짜 리뷰 → 새 손님"
  "🔄 자동으로 돌아가는 선순환"
```

### [20~30초] 피크
```
화면: 리뷰 화면 클로즈업 (별 5개짜리 줄줄이)
      사장님 자랑스러운 표정

대사:
  "지난 달에 리뷰가 63개 달렸어요.
   제가 아무것도 안 했는데.
   슈퍼멤버스가 알아서 해준 거예요."

텍스트 오버레이:
  "지난 달 리뷰 +63개"
  "사장님 개입 없이 자동"
```

### [30~35초] CTA
```
화면: 사장님 카메라 보며 엄지 척

대사:
  "맛있는 음식 만드는 데만 집중하세요.
   리뷰는 슈퍼멤버스한테 맡기시고요."

텍스트:
  "👇 지금 무료로 시작"
```

---
---

# 기획안 4 — "마케팅 공부 유튜브 그만 보세요"

**참고 소재**: 무료체험단하지마세요 (CTR 2.11%) + 마케팅업체속지말기  
**예상 CTR**: 7~10%  
**타겟**: 마케팅 공부하느라 시간 낭비하는 자영업자  
**길이**: 30초

---

## 인물 디자인

**주인공: 뷰티샵/네일샵 여성 사장님**

```
Grok / Nano Banana Pro 프롬프트:

A Korean woman in her early 40s, smart and no-nonsense energy.
Sharp features, confident gaze, minimal makeup.
Wearing a sleek black salon uniform/apron.
Slim build, straight posture, arms crossed slightly then releases.
Expression: knowingly tired but warm — "I've been there, here's what actually works."
Realistic iPhone-quality selfie photo.
Background: modern Korean beauty salon, nail stations visible, clean white interior.
Ultra-photorealistic, clean bright salon lighting.
Shot on iPhone 15 Pro.
```

---

## 전체 스크립트

### [0~3초] 훅
```
화면: 사장님이 팔짱 끼고 카메라 봄. 약간 단호한 표정.

대사: "마케팅 유튜브 그만 보세요. 진짜로요."

텍스트 오버레이:
  "🛑 마케팅 공부가 오히려 독인 이유"

사운드: 강한 베이스 히트
```

### [3~18초] 빌드
```
화면: 새벽에 유튜브 보는 장면 (시뮬레이션)
      눈 충혈, 시계 새벽 2시

대사:
  "저도 한 때 새벽 2시까지 마케팅 강의 봤어요.
   SEO, 블로그, 인스타, 유튜브...
   6개월 공부하고 실천했는데
   매출은 그대로였어요.
   
   이유가 뭔지 알아요?
   자영업자는 마케터가 되면 안 돼요.
   사장이어야 하거든요."

텍스트 오버레이:
  "6개월 마케팅 공부"
  "매출 변화: 0원"
  "문제는 공부가 아니었다"
```

### [18~26초] 반전
```
화면: 슈퍼멤버스 앱 클릭 몇 번으로 끝나는 화면

대사:
  "슈퍼멤버스는 클릭 3번이에요.
   AI가 알아서 분석하고, 진짜 손님 연결하고,
   리뷰 관리까지 다 해줘요.
   사장님은 장사만 하면 돼요."

텍스트 오버레이:
  "클릭 3번으로 끝"
  "AI가 알아서 함"
  "당신은 장사만"
```

### [26~30초] CTA
```
대사: "오늘 유튜브 끄고 이거 한 번만 해보세요."

텍스트:
  "👇 3분이면 시작 가능"
  "무료로 바로 시작"
```

---
---

# 기획안 5 — "손님이 없는 게 내 잘못이 아니었어요"

**참고 소재**: 옆집마케팅비밀 + 광고비줄이고매출올린비밀  
**예상 CTR**: 8~11%  
**타겟**: 자책하는 자영업자 (심리적 고통 정면 돌파)  
**길이**: 40초

---

## 인물 디자인

**주인공: 동네 식당 여성 사장님**

```
Grok / Nano Banana Pro 프롬프트:

A Korean woman in her late 40s, kind and resilient face with laugh lines.
Slightly tired eyes but warm expression — the look of someone who has been through a lot.
Wearing a floral pattern apron over casual clothes.
Medium build, warm and approachable energy.
Expression: starts vulnerable and reflective, transitions to empowered and resolved.
Realistic iPhone-quality photo.
Background: small Korean neighborhood restaurant, homestyle decor, warm lighting.
Ultra-photorealistic, warm homey lighting.
Shot on iPhone 15 Pro.
```

---

## 전체 스크립트

### [0~3초] 훅
```
화면: 사장님 혼자 텅 빈 매장 정리하다 카메라 봄

대사: "저 진짜로... 내가 뭘 잘못하나 생각했었어요."

텍스트 오버레이:
  "손님이 없는 건 내 잘못이 아니었습니다"

사운드: 조용하고 감성적인 피아노
```

### [3~20초] 빌드
```
화면: 회상 느낌 (흑백 or 필터)
      새벽에 음식 준비하는 사장님 손
      텅 빈 테이블
      창밖 지나가는 손님들

대사:
  "음식 더 맛있게 만들려고 레시피도 바꿨고,
   인테리어도 손봤고,
   가격도 낮춰봤는데...
   
   그래도 손님이 안 왔어요.
   
   근데 알고 보니까 문제는 '노출'이었어요.
   저희 가게가 네이버에서 아예 안 보였던 거예요."

텍스트 오버레이:
  "레시피 개선 → 효과 없음"
  "인테리어 → 효과 없음"
  "가격 인하 → 효과 없음"
  "진짜 문제: 검색에서 안 보임"
```

### [20~33초] 반전
```
화면: 컬러로 전환 (희망)
      슈퍼멤버스로 리뷰 쌓이는 화면
      네이버 순위 올라가는 화면
      실제 손님들 들어오는 가게

대사:
  "슈퍼멤버스로 진짜 손님 리뷰 모으기 시작했더니
   한 달 만에 네이버 검색에 보이기 시작했어요.
   
   제 음식이 나빴던 게 아니라
   그냥 아무도 저를 못 찾았던 거예요."

텍스트:
  "한 달 후: 네이버 검색 상위 노출"
  "음식은 처음부터 좋았다"
```

### [33~40초] CTA
```
화면: 사장님 환하게 웃으며 카메라 봄

대사:
  "잘못한 거 없어요. 그냥 알려지지 않은 거예요.
   이제 알릴 수 있어요."

텍스트:
  "👇 무료로 알려지기 시작"
```

---

# 🔧 노드 연결 후 즉시 실행 체크리스트

## Step 1: 이미지 생성 (Nano Banana Pro / Grok)
```
□ 기획안 1 — 40대 남성 자영업자 이미지 (위 프롬프트)
□ 기획안 2 — 30대 여성 카페 사장님 이미지
□ 기획안 3 — 50대 남성 식당 사장님 이미지
□ 기획안 4 — 40대 여성 뷰티샵 사장님 이미지
□ 기획안 5 — 40대 여성 식당 사장님 이미지
□ 슈퍼멤버스 앱 목업 화면 (리뷰 쌓이는 UI)
□ 각 캐릭터별 변형 이미지 2~3장 (다른 각도)
```

## Step 2: 영상 생성 (Google Flow / Veo 3.1)
```
□ 생성된 이미지 → Start Frame으로 사용
□ 위 JSON 프롬프트로 각 씬별 영상 생성
□ 루프백 기법으로 씬 이어붙이기
□ 총 30~40초 완성
```

## Step 3: 후반 작업
```
□ 자막 삽입 (전체 구간 풀자막)
□ 텍스트 오버레이 (기획안의 텍스트 그대로)
□ BGM/사운드 효과 삽입
□ Topaz 4K 업스케일
□ 9:16 세로 확인
```

## Step 4: Meta 광고 업로드
```
□ Meta Business Manager → 광고 크리에이티브 업로드
□ 네이밍: 260222-painpoint-vp-폐업신고서-v1-LNK-VID
□ 기존 상위 캠페인(리드)에 A/B 테스트로 추가
□ 초기 예산: 10만원/일 (검증 후 확대)
```

---

# 📊 성과 예측 (기존 소재 대비)

| 기획안 | 예상 CTR | 예상 CPL | 월 리드 (50만/월 기준) |
|--------|---------|---------|---------------------|
| 1 (폐업신고서) | 10~15% | 15,000~25,000원 | 20~33건 |
| 2 (AI 3일 1위) | 8~12% | 20,000~30,000원 | 17~25건 |
| 3 (손님 문자) | 10~14% | 15,000~22,000원 | 23~33건 |
| 4 (유튜브 그만) | 7~10% | 25,000~35,000원 | 14~20건 |
| 5 (내 잘못 아님) | 8~11% | 18,000~28,000원 | 18~28건 |
| **기존 최고 소재** | **2.89%** | **38,355원** | **13건** |
