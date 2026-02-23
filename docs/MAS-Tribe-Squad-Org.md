# MAS Tribe & Squad Organization

> 184명 / 27 Squads / 5 Tribes / 8 Chapters
> MAS API: `http://100.88.145.15:7720` | xapi: `http://100.88.145.15:7750/mas`

---

## 전체 조직 구조

MAS는 **매트릭스 조직**이다. 모든 페르소나는 두 개의 축에 동시에 속한다:

- **Tribe / Squad** (세로축) — 미션 기반 팀. 프로젝트 단위 라우팅에 사용
- **Functional Chapter** (가로축) — 직능 기반 그룹. 전문성 기반 라우팅에 사용

```
                          ┌─────────────────────────┐
                          │     MAS Organization     │
                          │ 184명 · 27 Sqd · 5T · 8C │
                          └────────────┬────────────┘
                                       │
                 ┌─────────────────────┴──────────────────────┐
                 │                                            │
          ═══ VERTICAL (Tribes) ═══              ═══ HORIZONTAL (Chapters) ═══
          미션/프로젝트 기반 팀                    직능/전문성 기반 그룹
                 │                                            │
    ┌────┬────┬──┴──┬────┐               ┌────┬────┬──┴──┬────┬────┬────┬────┐
    ▼    ▼    ▼     ▼    ▼               ▼    ▼    ▼     ▼    ▼    ▼    ▼    ▼
  Prod Grow  Rev  Brand Mod           Dev  Mkt  Mod   Cre  Com  Sls  UX   CX
  (38) (30) (15)  (41) (60)          (33) (60) (60) (11)  (5)  (5)  (5)  (5)
```

---

### Tribe (세로축) — 5개

```
  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │ Product │ │  Growth  │ │Revenue │ │ Brand  │ │ Model  │
  │  38명   │ │   30명   │ │  15명  │ │  41명  │ │  60명  │
  │ 6 Sqd   │ │  6 Sqd   │ │ 3 Sqd  │ │ 8 Sqd  │ │ 4 Sqd  │
  └────┬────┘ └────┬─────┘ └───┬────┘ └───┬────┘ └───┬────┘
       │           │           │          │          │
       ├ Engineering(8)  ├ Growth KR(5)   ├ Commerce(5)  ├ Brand KR(5)    ├ Korea(20)
       ├ AI&Data(7)      ├ Growth US(5)   ├ Sales(5)     ├ Brand US(5)    ├ Japan(10)
       ├ Platform(5)     ├ TikTok KR(5)   └ CX(5)       ├ ComMkt KR(5)   ├ USA(20)
       ├ GenAI(3)        ├ TikTok US(5)                  ├ ComMkt US(5)   └ Europe(10)
       ├ Global Eng(10)  ├ Amazon KR(5)                  ├ Design KR(5)
       └ Prod Design(5)  └ Amazon US(5)                  ├ Design US(5)
                                                         ├ Creative(5)
                                                         └ Art Master(6)
```

| Tribe | 역할 | 핵심 역량 |
|-------|------|----------|
| **Product** (38) | 제품 개발 & 기술 | 엔지니어링, AI/ML, 플랫폼, 디자인 |
| **Growth** (30) | 시장 확장 | Growth Hacking, TikTok, Amazon (KR/US) |
| **Revenue** (15) | 매출 창출 | 커머스, 세일즈, CX |
| **Brand** (41) | 브랜드 구축 | 브랜딩, 커머스마케팅, 디자인, 크리에이티브, AI아트 |
| **Model** (60) | 패션 모델링 | 한국, 일본, 미국, 유럽 |

---

### Functional Chapter (가로축) — 8개

기존 MAS 선택 엔진이 사용하는 직능 분류. `tribe/squad` 없이 요청하면 이 축으로 라우팅된다.

