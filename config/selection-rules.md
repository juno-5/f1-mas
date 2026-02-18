# MAS Persona Selection Rules

## Domain → Category Mapping

| User Intent | Primary Category | Secondary |
|-------------|-----------------|-----------|
| 코드 리뷰, 아키텍처, 버그 | `developers/` | — |
| 마케팅, 캠페인, 광고 | `marketers/` | `creatives/` |
| 화보, 촬영, 모델 캐스팅 | `models/` | `creatives/` |
| 브랜딩, 디자인, 비주얼 | `marketers/` (BRD/DES) | `creatives/` |
| 사운드, 음악, 음향 | `creatives/` (ECHO) | `developers/` (Resonance) |
| 이미지 생성, AI 아트 | `developers/` (Canvas) | `creatives/` |
| 영상 제작, 시네마 | `developers/` (Frame) | `creatives/` (TEMPO) |
| 제품 기획, PM | `developers/` (Ember/Priya) | `marketers/` |
| 보안, 해킹 방어 | `developers/` (Viper/Zero/Omar) | — |
| 인프라, 배포, SRE | `developers/` (Sentinel/Yuki) | — |
| 데이터, 분석 | `developers/` (Flux/Lisa) | `marketers/` (GRO) |

## Function → Persona Priority

### Technical Functions

| Function | 1st Choice | 2nd Choice | 3rd Choice |
|----------|-----------|-----------|-----------|
| System Architecture | Forge (F1-02) | Marcus (FC-01) | Hex (F1-07) |
| Security Audit | Viper (F1-01) | Zero (F1-06) | Omar (FC-06) |
| Performance Optimization | Blaze (F1-03) | Dmitri (FC-08) | — |
| Algorithm Design | Axiom (F1-04) | — | — |
| Debugging / Root Cause | Trace (F1-05) | — | — |
| ML Training / Fine-tuning | Pulse (F1-08) | Raj (FC-03) | — |
| AI Compiler / Runtime | Prism (F1-09) | — | — |
| Data Pipeline | Flux (F1-10) | Lisa (FC-07) | — |
| SRE / Monitoring | Sentinel (F1-11) | Yuki (FC-05) | — |
| NLP / LLM | Cortex (F1-12) | Pulse (F1-08) | — |
| Vision / Multimodal | Pixel (F1-13) | Canvas (F1-20) | — |
| Database / Storage | Vault (F1-14) | Elena (FC-02) | — |
| Networking | Wire (F1-15) | — | — |
| Cloud / Container | Mirage (F1-16) | Yuki (FC-05) | — |
| Formal Verification | Sage (F1-17) | — | — |
| Product / UX | Ember (F1-18) | Priya (FC-09) | Sarah (FC-04) |
| Quantum Computing | Nova (F1-19) | — | — |
| Image Generation | Canvas (F1-20) | Pixel (F1-13) | — |
| Video Generation | Frame (F1-21) | TEMPO (Creative) | — |
| Audio / Voice Gen | Resonance (F1-22) | ECHO (Creative) | — |
| Frontend / UI | Sarah (FC-04) | Forge (F1-02) | — |
| Engineering Mgmt | James (FC-10) | Marcus (FC-01) | — |

### Marketing Functions

| Function | KR 1st | KR 2nd | US 1st | US 2nd |
|----------|--------|--------|--------|--------|
| Commerce Strategy | Jay Kang | Serena Lee | Marcus Chen | Sarah Mitchell |
| Growth Hacking | Hank Choi | Simon Han | Alex Rivera | Brandon Taylor |
| Amazon Ops | Jake Oh | Sophie Bae | Robert Zhang | Jennifer Martinez |
| TikTok / Short-form | Tyler Kwon | Gia Moon | Kevin Nguyen | Olivia Brooks |
| Brand Strategy | Ashley Yoo | Sean Park | Victoria Chen | James Morrison |
| Visual Design | Yena Jang | Theo Kim | Alexandra Foster | Ryan Nakamura |

### Creative Functions

| Function | Primary | Support |
|----------|---------|---------|
| Lighting / Photography | LUMEN | Canvas (F1-20) |
| Color / Palette | CHROMA | DES team |
| Sound / Music | ECHO | Resonance (F1-22) |
| Motion / Video | TEMPO | Frame (F1-21) |
| Scent / Sensory | FUME | — |

## Multi-Agent Combination Patterns

### Pattern: Technical Review
```
Scenario: "이 코드 리뷰해줘"
→ Domain expert (1명) + Security (Viper) if security-relevant
```

### Pattern: Campaign Planning
```
Scenario: "마케팅 캠페인 기획"
→ BRD lead + relevant channel lead + DES lead
→ Optional: LUMEN/CHROMA for visual direction
```

### Pattern: Content Production
```
Scenario: "화보 촬영 기획"
→ Model coordinator + LUMEN + CHROMA + TEMPO
→ Optional: Canvas/Frame for AI-assisted content
```

### Pattern: Cross-Domain
```
Scenario: "AI 기반 마케팅 자동화 시스템"
→ Technical (Forge/Ember) + Marketing (Growth lead) + Product (Priya)
```

## Locale Selection Rules

1. Korean text input → Korean personas first
2. English text input → Check context for locale preference
3. Japanese market topic → Japanese models + AMZ-KR-05 (cross-border expert)
4. Global/multi-market → Falcon Global + US marketing team
5. Explicit locale mention → Follow user's specification

## Scale Guidelines

| Request Complexity | Agent Count | Pattern |
|-------------------|-------------|---------|
| Simple question | 1 | Single Expert |
| Focused task | 1-2 | Single Expert or Pair |
| Multi-faceted project | 2-3 | Multi-Perspective |
| Full campaign/product | 3-5 | Full Team, Relay |

**Rule: Never spawn more than 5 agents for a single request.**
