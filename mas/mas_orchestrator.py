"""MAS Orchestrator — analyze request → select personas → spawn agents → synthesize."""

import re
import time

from . import mas_config as cfg
from . import mas_state as state
from .mas_persona_index import get_index, PersonaEntry, FUNCTION_PRIORITY
from .mas_templates import (
    build_prompt, build_synthesis_prompt, select_template,
    TECHNICAL_REVIEW, MARKETING_CAMPAIGN, CONTENT_MODEL,
    CREATIVE_DIRECTION, GENERATIVE_AI, SYNTHESIS,
)
from .mas_agent_runner import run_agent, run_agents_parallel, run_synthesis
from .mas_conversation import execute_pattern, determine_pattern

# Function detection patterns (regex pre-classification)
_FUNCTION_PATTERNS = {
    "system_architecture": re.compile(
        r"아키텍처|architecture|설계|design.*system|마이크로서비스|microservice|인프라.*설계",
        re.IGNORECASE,
    ),
    "security_audit": re.compile(
        r"보안|security|취약점|vulnerability|침투.*테스트|pentest|audit|사이버.*해킹|해킹.*(?:시도|공격|방어|탐지|차단)",
        re.IGNORECASE,
    ),
    "performance": re.compile(
        r"성능|performance|최적화|optimize|벤치마크|benchmark|프로파일|profil",
        re.IGNORECASE,
    ),
    "algorithm": re.compile(
        r"알고리즘|algorithm|자료.*구조|data.*struct|복잡도|complexity",
        re.IGNORECASE,
    ),
    "debugging": re.compile(
        r"디버그|debug|버그|bug|에러|error.*찾|root.*cause|원인.*분석",
        re.IGNORECASE,
    ),
    "ml_training": re.compile(
        r"ML|머신러닝|machine.*learn|학습|training|파인튜닝|fine.?tun|모델.*학습",
        re.IGNORECASE,
    ),
    "data_pipeline": re.compile(
        r"데이터.*파이프|data.*pipeline|ETL|데이터.*엔지니어|spark|배치.*처리",
        re.IGNORECASE,
    ),
    "sre_monitoring": re.compile(
        r"SRE|모니터링|monitoring|인시던트|incident|가용성|availability|장애",
        re.IGNORECASE,
    ),
    "nlp_llm": re.compile(
        r"NLP|자연어|natural.*language|LLM|언어.*모델|language.*model|토크나이저|tokeniz",
        re.IGNORECASE,
    ),
    "image_gen": re.compile(
        r"이미지.*생성|image.*gen|diffusion|stable.*diff|DALL|미드저니|midjourney",
        re.IGNORECASE,
    ),
    "video_gen": re.compile(
        r"영상.*생성|video.*gen|영상.*제작|시네마|cinema|VFX",
        re.IGNORECASE,
    ),
    "audio_gen": re.compile(
        r"음성.*생성|audio.*gen|TTS|voice.*clon|음악.*생성|music.*gen",
        re.IGNORECASE,
    ),
    "frontend_ui": re.compile(
        r"프론트엔드|frontend|UI|UX|리액트|react|웹.*개발|web.*dev",
        re.IGNORECASE,
    ),
    "product_ux": re.compile(
        r"제품.*기획|product.*plan|PM|프로덕트|product.*manage|로드맵|roadmap",
        re.IGNORECASE,
    ),
    "database_storage": re.compile(
        r"데이터베이스|database|DB|SQL|스토리지|storage|쿼리|query",
        re.IGNORECASE,
    ),
    "commerce_strategy": re.compile(
        r"커머스|commerce|이커머스|e.?commerce|매출|revenue|전환율|conversion|CRO",
        re.IGNORECASE,
    ),
    "growth_hacking": re.compile(
        r"그로스|growth|성장|UA|유저.*획득|acquisition|리텐션|retention|AARRR",
        re.IGNORECASE,
    ),
    "amazon_ops": re.compile(
        r"아마존|amazon|AWS.*마켓|FBA|셀러|seller|PPC",
        re.IGNORECASE,
    ),
    "tiktok_shortform": re.compile(
        r"틱톡|tiktok|숏폼|short.?form|릴스|reels|쇼츠|shorts",
        re.IGNORECASE,
    ),
    "brand_strategy": re.compile(
        r"브랜딩|branding|브랜드.*전략|brand.*strateg|네이밍|naming|\bBI\b|\bCI\b",
        re.IGNORECASE,
    ),
    "visual_design": re.compile(
        r"디자인|design|비주얼|visual|로고|logo|UI.*디자인|패키지.*디자인",
        re.IGNORECASE,
    ),
    "lighting_photography": re.compile(
        r"조명|lighting|라이팅|촬영|photography|화보|lookbook",
        re.IGNORECASE,
    ),
    "color_palette": re.compile(
        r"컬러|color|팔레트|palette|색감|색상",
        re.IGNORECASE,
    ),
    "sound_music": re.compile(
        r"사운드|sound|음악|music|음향|acoustic|소닉|sonic",
        re.IGNORECASE,
    ),
    "motion_video": re.compile(
        r"모션|motion|영상.*편집|video.*edit|애니메이션|animation",
        re.IGNORECASE,
    ),
    # Commerce team functions
    "ecommerce_platform": re.compile(
        r"이커머스.*플랫폼|ecommerce.*platform|재고|inventory|물류|logistics|배송|delivery|추천.*알고리즘|recommendation",
        re.IGNORECASE,
    ),
    "conversion_optimization": re.compile(
        r"전환율.*최적화|conversion.*optim|\bCRO\b|A/B.*테스트|a.?b.*test|장바구니.*이탈|cart.*abandon|체크아웃|checkout",
        re.IGNORECASE,
    ),
    "marketplace_strategy": re.compile(
        r"마켓플레이스|marketplace|셀러.*생태계|seller.*ecosystem|글로벌.*커머스|cross.?border",
        re.IGNORECASE,
    ),
    "loyalty_retention": re.compile(
        r"로열티|loyalty|구독.*커머스|subscription|\bLTV\b|생애.*가치|lifetime.*value|리피트|repeat",
        re.IGNORECASE,
    ),
    # Sales team functions
    "enterprise_sales": re.compile(
        r"엔터프라이즈.*세일즈|enterprise.*sales|대형.*계약|MEDDIC|CHALLENGER|딜|deal.*클로징|closing",
        re.IGNORECASE,
    ),
    "sales_methodology": re.compile(
        r"세일즈.*코칭|sales.*coach|revenue.*intelligence|세일즈.*방법론|sales.*method|enablement",
        re.IGNORECASE,
    ),
    "plg_sales": re.compile(
        r"\bPLG\b|product.?led.*growth|SaaS.*세일즈|saas.*sales|채널.*파트너|channel.*partner",
        re.IGNORECASE,
    ),
    "account_management": re.compile(
        r"계정.*관리|account.*manage|\bNRR\b|갱신|renewal|업셀|upsell|cross.?sell",
        re.IGNORECASE,
    ),
    "sales_engineering": re.compile(
        r"기술.*세일즈|sales.*engineer|\bPOC\b|데모|demo|value.*assess|솔루션.*아키텍|solution.*architect",
        re.IGNORECASE,
    ),
    # UIUX team functions
    "design_strategy": re.compile(
        r"디자인.*전략|design.*strateg|\bCDO\b|\bHCD\b|디자인.*원칙|design.*principle|design.*direction",
        re.IGNORECASE,
    ),
    "interaction_design": re.compile(
        r"인터랙션|interaction.*design|모션.*디자인|motion.*design|마이크로.*인터랙션|micro.?interaction|제스처|gesture",
        re.IGNORECASE,
    ),
    "user_research": re.compile(
        r"사용자.*리서치|user.*research|사용성.*테스트|usability|유저.*인터뷰|user.*interview|접근성|accessibility|a11y",
        re.IGNORECASE,
    ),
    "design_system": re.compile(
        r"디자인.*시스템|design.*system|컴포넌트.*라이브러리|component.*library|Storybook|디자인.*토큰|design.*token",
        re.IGNORECASE,
    ),
    "ux_engineering": re.compile(
        r"UX.*엔지니어|ux.*engineer|프로토타입|prototype|Framer|핸드오프|handoff|디자인.*개발|design.*develop",
        re.IGNORECASE,
    ),
    # CX team functions
    "cx_strategy": re.compile(
        r"CX.*전략|cx.*strateg|고객.*경험.*전략|customer.*experience.*strateg|\bVOC\b|\bNPS\b|\bCSAT\b|\bCES\b",
        re.IGNORECASE,
    ),
    "customer_success": re.compile(
        r"고객.*성공|customer.*success|온보딩|onboarding|이탈.*방지|churn.*prevent|CS.*플레이북",
        re.IGNORECASE,
    ),
    "cx_analytics": re.compile(
        r"고객.*분석|customer.*analytics|감성.*분석|sentiment|이탈.*예측|churn.*predict|VoC.*분석",
        re.IGNORECASE,
    ),
    "omnichannel_cx": re.compile(
        r"옴니채널|omnichannel|AI.*고객지원|ai.*support|챗봇|chatbot|콜센터|call.*center",
        re.IGNORECASE,
    ),
    "cx_operations": re.compile(
        r"CS.*운영|cs.*operation|\bQA\b.*\bQC\b|품질.*관리|quality.*manage|\bSLA\b|서비스.*레벨",
        re.IGNORECASE,
    ),
    # --- Missing function patterns (auto-zero cycle #3) ---
    "cloud_container": re.compile(
        r"도커|docker|쿠버네티스|kubernetes|k8s|컨테이너|container|클라우드|cloud|AWS|GCP|Azure|파드|pod|헬름|helm",
        re.IGNORECASE,
    ),
    "networking": re.compile(
        r"네트워크|network|TCP|UDP|DNS|라우팅|routing|프로토콜|protocol|소켓|socket|HTTP|gRPC|websocket|로드.*밸런|load.*balanc",
        re.IGNORECASE,
    ),
    "vision_multimodal": re.compile(
        r"비전|vision|이미지.*분석|image.*analy|객체.*인식|object.*detect|멀티모달|multimodal|OCR|세그멘테이션|segmentation|YOLO|CNN",
        re.IGNORECASE,
    ),
    "ai_compiler": re.compile(
        r"컴파일러|compiler|런타임|runtime|LLVM|코드.*생성|code.*gen|인터프리터|interpreter|JIT|바이트코드|bytecode|AST|파서|parser",
        re.IGNORECASE,
    ),
    "formal_verification": re.compile(
        r"형식.*검증|formal.*verif|타입.*이론|type.*theory|정형.*명세|정적.*분석|static.*analy|증명|proof.*assist|Coq|Lean|Isabelle",
        re.IGNORECASE,
    ),
    "quantum": re.compile(
        r"양자|quantum|큐빗|qubit|양자.*게이트|quantum.*gate|양자.*회로|quantum.*circuit|Qiskit|얽힘|entangle",
        re.IGNORECASE,
    ),
    "engineering_mgmt": re.compile(
        r"엔지니어링.*관리|eng.*manage|코드.*리뷰|code.*review|스프린트|sprint|애자일|agile|스크럼|scrum|기술.*리더|tech.*lead|1on1",
        re.IGNORECASE,
    ),
}