```
  Chapter          인원    대표 ID 범위                 전문 영역
  ─────────────────────────────────────────────────────────────────────
  Developers        33    F1-00~22, FC-01~10           시스템, AI/ML, 보안, 인프라
  Marketers         60    GRO/TIK/AMZ/BRD/COM/DES-xx   그로스, 퍼포먼스, 브랜딩, 디자인
  Models            60    KF/KM/JF/JM/USF/USM/EUF/EUM  패션 모델링 (4개국)
  Creatives         11    01~05, AM-01~06                오감 크리에이티브 + AI Art Master
  Commerce           5    CMM-01~05                     커머스 아키텍처, CRO, 마켓플레이스
  Sales              5    SLS-01~05                     엔터프라이즈, PLG, 채널 세일즈
  UI/UX              5    UX-01~05                      인터랙션, 리서치, 디자인시스템
  CX                 5    CX-01~05                      고객 성공, VoC, 옴니채널
  ─────────────────────────────────────────────────────────────────────
  합계             184
```

#### Developers Chapter (33명)

| 그룹 | 인원 | ID 범위 | 핵심 |
|------|------|---------|------|
| F1 Core | 8 | F1-00 ~ F1-07 | 시스템, 보안, 아키텍처, 성능, 알고리즘 |
| F1 Extended | 12 | F1-08 ~ F1-19 | ML, 컴파일러, 데이터, SRE, NLP, 클라우드, 양자 |
| F1 GenAI | 3 | F1-20 ~ F1-22 | 이미지/비디오/오디오 생성 |
| Falcon Global | 10 | FC-01 ~ FC-10 | 글로벌 분산 엔지니어링 (8개국) |

#### Marketers Chapter (60명)

| 기능 | KR | US | 합계 |
|------|----|----|------|
| Growth | GRO-KR-01~05 | GRO-US-01~05 | 10 |
| TikTok | TIK-KR-01~05 | TIK-US-01~05 | 10 |
| Amazon | AMZ-KR-01~05 | AMZ-US-01~05 | 10 |
| Brand | BRD-KR-01~05 | BRD-US-01~05 | 10 |
| Commerce Mkt | COM-KR-01~05 | COM-US-01~05 | 10 |
| Design | DES-KR-01~05 | DES-US-01~05 | 10 |
| | **30** | **30** | **60** |

#### Models Chapter (60명)

| 지역 | 여성 | 남성 | 합계 |
|------|------|------|------|
| Korea | KF01~14 (14) | KM01~06 (6) | 20 |
| Japan | JF01~07 (7) | JM01~03 (3) | 10 |
| USA | USF01~13 (13) | USM01~07 (7) | 20 |
| Europe | EUF01~07 (7) | EUM01~03 (3) | 10 |
| | **41** | **19** | **60** |

#### 전문직 Chapters (각 5명)

| Chapter | Lead | 구성원 | 핵심 역할 |
|---------|------|--------|----------|
| **Creatives** | 01 LUMEN / AM-01 NEXART | Five Senses (5) + Art Master (6) | 오감 크리에이티브 + AI아트 |
| **Commerce** | CMM-01 Apex | Apex, Metric, Tide, Matrix, Anchor | 커머스 전략/최적화 |
| **Sales** | SLS-01 Blade | Blade, Echo, Storm, Cipher, Pivot | 엔터프라이즈/채널 세일즈 |
| **UI/UX** | UX-01 Vision | Vision, Sketch, Palette, Arc, Spark | 디자인/리서치/시스템 |
| **CX** | CX-01 Harbor | Harbor, Bridge, Compass, Weave, Root | 고객경험/VoC/옴니채널 |

---

### Chapter x Tribe 매트릭스

각 페르소나가 어떤 Chapter(가로)와 Tribe(세로)에 동시에 속하는지 보여주는 교차표:

```
              │ Product │ Growth │ Revenue │  Brand │  Model │ 합계
  ────────────┼─────────┼────────┼─────────┼────────┼────────┼──────
  Developers  │   33    │        │         │        │        │  33
  Marketers   │         │   30   │         │   30   │        │  60
  Models      │         │        │         │        │   60   │  60
  Creatives   │         │        │         │   11   │        │  11
  Commerce    │         │        │    5    │        │        │   5
  Sales       │         │        │    5    │        │        │   5
  UI/UX       │    5    │        │         │        │        │   5
  CX          │         │        │    5    │        │        │   5
  ────────────┼─────────┼────────┼─────────┼────────┼────────┼──────
  합계        │   38    │   30   │   15    │   41   │   60   │ 184
```

