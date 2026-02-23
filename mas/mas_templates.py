"""MAS Task Prompt Templates — loads 6 templates from task-templates.md."""

import os
import re

from . import mas_config as cfg
from .mas_constitution import CONSTITUTION_SUMMARY

# Template IDs
TECHNICAL_REVIEW = "technical_review"
MARKETING_CAMPAIGN = "marketing_campaign"
CONTENT_MODEL = "content_model"
CREATIVE_DIRECTION = "creative_direction"
SYNTHESIS = "synthesis"
GENERATIVE_AI = "generative_ai"
COMMERCE_TASK = "commerce_task"
SALES_TASK = "sales_task"
UIUX_TASK = "uiux_task"
CX_TASK = "cx_task"

# Fallback inline templates (used if task-templates.md not available)
_TEMPLATES = {
    TECHNICAL_REVIEW: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 기술 주제에 대해 전문가 관점에서 분석하고 답변해주세요.
코드가 제공된 경우 리뷰하고, 일반 질문인 경우 실무 경험 기반으로 깊이 있게 분석해주세요:

{user_request}

## Output Format
### Summary
[1-2줄 요약]

### Analysis
1. [핵심 포인트/이슈]
   - Detail: [설명]
   - Recommendation: [권장사항]

### Positive Aspects
- [what's good / 현재 접근법의 장점]

### Recommendations
1. [priority order]""",

    MARKETING_CAMPAIGN: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 마케팅 과제를 수행해주세요:

{user_request}

## Output Format
### Campaign Concept
[핵심 컨셉 1-2줄]

### Strategy
- Channel: [채널]
- Key Message: [핵심 메시지]
- Creative Direction: [크리에이티브 방향]

### Execution Plan
1. Phase 1: [description]
2. Phase 2: [description]

### KPIs
| Metric | Target |
|--------|--------|
| [metric] | [target] |""",

    CONTENT_MODEL: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 콘텐츠/촬영을 기획해주세요:

{user_request}

## Output Format
### Concept Direction
[컨셉 설명]

### Visual Mood
- Lighting: [조명 방향]
- Color Palette: [컬러]
- Styling: [스타일링]
- Location: [장소]

### Shot List
1. [shot description]

### References
- [reference links/descriptions]""",

    CREATIVE_DIRECTION: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({sense} 전문가)입니다.
다음 프로젝트의 {sense} 방향을 제안해주세요:

{user_request}

## Output Format
### {sense} Direction
[핵심 방향 설명]

### Detailed Specification
[구체적 스펙]

### Reference & Inspiration
[레퍼런스]

### Integration Notes
[다른 감각과의 조화 포인트]""",

    SYNTHESIS: """# Multi-Perspective Synthesis

## Original Request
{user_request}

## Agent Outputs

{agent_outputs}

## Synthesis Instructions
위 전문가들의 관점을 종합하여:

1. **Key Agreements**: 모든 전문가가 동의하는 핵심 포인트
2. **Tensions / Trade-offs**: 의견이 갈리는 부분과 그 이유
3. **Unified Recommendation**: 모든 관점을 통합한 최종 권고
4. **Action Items**: 구체적 실행 항목 (우선순위 순)

한국어로 작성하되, 전문 용어는 영어 병기 가능.
각 전문가의 관점이 균형있게 반영되도록 합성해주세요.""",

    GENERATIVE_AI: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 생성 작업을 도와주세요:

{user_request}

## Output Format
### Approach
[생성 접근 방법]

### Technical Pipeline
[사용할 모델/도구/파라미터]

### Prompt Engineering
[실제 생성 프롬프트 또는 파이프라인 코드]

### Quality Assurance
[품질 검증 기준]""",

    COMMERCE_TASK: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 커머스 과제를 수행해주세요:

{user_request}

## Output Format
### Analysis
[현황 분석 및 핵심 인사이트]

### Strategy
[전략 방향 및 근거]

### Execution Plan
1. [단계별 실행 계획]

### Metrics & KPIs
| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| [metric] | [target] | [how] |""",

    SALES_TASK: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 세일즈 과제를 수행해주세요:

{user_request}

## Output Format
### Situation Analysis
[현재 상황 분석]

### Strategy & Approach
[전략 및 접근 방식]

### Action Plan
1. [우선순위별 실행 항목]

### Expected Outcomes
[예상 결과 및 리스크]""",

    UIUX_TASK: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 UX/UI 설계 과제를 수행해주세요:

{user_request}

## Output Format
### User Context
[사용자 맥락 및 니즈 분석]

### Design Direction
[설계 방향 및 원칙]

### Specifications
[구체적 설계 사양]

### Rationale
[설계 근거 및 사용성 고려사항]""",

    CX_TASK: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 고객 경험 과제를 수행해주세요:

{user_request}

## Output Format
### Customer Insight
[고객 인사이트 분석]

### Strategy
[CX 전략 및 방향]

### Implementation Plan
1. [실행 계획]

### Impact & Measurement
[기대 효과 및 측정 방법]""",
}

# Domain → template mapping
DOMAIN_TEMPLATE_MAP = {
    "developers": TECHNICAL_REVIEW,
    "marketers": MARKETING_CAMPAIGN,
    "models": CONTENT_MODEL,
    "creatives": CREATIVE_DIRECTION,
    "commerce": COMMERCE_TASK,
    "sales": SALES_TASK,
    "uiux": UIUX_TASK,
    "cx": CX_TASK,
}

# Tag-based overrides
TAG_TEMPLATE_MAP = {
    "image-gen": GENERATIVE_AI,
    "video-gen": GENERATIVE_AI,
    "audio-gen": GENERATIVE_AI,
    "diffusion": GENERATIVE_AI,
    # Art Master Squad tags
    "ai-art": GENERATIVE_AI,
    "kling": GENERATIVE_AI,
    "higgsfield": GENERATIVE_AI,
    "seedance": GENERATIVE_AI,
    "nano-banana": GENERATIVE_AI,
    "veo3": GENERATIVE_AI,
    "img2video": GENERATIVE_AI,
    "prompt-engineering": GENERATIVE_AI,
    "multi-model": GENERATIVE_AI,
}


def get_template(template_id: str) -> str:
    """Get a template by ID."""
    return _TEMPLATES.get(template_id, _TEMPLATES[TECHNICAL_REVIEW])


def select_template(category: str, tags: list[str] = None) -> str:
    """Select appropriate template based on category and tags."""
    # Check tag overrides first
    if tags:
        for tag in tags:
            if tag in TAG_TEMPLATE_MAP:
                return TAG_TEMPLATE_MAP[tag]

    return DOMAIN_TEMPLATE_MAP.get(category, TECHNICAL_REVIEW)


def build_prompt(
    template_id: str,
    character_content: str,
    callsign: str,
    role: str,
    user_request: str,
    **kwargs,
) -> str:
    """Build a complete prompt from template + persona + request."""
    template = get_template(template_id)

    return template.format(
        character_content=character_content,
        constitution=CONSTITUTION_SUMMARY,
        callsign=callsign,
        role=role,
        user_request=user_request,
        sense=kwargs.get("sense", ""),
        agent_outputs=kwargs.get("agent_outputs", ""),
    )


def build_synthesis_prompt(user_request: str, agent_outputs: list[dict],
                           max_chars_per_agent: int = 0) -> str:
    """Build a synthesis prompt from multiple agent outputs.

    agent_outputs: [{"callsign": str, "role": str, "output": str}, ...]
    max_chars_per_agent: Truncate each agent output to this many chars (0 = no limit).
    """
    output_sections = []
    for ao in agent_outputs:
        text = ao['output']
        if max_chars_per_agent and len(text) > max_chars_per_agent:
            text = text[:max_chars_per_agent] + "\n\n[...truncated]"
        output_sections.append(
            f"### {ao['callsign']} ({ao['role']})\n{text}"
        )

    return build_prompt(
        SYNTHESIS,
        character_content="",
        callsign="MAS",
        role="Synthesizer",
        user_request=user_request,
        agent_outputs="\n\n".join(output_sections),
    )
