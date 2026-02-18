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

# Fallback inline templates (used if task-templates.md not available)
_TEMPLATES = {
    TECHNICAL_REVIEW: """# Persona
{character_content}

{constitution}

# Task
당신은 {callsign} ({role})입니다.
다음 코드/아키텍처/시스템을 리뷰해주세요:

{user_request}

## Output Format
### Summary
[1-2줄 요약]

### Issues Found
1. [Severity: Critical/Major/Minor] [Description]
   - Location: [file:line]
   - Recommendation: [fix]

### Positive Aspects
- [what's good]

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
}

# Domain → template mapping
DOMAIN_TEMPLATE_MAP = {
    "developers": TECHNICAL_REVIEW,
    "marketers": MARKETING_CAMPAIGN,
    "models": CONTENT_MODEL,
    "creatives": CREATIVE_DIRECTION,
}

# Tag-based overrides
TAG_TEMPLATE_MAP = {
    "image-gen": GENERATIVE_AI,
    "video-gen": GENERATIVE_AI,
    "audio-gen": GENERATIVE_AI,
    "diffusion": GENERATIVE_AI,
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


def build_synthesis_prompt(user_request: str, agent_outputs: list[dict]) -> str:
    """Build a synthesis prompt from multiple agent outputs.

    agent_outputs: [{"callsign": str, "role": str, "output": str}, ...]
    """
    output_sections = []
    for ao in agent_outputs:
        output_sections.append(
            f"### {ao['callsign']} ({ao['role']})\n{ao['output']}"
        )

    return build_prompt(
        SYNTHESIS,
        character_content="",
        callsign="MAS",
        role="Synthesizer",
        user_request=user_request,
        agent_outputs="\n\n".join(output_sections),
    )