> **읽는 법**: "Commerce Chapter 5명은 전원 Revenue Tribe 소속"
> "Marketers 60명 중 30명은 Growth Tribe, 30명은 Brand Tribe"

---

### 라우팅 방식 비교

| 요청 | 라우팅 축 | 예시 |
|------|----------|------|
| `tribe/squad` 없이 | **Chapter (가로)** | `"보안 감사"` → Developers 중 Viper, Zero 선택 |
| `tribe=` 지정 | **Tribe (세로)** | `"tribe":"growth"` → Growth 30명 풀에서 선택 |
| `squad=` 지정 | **Squad (세로)** | `"squad":"engineering"` → Engineering 8명에서 선택 |
| 둘 다 없지만 키워드 감지 | **자동 탐지** | `"아마존 입점"` → Growth Tribe 자동 감지 |

---

## Product Tribe (38명, 6 Squads)
> Engineering, AI/Data, Platform, GenAI, Global Engineering, Product Design

### Engineering Squad (8명) — Lead: F1-00 Kernel
| ID | Callsign | Role |
|----|----------|------|
| F1-00 | Kernel | Principal Systems Engineer (Lead) |
| F1-01 | Viper | AI Security Engineer |
| F1-02 | Forge | Full-Stack Architect |
| F1-03 | Blaze | Performance Engineer |
| F1-04 | Axiom | Algorithm Engineer |
| F1-05 | Trace | Debug Engineer |
| F1-06 | Zero | Security Researcher |
| F1-07 | Hex | Distributed Systems |

### AI & Data Squad (7명) — Lead: F1-08 Pulse
| ID | Callsign | Role |
|----|----------|------|
| F1-08 | Pulse | ML Training & Optimization |
| F1-09 | Prism | AI Compiler & Runtime |
| F1-10 | Flux | Data Engineering |
| F1-11 | Sentinel | Site Reliability |
| F1-12 | Cortex | NLP / Language Models |
| F1-16 | Mirage | Cloud & Virtualization |
| F1-19 | Nova | Quantum-Classical Hybrid |

### Platform Squad (5명) — Lead: F1-13 Pixel
| ID | Callsign | Role |
|----|----------|------|
| F1-13 | Pixel | Vision & Multimodal AI |
| F1-14 | Vault | Database & Storage |
| F1-15 | Wire | Network Engineering |
| F1-17 | Sage | Formal Verification |
| F1-18 | Ember | Product Engineering |

### GenAI Squad (3명) — Lead: F1-20 Canvas
| ID | Callsign | Role |
|----|----------|------|
| F1-20 | Canvas | Image Generation |
| F1-21 | Frame | Video Generation |
| F1-22 | Resonance | Audio Generation |

### Global Engineering Squad (10명) — Lead: FC-01 Nexus
| ID | Callsign | Location | Role |
|----|----------|----------|------|
| FC-01 | Nexus | Seattle | System Architect (Lead) |
| FC-02 | Bedrock | Mexico City | Backend & Infrastructure |
| FC-03 | Neuron | Bangalore | AI/ML Engineering |
| FC-04 | Grid | San Francisco | Frontend & UX |
| FC-05 | Crane | Tokyo | DevOps & Platform |
| FC-06 | Guardian | Dubai | Security |
| FC-07 | Delta | Seoul | Data Engineering |
| FC-08 | Core | Moscow | Systems Engineering |
| FC-09 | Atlas | Mumbai | Product Management |
| FC-10 | Helm | London | Engineering Management |

