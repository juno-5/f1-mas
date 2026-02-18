"""MAS Constitution — P0 input blocking + P0 output filtering."""

import re

from . import mas_config as cfg

# P0 input patterns — absolute block (regex-based, no API call)
_P0_INPUT_PATTERNS = [
    # Illegal instructions / violence
    (r"(폭탄|bomb|explosive|무기|weapon|살인|murder|kill|테러|terror)", "illegal/violence"),
    (r"(자살.*방법|suicide.*method|how.*to.*kill)", "self-harm"),
    # CSAM
    (r"(아동.*성|child.*sex|minor.*porn|pedoph|아청법)", "csam"),
    # Identity theft
    (r"(주민등록번호|social.*security.*number|SSN.*\d{6})", "identity_theft"),
    (r"(신용카드.*번호|credit.*card.*number|CVV)", "identity_theft"),
    # Real person impersonation (명시적 사칭)
    (r"(인 것처럼|인 척|사칭.*해|pretend.*to.*be|impersonate)\s*(대통령|president|CEO)", "impersonation"),
    # Confidential data leak
    (r"(기밀.*유출|leak.*confidential|classified.*info)", "data_leak"),
]

# P1 input patterns — refuse with alternatives
_P1_INPUT_PATTERNS = [
    (r"(의료.*처방|진단.*해줘|medical.*diagnosis|prescribe)", "medical_advice"),
    (r"(법률.*자문|변호사.*의견|legal.*advice|attorney.*opinion)", "legal_advice"),
    (r"(투자.*추천|종목.*추천|financial.*advice|stock.*pick)", "financial_advice"),
    (r"(심리.*조종|manipulation.*technique|가스라이팅|gaslighting)", "manipulation"),
    (r"(딥페이크|deepfake).*실제.*인물", "deepfake_real_person"),
]

_p0_compiled = [(re.compile(p, re.IGNORECASE), label) for p, label in _P0_INPUT_PATTERNS]
_p1_compiled = [(re.compile(p, re.IGNORECASE), label) for p, label in _P1_INPUT_PATTERNS]

# P0 output patterns — strip from agent output
_OUTPUT_STRIP_PATTERNS = [
    re.compile(r"\b\d{6}[-\s]?\d{7}\b"),          # 주민등록번호-like
    re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),  # Credit card
    re.compile(r"(?i)api[_\s]?key[:\s=]+\S{10,}"),  # API key
    re.compile(r"(?i)(sk-[a-zA-Z0-9]{20,})"),       # Anthropic key
    re.compile(r"(?i)(password|passwd|pw)[:\s=]+\S+"),  # Passwords
]

CONSTITUTION_SUMMARY = """## Constitution Rules (MUST FOLLOW)
- P0 (BLOCK): No illegal instructions, CSAM, identity theft, confidential data leaks
- P1 (REFUSE): No professional medical/legal/financial advice, no manipulation techniques
- Always disclose AI nature when directly asked
- F1 brand safety: protect reputation, no competitor disparagement
- Respect model boundaries and consent for content involving personas
- No deepfakes of real persons, no NSFW content without explicit authorization"""


def check_input(text: str) -> tuple[bool, str]:
    """Check user input against constitution.

    Returns (blocked: bool, reason: str).
    blocked=True means P0 violation (hard block).
    blocked=False with non-empty reason means P1 (refuse with alternatives).
    """
    if not cfg.get_nested("constitution", "enabled", True):
        return False, ""

    # P0 check
    if cfg.get_nested("constitution", "p0_block", True):
        for pat, label in _p0_compiled:
            if pat.search(text):
                return True, f"P0 violation: {label}"

    # P1 check
    if cfg.get_nested("constitution", "p1_refuse", True):
        for pat, label in _p1_compiled:
            if pat.search(text):
                return False, f"P1: {label} — 전문가 상담을 권장합니다."

    return False, ""


def filter_output(text: str) -> str:
    """Strip sensitive patterns from agent output."""
    result = text
    for pat in _OUTPUT_STRIP_PATTERNS:
        result = pat.sub("[REDACTED]", result)
    return result