def _log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [orchestrator] {msg}", flush=True)


class Orchestrator:
    def __init__(self):
        self._index = get_index()

    def analyze_request(self, query: str, pattern: str = None) -> dict:
        """Analyze user request: detect domain, function, locale, complexity.

        Returns {"domains": [...], "functions": [...], "locale": str,
                 "complexity": str, "agent_count": int}.
        """
        # Domain detection
        domains = self._index.detect_domain(query)

        # Function detection (regex 80%)
        functions = []
        for func_key, pattern in _FUNCTION_PATTERNS.items():
            if pattern.search(query):
                functions.append(func_key)

        # Locale detection
        locale = self._index.detect_locale(query)

        # Complexity estimation
        query_len = len(query)
        func_count = len(functions)

        if query_len < 50 and func_count <= 1:
            complexity = "simple"
            agent_count = 1
        elif query_len < 200 and func_count <= 2:
            complexity = "focused"
            agent_count = min(2, func_count + 1)
        elif len(domains) > 1 or func_count >= 3:
            complexity = "full_project"
            agent_count = min(5, func_count + 1)
        else:
            complexity = "multi_faceted"
            agent_count = min(3, func_count + 1)

        # Pattern-based minimum: multi_perspective needs 2+, full_team needs 3+
        if pattern == "multi_perspective":
            agent_count = max(agent_count, 2)
        elif pattern == "full_team":
            agent_count = max(agent_count, 3)

        # Ensure at least 1 agent
        agent_count = max(1, agent_count)

        return {
            "domains": domains,
            "functions": functions if functions else [self._default_function(domains[0])],
            "locale": locale,
            "complexity": complexity,
            "agent_count": agent_count,
        }

    def _default_function(self, domain: str) -> str:
        """Get default function for a domain."""
        defaults = {
            "developers": "system_architecture",
            "marketers": "brand_strategy",
            "models": "lighting_photography",
            "creatives": "color_palette",
            "commerce": "ecommerce_platform",
            "sales": "enterprise_sales",
            "uiux": "design_strategy",
            "cx": "cx_strategy",
        }
        return defaults.get(domain, "system_architecture")

    def select_personas(self, analysis: dict) -> list[PersonaEntry]:
        """Select optimal personas based on analysis.

        Strategy: pick top-1 per function first (round-robin), then fill remaining slots.
        """
        selected = []
        seen_ids = set()
        locale = analysis["locale"]
        max_count = analysis["agent_count"]

        # Pass 1: Pick top-1 per function (best locale match)
        for func in analysis["functions"]:
            if len(selected) >= max_count:
                break
            candidates = self._index.by_function(func)
            if not candidates:
                continue

            picked = None
            # Prefer locale match
            for c in candidates:
                if c.locale == locale and c.id not in seen_ids:
                    picked = c
                    break
            if not picked:
                for c in candidates:
                    if c.id not in seen_ids:
                        picked = c
                        break
            if picked:
                selected.append(picked)
                seen_ids.add(picked.id)

        # Pass 2: Fill remaining slots from all functions' 2nd/3rd choices
        if len(selected) < max_count:
            for func in analysis["functions"]:
                candidates = self._index.by_function(func)
                for c in candidates:
                    if c.id not in seen_ids and len(selected) < max_count:
                        selected.append(c)
                        seen_ids.add(c.id)
                if len(selected) >= max_count:
                    break

        # Fallback: if no function-based selection, use domain + locale
        if not selected:
            domain = analysis["domains"][0]
            domain_personas = self._index.by_category(domain)
            locale_match = [p for p in domain_personas if p.locale == locale]
            pool = locale_match if locale_match else domain_personas
            selected = pool[:max_count]

        return selected[:max_count]

    def execute(
        self,
        request_id: str,
        query: str,
        persona_ids: list[str] = None,
        pattern: str = None,
    ):
        """Full orchestration: analyze → select → spawn → synthesize.

        This runs synchronously (called from a background thread).
        """
        # 1. Analyze
        state.update_request(request_id, status="analyzing")
        analysis = self.analyze_request(query, pattern=pattern)
        _log(f"[{request_id}] Analysis: {analysis}")

        # 2. Select personas
        state.update_request(request_id, status="assembling",
                             domain=analysis["domains"][0],
                             locale=analysis["locale"])

        if persona_ids:
            # Forced persona selection
            personas = [self._index.get(pid) for pid in persona_ids]
            personas = [p for p in personas if p is not None]
        else:
            personas = self.select_personas(analysis)

        if not personas:
            state.update_request(request_id, status="failed",
                                 error="no suitable personas found")
            return

        persona_id_list = [p.id for p in personas]
        state.update_request(request_id, selected_personas=persona_id_list)

        _log(f"[{request_id}] Selected: {[p.callsign for p in personas]}")

        # 3. Notify Slack (if enabled)
        self._slack_notify_assembly(request_id, query, personas, analysis)

        # 4. Determine pattern
        if pattern:
            conv_pattern = pattern
        else:
            conv_pattern = determine_pattern(analysis, personas)

        state.update_request(request_id, pattern=conv_pattern)
        _log(f"[{request_id}] Pattern: {conv_pattern}")

        # 5. Execute pattern
        state.update_request(request_id, status="running")
        result = execute_pattern(
            request_id=request_id,
            query=query,
            personas=personas,
            pattern=conv_pattern,
            index=self._index,
        )

        # 6. Update state with result
        if result.get("error"):
            state.update_request(request_id, status="failed",
                                 error=result["error"])
            _log(f"[{request_id}] Failed: {result['error']}")
        else:
            synthesis = result.get("synthesis", "")
            state.update_request(request_id,
                                 status="completed",
                                 synthesis=synthesis)
            _log(f"[{request_id}] Completed ({len(synthesis)} chars)")

        # 7. Slack final update
        self._slack_notify_complete(request_id)

        state.record_event("complete" if not result.get("error") else "error",
                           f"Request {request_id} {state.get_request(request_id).status}",
                           request_id)

    def _slack_notify_assembly(self, request_id, query, personas, analysis):
        """Send Slack notification about team assembly."""
        if not cfg.get_nested("slack", "enabled", False):
            return
        try:
            from .mas_slack import notify_assembly
            notify_assembly(request_id, query, personas, analysis)
        except Exception as e:
            _log(f"Slack assembly notify failed: {e}")

    def _slack_notify_complete(self, request_id):
        """Send Slack notification about completion."""
        if not cfg.get_nested("slack", "enabled", False):
            return
        try:
            from .mas_slack import notify_complete
            notify_complete(request_id)
        except Exception as e:
            _log(f"Slack complete notify failed: {e}")