### Product Design Squad (5명) — Lead: UX-01 Vision
| ID | Callsign | Role |
|----|----------|------|
| UX-01 | Vision | Chief Design Officer |
| UX-02 | Sketch | Interaction Design & Motion |
| UX-03 | Palette | User Research & Insights |
| UX-04 | Arc | Design Systems & Accessibility |
| UX-05 | Spark | UX Engineering |

---

## Growth Tribe (30명, 6 Squads)
> Growth, TikTok, Amazon — KR & US market squads

### Growth KR Squad (5명) — Lead: GRO-KR-01
최현우(Hank Choi), 윤지현, 임도윤, 송예린, 한승민

### Growth US Squad (5명) — Lead: GRO-US-01
Alex Rivera, Michelle Lee, Tyler Williams, Rachel Kim, Brandon Taylor

### TikTok KR Squad (5명) — Lead: TIK-KR-01
권태현(Tyler Kwon), 문지아, 정호성, 이수민, 강예찬

### TikTok US Squad (5명) — Lead: TIK-US-01
Kevin Nguyen, Olivia Brooks, Daniel Kim, Jessica Wang, Andrew Scott

### Amazon KR Squad (5명) — Lead: AMZ-KR-01
오준혁(Jake Oh), 배서현, 황동현, 신유나, 조민재

### Amazon US Squad (5명) — Lead: AMZ-US-01
Robert Zhang, Jennifer Martinez, Michael Johnson, Amanda Wilson, Christopher Lee

---

## Revenue Tribe (15명, 3 Squads)
> Commerce, Sales, CX — revenue-driving functions

### Commerce Squad (5명) — Lead: CMM-01 Apex
| ID | Callsign | Role |
|----|----------|------|
| CMM-01 | Apex | Commerce Architecture |
| CMM-02 | Metric | Conversion Optimization |
| CMM-03 | Tide | Marketplace Strategy |
| CMM-04 | Matrix | Data & Personalization |
| CMM-05 | Anchor | Loyalty & Retention |

### Sales Squad (5명) — Lead: SLS-01 Blade
| ID | Callsign | Role |
|----|----------|------|
| SLS-01 | Blade | Enterprise Sales |
| SLS-02 | Echo | Sales Methodology |
| SLS-03 | Storm | PLG & Channel Sales |
| SLS-04 | Cipher | Global Account Management |
| SLS-05 | Pivot | Sales Engineering |

### CX Squad (5명) — Lead: CX-01 Harbor
| ID | Callsign | Role |
|----|----------|------|
| CX-01 | Harbor | Chief CX Officer |
| CX-02 | Bridge | Customer Success |
| CX-03 | Compass | CX Analytics & VoC |
| CX-04 | Weave | Omnichannel CX |
| CX-05 | Root | CX Operations & QA |

---

## Brand Tribe (41명, 8 Squads)
> Branding, Commerce Marketing, Design, Creative

### Brand KR Squad (5명) — Lead: BRD-KR-01
유현진(Ashley Yoo), 박성훈, 김소희, 이준영, 최민지

### Brand US Squad (5명) — Lead: BRD-US-01
Victoria Chen, James Morrison, Samantha Wright, Michael Torres, Lauren Kim

### Commerce Mkt KR Squad (5명) — Lead: COM-KR-01
강민준(Jay Kang), 이서연, 박재현, 김하은, 정우진

### Commerce Mkt US Squad (5명) — Lead: COM-US-01
Marcus Chen, Sarah Mitchell, David Rodriguez, Emily Thompson, Jason Park

### Design KR Squad (5명) — Lead: DES-KR-01
장예은(Yena Jang), 김태호, 박서연, 이동훈, 한수아

### Design US Squad (5명) — Lead: DES-US-01
Alexandra Foster, Ryan Nakamura, Emma Rodriguez, Christopher Wang, Olivia Martinez

### Creative Squad (5명) — Lead: 01 LUMEN
| ID | Callsign | Sense |
|----|----------|-------|
| 01 | LUMEN | Light |
| 02 | CHROMA | Color |
| 03 | ECHO | Sound |
| 04 | TEMPO | Motion |
| 05 | FUME | Scent |

### Art Master Squad (6명) — Lead: AM-01 NEXART
| ID | Callsign | Role |
|----|----------|------|
| AM-01 | NEXART | AI Art Director (Lead) |
| AM-02 | VEO | Veo 3 Video Generation |
| AM-03 | KLING | Kling + Higgsfield Motion |
| AM-04 | BLOOM | Nano Banana Image Generation |
| AM-05 | SEED | Seedance Short-form |
| AM-06 | ORACLE | Global Prompt Architect |

---

## Model Tribe (60명, 4 Squads)
> Fashion models — Korea, Japan, USA, Europe

### Korea Squad (20명) — Lead: KF01
KF01~KF14 (여성 14명), KM01~KM06 (남성 6명)

### Japan Squad (10명) — Lead: JF01
JF01~JF07 (여성 7명), JM01~JM03 (남성 3명)

### USA Squad (20명) — Lead: USF01
USF01~USF13 (여성 13명), USM01~USM07 (남성 7명)

### Europe Squad (10명) — Lead: EUF01
EUF01~EUF07 (여성 7명), EUM01~EUM03 (남성 3명)

---

## API Endpoints

### MAS 직접 (localhost:7720)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tribes` | 전체 Tribe 목록 |
| GET | `/tribes/{id}` | Tribe 상세 (소속 Squad + 멤버) |
| GET | `/tribes/{id}/squads` | Tribe의 Squad 목록 |
| GET | `/squads` | 전체 Squad 목록 (?tribe= 필터) |
| GET | `/squads/{id}` | Squad 상세 (lead + 멤버) |
| GET | `/personas/select?q=&tribe=&squad=` | Tribe/Squad 제약 선택 |
| POST | `/request` | 요청 (tribe/squad 파라미터) |

### xapi 게이트웨이 (100.88.145.15:7750)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/mas/tribes` | 전체 Tribe 목록 (캐시 60s) |
| GET | `/mas/tribes/{id}` | Tribe 상세 |
| GET | `/mas/tribes/{id}/squads` | Tribe의 Squad 목록 |
| GET | `/mas/squads` | 전체 Squad 목록 (?tribe= 필터) |
| GET | `/mas/squads/{id}` | Squad 상세 (lead + 멤버) |
| GET | `/mas/org/summary` | 조직 전체 요약 |
| POST | `/mas/org/route` | 쿼리 → Tribe/Squad 자동 추천 |
| GET | `/mas/personas/search?q=&tribe=&squad=` | Tribe/Squad 제약 선택 |
| POST | `/mas/request` | 요청 (tribe/squad 파라미터) |

> xapi 호출 시 `X-API-Key` 헤더 필요

---

## 사용 예시

```bash
# Tribe 목록 (MAS 직접)
curl -s http://100.88.145.15:7720/tribes

# Tribe 목록 (xapi 경유)
curl -s -H "X-API-Key: $KEY" http://100.88.145.15:7750/mas/tribes

# Product Tribe의 Engineering Squad만 활용해서 코드 리뷰
curl -X POST http://100.88.145.15:7720/request \
  -H 'Content-Type: application/json' \
  -d '{"query":"마이크로서비스 아키텍처 리뷰","squad":"engineering"}'

# Growth Tribe 전체에서 그로스 전략
curl -X POST http://100.88.145.15:7720/request \
  -H 'Content-Type: application/json' \
  -d '{"query":"신규 앱 그로스 전략","tribe":"growth"}'

# 조직 전체 요약 (xapi 전용)
curl -s -H "X-API-Key: $KEY" http://100.88.145.15:7750/mas/org/summary

# 쿼리에 최적 Tribe/Squad 추천 (dry-run, xapi 전용)
curl -s -X POST -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  http://100.88.145.15:7750/mas/org/route \
  -d '{"query":"모바일 앱 그로스 전략"}'

# 기존처럼 tribe/squad 없이도 100% 호환
curl -X POST http://100.88.145.15:7720/request \
  -H 'Content-Type: application/json' \
  -d '{"query":"보안 감사"}'
```
