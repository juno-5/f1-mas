#!/usr/bin/env python3
"""library-scanner.py — Slack 히스토리 + 에이전트 워크스페이스에서 문서 수집 → 도메인별 분류 → 라이브러리 정리.

Modes:
  --mode=status              스캔 상태, 채널 수, 링크 수
  --mode=scan                Slack 히스토리 스캔 → 링크 추출
  --mode=fetch               URL별 문서 내용 가져오기 (Notion API / HTTP)
  --mode=classify            문서를 8개 도메인으로 분류
  --mode=render              references.md 머지용 마크다운 생성
  --mode=workspace           에이전트 워크스페이스 스캔 → 생성 문서 발견·분류
  --mode=workspace-collect   워크스페이스 문서를 library 디렉토리에 복사
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

# ---------------------------------------------------------------------------
# Credential loaders
# ---------------------------------------------------------------------------

F1CREW_JSON = Path("~/.f1crew/f1crew.json").expanduser()
CREDENTIALS_ENV = Path("~/.f1crew/credentials/.env").expanduser()
STATE_FILE = Path("~/.f1crew/shared/library-scan-state.json").expanduser()
LIBRARY_DIR = Path("~/projects/mayacrew-f1crew/f1-mas/library").expanduser()


def _load_slack_token() -> str:
    with open(F1CREW_JSON) as f:
        cfg = json.load(f)
    return cfg["channels"]["slack"]["accounts"]["zero"]["botToken"]


def _load_notion_token() -> str:
    if CREDENTIALS_ENV.exists():
        for line in CREDENTIALS_ENV.read_text().splitlines():
            line = line.strip()
            if line.startswith("NOTION_API_TOKEN="):
                return line.split("=", 1)[1].strip().strip("\"'")
    return os.environ.get("NOTION_API_TOKEN", "")


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"channels": {}, "processed_urls": {}, "last_full_scan": None}


def _save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only for Slack, requests for Notion)
# ---------------------------------------------------------------------------

def _slack_api(method: str, token: str, params: dict = None,
               post: bool = False) -> dict:
    """Call Slack Web API. Returns parsed JSON."""
    import urllib.request
    import urllib.parse
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if post or method in ("conversations.join",):
        headers["Content-Type"] = "application/json"
        data = json.dumps(params or {}).encode()
    elif params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers, data=data)
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())


def _notion_api(endpoint: str, token: str, method: str = "GET",
                body: dict = None) -> dict:
    """Call Notion API v2025-09-03."""
    import urllib.request
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def _http_get_text(url: str, max_chars: int = 3000) -> str:
    """Fetch a URL and return plain text content (truncated)."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "F1Crew-LibraryScanner/1.0"
        })
        resp = urllib.request.urlopen(req, timeout=15)
        ct = resp.headers.get("Content-Type", "")
        raw = resp.read(100_000).decode("utf-8", errors="replace")
        if "html" in ct.lower():
            # Strip HTML tags
            raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.S)
            raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S)
            raw = re.sub(r"<[^>]+>", " ", raw)
            raw = re.sub(r"\s+", " ", raw).strip()
        return raw[:max_chars]
    except Exception as e:
        return f"(fetch error: {e})"


# ---------------------------------------------------------------------------
# URL extraction regexes
# ---------------------------------------------------------------------------

GDRIVE_RE = re.compile(
    r"https?://(?:drive|docs)\.google\.com/[^\s>|)\"']+", re.I
)
NOTION_RE = re.compile(
    r"https?://(?:www\.)?notion\.(?:so|site)/[^\s>|)\"']+", re.I
)
SLACK_LINK_RE = re.compile(r"<(https?://[^>|]+)(?:\|[^>]*)?>")

DOC_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".csv"}


def _extract_urls(text: str) -> list[dict]:
    """Extract document URLs from Slack message text."""
    results = []
    seen = set()

    # Slack-formatted links first: <url|label>
    for m in SLACK_LINK_RE.finditer(text):
        url = m.group(1)
        if url not in seen:
            seen.add(url)
            results.append({"url": url, "type": _classify_url(url)})

    # Plain URLs
    for pattern, url_type in [
        (GDRIVE_RE, "gdrive"),
        (NOTION_RE, "notion"),
    ]:
        for m in pattern.finditer(text):
            url = m.group(0).rstrip(".,;:")
            if url not in seen:
                seen.add(url)
                results.append({"url": url, "type": url_type})

    return [r for r in results if r["type"] in ("gdrive", "notion", "doc_url")]


def _classify_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    path = parsed.path.lower()
    if "drive.google.com" in host or "docs.google.com" in host:
        return "gdrive"
    if "notion.so" in host or "notion.site" in host:
        return "notion"
    ext = Path(path).suffix.lower()
    if ext in DOC_EXTENSIONS:
        return "doc_url"
    return "other"


# ---------------------------------------------------------------------------
# Domain classification
# ---------------------------------------------------------------------------

AGENT_DOMAIN_MAP = {
    "dev-master": "developers",
    "mkt-master": "marketers",
    "art-master": "creatives",
    "commerce-master": "commerce",
    "sales-master": "sales",
    "uiux-master": "uiux",
    "cx-master": "cx",
}

# Agent workspace scanning — system files to exclude
WORKSPACE_DIR = Path("~/.f1crew").expanduser()
WORKSPACE_SYSTEM_FILES = {
    "CLAUDE.md", "IDENTITY.md", "SOUL.md", "MEMORY.md",
    "AGENTS.md", "HEARTBEAT.md", "TOOLS.md", "USER.md",
}
WORKSPACE_EXCLUDE_DIRS = {"memory", ".openclaw", ".pi"}

# Memory file domain normalization — maps non-standard Domain fields to library domains
MEMORY_DOMAIN_NORMALIZE = {
    # English exact matches
    "developers": "developers", "marketers": "marketers", "creatives": "creatives",
    "commerce": "commerce", "sales": "sales", "uiux": "uiux", "cx": "cx", "models": "models",
    # Korean domain names
    "개발": "developers", "마케팅": "marketers", "크리에이티브": "creatives",
    "커머스": "commerce", "세일즈": "sales", "디자인": "uiux", "고객경험": "cx", "모델": "models",
}

# Keyword patterns for normalizing memory Domain field to library domains
MEMORY_DOMAIN_PATTERNS = [
    (re.compile(r"dev|infra|hpc|gpu|server|backend|frontend|\bapi\b|code|deploy|token.?econ|개발|인프라|클라우드|보안|소프트웨어|딥러닝|머신러닝|병렬", re.I), "developers"),
    (re.compile(r"market|ads?\b|campaign|seo|brand|growth|advertis|social.?media|광고|마케|브랜드", re.I), "marketers"),
    (re.compile(r"creative|visual|\bdesign\b|video|photo|music|audio|color|motion|film|크리에이|영상|음악|사운드|감성", re.I), "creatives"),
    (re.compile(r"commerce|shop|amazon|ecommerce|seller|fulfillment|logistics|물류|커머스|배송|셀러|입고", re.I), "commerce"),
    (re.compile(r"\bsales\b|deal\b|pipeline|revenue|pricing|negotiat|세일즈|영업|거래", re.I), "sales"),
    (re.compile(r"\bux\b|\bui\b|usability|figma|prototype|wireframe|interaction|user.?research|\bUX\b|\bUI\b", re.I), "uiux"),
    (re.compile(r"\bcx\b|\bcs\b|support|customer|service|healthcare|health|의료|환자|서비스.?운영|고객", re.I), "cx"),
    (re.compile(r"fashion|casting|shoot|runway|editorial|beauty|모델|캐스팅|촬영|패션|뷰티", re.I), "models"),
]

# Workspace owner → default library domain (all agents)
AGENT_LIBRARY_DOMAIN = {
    **AGENT_DOMAIN_MAP,
    "zero": "developers", "main": "developers",
    # Dev personas — default to developers, but content-based override applies
    **{name: "developers" for name in [
        "anvil", "axiom", "blaze", "bridge", "chain", "cortex", "ember", "flux",
        "forge", "hex", "kernel", "ledger", "luffy", "mint", "mirage", "nova",
        "pixel", "prism", "pulse", "sage", "sentinel", "trace", "vault", "viper", "wire",
    ]},
}


def _normalize_memory_domain(domain_field: str, tags: str = "", title: str = "") -> str | None:
    """Normalize a memory file's Domain field to a library domain."""
    if not domain_field:
        return None
    dl = domain_field.strip().lower()
    # Exact match
    if dl in MEMORY_DOMAIN_NORMALIZE:
        return MEMORY_DOMAIN_NORMALIZE[dl]
    # Pattern match on domain field + tags + title
    combined = f"{domain_field} {tags} {title}"
    for pattern, lib_domain in MEMORY_DOMAIN_PATTERNS:
        if pattern.search(combined):
            return lib_domain
    return None


def _parse_memory_file(filepath: Path) -> dict | None:
    """Parse a structured memory .md file and extract metadata."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    lines = text.splitlines()
    meta = {"title": "", "source": "", "date": "", "domain": "", "tags": "",
            "relevance": 0.0, "type": "", "agent": "", "entities": "", "insight": ""}
    for line in lines:
        line = line.strip()
        if line.startswith("# ") and not meta["title"]:
            meta["title"] = line[2:].strip()
        elif line.startswith("- **Source**:"):
            meta["source"] = line.split(":", 1)[1].strip().lstrip("*").rstrip("*").strip()
        elif line.startswith("- **Date**:"):
            meta["date"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Domain**:"):
            meta["domain"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Tags**:"):
            meta["tags"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Relevance**:"):
            try:
                meta["relevance"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("- **Type**:"):
            meta["type"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Agent**:"):
            meta["agent"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Entities**:"):
            meta["entities"] = line.split(":", 1)[1].strip()
    # Extract insight section
    in_insight = False
    insight_lines = []
    for line in lines:
        if line.strip().startswith("## 핵심 인사이트"):
            in_insight = True
            continue
        if in_insight:
            if line.strip().startswith("## "):
                break
            if line.strip():
                insight_lines.append(line.strip())
    meta["insight"] = " ".join(insight_lines)
    return meta if meta["title"] else None


# Product names that map to product-level library subdirectories
PRODUCT_NAMES = ["supermembers", "superchart", "cosduck", "heeda", "kimchip", "mapda", "medihair"]

# Agent domain → functional subdomain mapping for product paths
_AGENT_FUNC_MAP = {
    "art-master": "marketing",    # creatives work is marketing-adjacent for products
    "mkt-master": "marketing",
    "dev-master": "dev",
    "commerce-master": "marketing",
    "sales-master": "sales",
    "uiux-master": "dev",
    "cx-master": "cx",
}

CHANNEL_NAME_PATTERNS = [
    (re.compile(r"dev|eng|code|backend|frontend|infra", re.I), "developers"),
    (re.compile(r"mkt|marketing|campaign|brand|growth", re.I), "marketers"),
    (re.compile(r"art|creative|visual|photo|video", re.I), "creatives"),
    (re.compile(r"commerce|shop|amazon|ecommerce|qoo10", re.I), "commerce"),
    (re.compile(r"sales|deal|biz|business", re.I), "sales"),
    (re.compile(r"uiux|ux|ui|design.?system|product.?design", re.I), "uiux"),
    (re.compile(r"cx|cs|support|customer|service", re.I), "cx"),
    (re.compile(r"model|casting|shoot|fashion", re.I), "models"),
]

DOMAIN_KEYWORDS = {
    "developers": {
        "api": 3, "sdk": 3, "deploy": 2, "code": 2, "git": 2,
        "server": 2, "backend": 3, "frontend": 2, "database": 2,
        "docker": 2, "kubernetes": 2, "ci/cd": 3, "bug": 1,
        "architecture": 3, "microservice": 3, "rest": 2, "graphql": 2,
        "terraform": 2, "aws": 2, "python": 2, "typescript": 2,
    },
    "marketers": {
        "campaign": 3, "ad": 2, "roi": 3, "funnel": 2, "seo": 3,
        "brand": 2, "instagram": 2, "tiktok": 2, "facebook": 2,
        "meta ads": 3, "google ads": 3, "ctr": 3, "conversion": 2,
        "influencer": 2, "content marketing": 3, "naver": 2,
    },
    "creatives": {
        "design": 2, "visual": 3, "photo": 2, "video": 2, "render": 2,
        "prompt": 2, "storyboard": 3, "illustration": 3, "creative": 2,
        "color": 2, "motion": 3, "3d": 2, "ai generation": 3,
    },
    "commerce": {
        "amazon": 3, "qoo10": 3, "tiktok shop": 3, "listing": 2,
        "inventory": 2, "order": 2, "sku": 3, "marketplace": 2,
        "fulfillment": 3, "ecommerce": 3, "shipping": 2, "seller": 2,
    },
    "sales": {
        "deal": 3, "pipeline": 3, "prospect": 2, "lead": 2, "crm": 3,
        "negotiation": 2, "contract": 2, "pricing": 2, "revenue": 2,
        "quota": 3, "plg": 3, "outbound": 2, "inbound": 2,
    },
    "uiux": {
        "figma": 3, "prototype": 3, "usability": 3, "user research": 3,
        "wireframe": 3, "component": 2, "design system": 3, "a11y": 2,
        "interaction": 2, "ux": 2, "ui": 2, "heuristic": 2,
    },
    "cx": {
        "customer": 2, "support": 2, "ticket": 3, "sla": 3, "nps": 3,
        "voc": 3, "faq": 2, "complaint": 2, "escalation": 3,
        "satisfaction": 2, "onboarding": 2, "churn": 2,
    },
    "models": {
        "shooting": 3, "casting": 3, "agency": 2, "model": 2,
        "photoshoot": 3, "lookbook": 3, "runway": 3, "fitting": 2,
        "editorial": 3, "fashion": 2, "beauty": 2, "pose": 2,
    },
}


def classify_by_channel(channel_name: str) -> str | None:
    """Classify domain by channel name pattern."""
    for pattern, domain in CHANNEL_NAME_PATTERNS:
        if pattern.search(channel_name):
            return domain
    return None


def classify_by_content(text: str) -> tuple[str, float]:
    """Classify domain by content keywords. Returns (domain, score)."""
    text_lower = text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for kw, weight in keywords.items():
            count = text_lower.count(kw.lower())
            if count:
                score += weight * min(count, 3)
        if score > 0:
            scores[domain] = score
    if not scores:
        return "general", 0.0
    best = max(scores, key=scores.get)
    return best, scores[best]


# ---------------------------------------------------------------------------
# Notion content extraction
# ---------------------------------------------------------------------------

def _notion_extract_page_id(url: str) -> str | None:
    """Extract page ID (UUID) from Notion URL."""
    path = urlparse(url).path
    # Notion URLs end with {title}-{32hex} or just {32hex}
    m = re.search(r"([0-9a-f]{32})", path.replace("-", ""))
    if m:
        h = m.group(1)
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
    return None


def _notion_blocks_to_text(blocks: list, depth: int = 0) -> str:
    """Convert Notion blocks to plain text."""
    lines = []
    for b in blocks:
        btype = b.get("type", "")
        data = b.get(btype, {})
        rich_texts = data.get("rich_text", data.get("text", []))
        text = "".join(rt.get("plain_text", "") for rt in rich_texts if isinstance(rt, dict))
        if btype.startswith("heading"):
            level = btype[-1] if btype[-1].isdigit() else "2"
            lines.append(f"{'#' * int(level)} {text}")
        elif btype in ("paragraph", "quote", "callout"):
            lines.append(text)
        elif btype in ("bulleted_list_item", "numbered_list_item", "to_do"):
            prefix = "  " * depth + "- "
            lines.append(f"{prefix}{text}")
        elif btype == "code":
            lines.append(f"```\n{text}\n```")
        elif text:
            lines.append(text)
    return "\n".join(lines)


def fetch_notion_page(url: str, token: str) -> dict:
    """Fetch Notion page title + content."""
    page_id = _notion_extract_page_id(url)
    if not page_id:
        return {"url": url, "type": "notion", "error": "Could not extract page ID"}

    page = _notion_api(f"pages/{page_id}", token)
    if "error" in page:
        return {"url": url, "type": "notion", "error": page["error"]}

    # Extract title from properties
    title = ""
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            title = "".join(
                t.get("plain_text", "")
                for t in prop.get("title", [])
            )
            break

    # Fetch content blocks
    blocks_resp = _notion_api(f"blocks/{page_id}/children?page_size=100", token)
    blocks = blocks_resp.get("results", [])
    content = _notion_blocks_to_text(blocks)

    return {
        "url": url,
        "type": "notion",
        "title": title or "(Untitled)",
        "content_summary": content[:500],
        "full_text": content[:3000],
        "error": None,
    }


# ---------------------------------------------------------------------------
# Google Drive content extraction
# ---------------------------------------------------------------------------

def _gdrive_extract_file_id(url: str) -> str | None:
    """Extract file ID from Google Drive/Docs URL."""
    # /d/{id}/ pattern
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    # /document/d/{id}
    m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    # /spreadsheets/d/{id}
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    # /file/d/{id}
    m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    return None


def fetch_gdrive_doc(url: str) -> dict:
    """Fetch Google Drive document. Try gog CLI, fallback to public export."""
    file_id = _gdrive_extract_file_id(url)
    if not file_id:
        return {"url": url, "type": "gdrive", "error": "Could not extract file ID",
                "title": unquote(urlparse(url).path.split("/")[-1])}

    # Try gog CLI
    import subprocess
    try:
        result = subprocess.run(
            ["gog", "drive", "read", file_id],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()
            # Extract title from first line if possible
            lines = content.splitlines()
            title = lines[0].strip("# ") if lines else file_id
            return {
                "url": url, "type": "gdrive", "title": title,
                "content_summary": content[:500],
                "full_text": content[:3000],
                "error": None,
            }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: try public export URL
    export_url = f"https://docs.google.com/document/d/{file_id}/export?format=txt"
    content = _http_get_text(export_url)
    if "error" not in content.lower() and len(content) > 50:
        lines = content.splitlines()
        title = lines[0].strip() if lines else file_id
        return {
            "url": url, "type": "gdrive", "title": title,
            "content_summary": content[:500],
            "full_text": content[:3000],
            "error": None,
        }

    return {
        "url": url, "type": "gdrive",
        "title": f"Google Doc ({file_id[:8]}...)",
        "content_summary": "",
        "full_text": "",
        "error": "Could not fetch content (private document or unsupported format)",
    }


# ---------------------------------------------------------------------------
# Mode implementations
# ---------------------------------------------------------------------------

def mode_status(args):
    """Show current scan state."""
    state = _load_state()
    token = _load_slack_token()

    # List accessible channels
    resp = _slack_api("conversations.list", token, {
        "types": "public_channel,private_channel",
        "limit": 200, "exclude_archived": "true"
    })
    channels = resp.get("channels", [])

    output = {
        "last_full_scan": state.get("last_full_scan"),
        "total_processed_urls": len(state.get("processed_urls", {})),
        "channels_accessible": len(channels),
        "channels_scanned": len(state.get("channels", {})),
        "channel_list": [
            {"id": ch["id"], "name": ch.get("name", "?"),
             "members": ch.get("num_members", 0)}
            for ch in sorted(channels, key=lambda c: c.get("num_members", 0), reverse=True)[:20]
        ],
        "notion_token_available": bool(_load_notion_token()),
        "library_dir_exists": LIBRARY_DIR.exists(),
        "domains": list(DOMAIN_KEYWORDS.keys()),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def mode_scan(args):
    """Scan Slack history for document links."""
    token = _load_slack_token()
    state = _load_state()
    limit = args.limit or 200
    since = args.since or "0"

    # Get channels
    channel_name_map = {}
    if args.channel:
        channel_ids = [args.channel]
    else:
        resp = _slack_api("conversations.list", token, {
            "types": "public_channel,private_channel,im,mpim",
            "limit": 200, "exclude_archived": "true"
        })
        channels = resp.get("channels", [])
        channel_ids = [ch["id"] for ch in channels]
        channel_name_map = {ch["id"]: ch.get("name", ch["id"]) for ch in channels}

    all_links = []
    channels_scanned = 0

    for ch_id in channel_ids:
        ch_name = channel_name_map.get(ch_id, "")
        if not ch_name:
            try:
                ch_info = _slack_api("conversations.info", token, {"channel": ch_id})
                ch_name = ch_info.get("channel", {}).get("name", ch_id)
            except Exception:
                ch_name = ch_id

        # Determine since timestamp for this channel
        ch_since = state.get("channels", {}).get(ch_id, {}).get("last_scan_ts", since)

        params = {"channel": ch_id, "limit": min(limit, 200)}
        if ch_since and ch_since != "0":
            params["oldest"] = ch_since

        try:
            resp = _slack_api("conversations.history", token, params)
            if not resp.get("ok") and resp.get("error") == "not_in_channel":
                # Auto-join public channel and retry
                _slack_api("conversations.join", token, {"channel": ch_id})
                resp = _slack_api("conversations.history", token, params)
        except Exception as e:
            # Skip channels we can't access
            continue

        if not resp.get("ok"):
            continue

        messages = resp.get("messages", [])
        newest_ts = "0"

        for msg in messages:
            ts = msg.get("ts", "0")
            if ts > newest_ts:
                newest_ts = ts

            text = msg.get("text", "")
            urls = _extract_urls(text)
            for u in urls:
                if u["url"] not in state.get("processed_urls", {}):
                    u["channel_id"] = ch_id
                    u["channel_name"] = ch_name
                    u["sharer"] = msg.get("user", "")
                    u["ts"] = ts
                    u["msg_snippet"] = text[:200]
                    all_links.append(u)

        # Update state
        state.setdefault("channels", {})[ch_id] = {
            "name": ch_name,
            "last_scan_ts": newest_ts if newest_ts != "0" else ch_since,
            "links_found": len([l for l in all_links if l.get("channel_id") == ch_id]),
        }
        channels_scanned += 1

        # Polite rate limit
        time.sleep(0.5)

    # Deduplicate
    seen = set()
    deduped = []
    for link in all_links:
        if link["url"] not in seen:
            seen.add(link["url"])
            deduped.append(link)

    state["last_full_scan"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    _save_state(state)

    output = {
        "channels_scanned": channels_scanned,
        "total_links_found": len(deduped),
        "by_type": {},
        "links": deduped,
    }
    for link in deduped:
        t = link["type"]
        output["by_type"][t] = output["by_type"].get(t, 0) + 1

    print(json.dumps(output, indent=2, ensure_ascii=False))


def mode_fetch(args):
    """Fetch document contents for given URLs."""
    if args.input:
        with open(args.input) as f:
            data = json.load(f)
        urls = data if isinstance(data, list) else data.get("links", [])
    elif args.urls:
        urls = json.loads(args.urls)
    else:
        print(json.dumps({"error": "Provide --urls or --input"}))
        return

    notion_token = _load_notion_token()
    results = []

    for item in urls:
        url = item if isinstance(item, str) else item.get("url", "")
        url_type = _classify_url(url) if isinstance(item, str) else item.get("type", _classify_url(url))

        if url_type == "notion" and notion_token:
            result = fetch_notion_page(url, notion_token)
        elif url_type == "gdrive":
            result = fetch_gdrive_doc(url)
        else:
            content = _http_get_text(url)
            title = url.split("/")[-1][:50] or url
            result = {
                "url": url, "type": url_type,
                "title": title,
                "content_summary": content[:500],
                "full_text": content[:3000],
                "error": None if len(content) > 20 else "Could not fetch content",
            }

        # Carry over channel info
        if isinstance(item, dict):
            result["channel_name"] = item.get("channel_name", "")
            result["channel_id"] = item.get("channel_id", "")

        results.append(result)
        time.sleep(0.3)  # Rate limit

    print(json.dumps({"fetched": len(results), "documents": results},
                     indent=2, ensure_ascii=False))


def mode_classify(args):
    """Classify fetched documents by domain."""
    if args.input:
        with open(args.input) as f:
            data = json.load(f)
        docs = data if isinstance(data, list) else data.get("documents", [])
    else:
        print(json.dumps({"error": "Provide --input"}))
        return

    results = []
    for doc in docs:
        ch_name = doc.get("channel_name", "")
        content = (doc.get("title", "") + " " +
                   doc.get("content_summary", "") + " " +
                   doc.get("full_text", ""))

        # Tier 1: channel name
        domain = classify_by_channel(ch_name)
        method = "channel"

        # Tier 2: content keywords
        if not domain:
            domain, score = classify_by_content(content)
            method = "content"
            if score < 3:
                domain = "general"
                method = "low_confidence"

        # Multi-domain check
        text_lower = content.lower()
        all_domains = []
        for d, keywords in DOMAIN_KEYWORDS.items():
            score = sum(w * min(text_lower.count(k.lower()), 3)
                       for k, w in keywords.items())
            if score >= 3:
                all_domains.append({"domain": d, "score": score})
        all_domains.sort(key=lambda x: x["score"], reverse=True)

        results.append({
            "url": doc.get("url", ""),
            "title": doc.get("title", ""),
            "content_summary": doc.get("content_summary", "")[:200],
            "primary_domain": domain,
            "all_domains": [d["domain"] for d in all_domains[:3]],
            "classification_method": method,
            "channel_name": ch_name,
        })

    # Group by domain
    by_domain = {}
    for r in results:
        d = r["primary_domain"]
        by_domain.setdefault(d, []).append(r)

    print(json.dumps({
        "total": len(results),
        "by_domain": {d: len(docs) for d, docs in by_domain.items()},
        "classified": results,
    }, indent=2, ensure_ascii=False))


def mode_render(args):
    """Render references.md entries for a domain."""
    if not args.input:
        print(json.dumps({"error": "Provide --input (classified docs JSON)"}))
        return
    if not args.domain:
        print(json.dumps({"error": "Provide --domain"}))
        return

    with open(args.input) as f:
        data = json.load(f)
    classified = data if isinstance(data, list) else data.get("classified", [])

    # Filter to target domain
    domain_docs = [d for d in classified
                   if d.get("primary_domain") == args.domain
                   or args.domain in d.get("all_domains", [])]

    if not domain_docs:
        print(json.dumps({"domain": args.domain, "entries": 0, "markdown": ""}))
        return

    # Read existing references.md to check for duplicates
    refs_file = LIBRARY_DIR / args.domain / "references.md"
    existing_content = ""
    if refs_file.exists():
        existing_content = refs_file.read_text()

    # Build entries (skip URLs already in references.md)
    new_entries = []
    for doc in domain_docs:
        url = doc.get("url", "")
        if url in existing_content:
            continue
        title = doc.get("title", "Untitled")
        summary = doc.get("content_summary", "")[:100]
        source = doc.get("channel_name", "")
        doc_type = _classify_url(url)
        type_label = {"notion": "Notion", "gdrive": "Google Drive"}.get(doc_type, "Web")

        new_entries.append({
            "title": title,
            "url": url,
            "summary": summary,
            "source": source,
            "type": type_label,
        })

    # Render markdown table rows
    md_lines = []
    if new_entries:
        md_lines.append(f"\n## Auto-Collected References\n")
        md_lines.append("| Resource | Source | Type | 비고 |")
        md_lines.append("|----------|--------|------|------|")
        for e in new_entries:
            safe_title = e["title"].replace("|", "/")[:60]
            safe_summary = e["summary"].replace("|", "/").replace("\n", " ")[:80]
            md_lines.append(
                f"| [{safe_title}]({e['url']}) | {e['source']} | {e['type']} | {safe_summary} |"
            )
        md_lines.append("")
        md_lines.append(f"*Auto-collected: {time.strftime('%Y-%m-%d')} "
                       f"({len(new_entries)} documents)*")

    output = {
        "domain": args.domain,
        "entries": len(new_entries),
        "skipped_duplicates": len(domain_docs) - len(new_entries),
        "markdown": "\n".join(md_lines),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Mode: workspace — scan agent workspace directories for generated docs
# ---------------------------------------------------------------------------

def mode_workspace(args):
    """Scan master agent workspaces for generated documents, classify into library domains."""
    state = _load_state()
    processed = state.get("workspace_processed", {})
    agent_filter = args.agent  # optional: scan specific agent only

    agents = list(AGENT_DOMAIN_MAP.keys())
    if agent_filter:
        agents = [a for a in agents if a == agent_filter]

    all_files = []
    classified = {}

    for agent_id in agents:
        ws_dir = WORKSPACE_DIR / f"workspace-{agent_id}"
        if not ws_dir.is_dir():
            continue

        default_domain = AGENT_DOMAIN_MAP.get(agent_id, "general")
        func_subdomain = _AGENT_FUNC_MAP.get(agent_id, default_domain)

        for md_file in ws_dir.rglob("*.md"):
            # Skip system files
            if md_file.name in WORKSPACE_SYSTEM_FILES:
                continue
            # Skip excluded directories
            rel = md_file.relative_to(ws_dir)
            if any(part in WORKSPACE_EXCLUDE_DIRS for part in rel.parts):
                continue

            rel_key = f"{agent_id}/{rel}"

            # Read title (first heading line)
            try:
                first_lines = md_file.read_text(encoding="utf-8", errors="replace")[:500]
                title_match = re.match(r"^#\s+(.+)", first_lines)
                title = title_match.group(1).strip() if title_match else md_file.stem
            except Exception:
                title = md_file.stem

            # Determine domain: product path takes priority
            domain = default_domain
            rel_lower = str(rel).lower()
            product_match = None
            for pname in PRODUCT_NAMES:
                if pname in rel_lower:
                    product_match = pname
                    break

            if product_match:
                # Product document → library/{product}/{func}/
                domain = f"{product_match}/{func_subdomain}"
            else:
                # Use content-based classification as secondary signal
                try:
                    content_sample = md_file.read_text(encoding="utf-8", errors="replace")[:2000]
                    content_domain, score = classify_by_content(content_sample)
                    if score >= 6 and content_domain != default_domain:
                        # Strong content signal overrides agent default
                        domain = content_domain
                except Exception:
                    pass

            is_new = rel_key not in processed
            file_size = md_file.stat().st_size
            mtime = time.strftime("%Y-%m-%d", time.localtime(md_file.stat().st_mtime))

            entry = {
                "source": agent_id,
                "path": str(rel),
                "full_path": str(md_file),
                "rel_key": rel_key,
                "domain": domain,
                "title": title[:100],
                "size": file_size,
                "mtime": mtime,
                "is_new": is_new,
            }
            all_files.append(entry)
            classified.setdefault(domain, []).append(str(rel))

    # Summary
    new_files = [f for f in all_files if f["is_new"]]
    output = {
        "scanned_agents": len(agents),
        "total_files": len(all_files),
        "new_files": len(new_files),
        "classified": {d: files for d, files in sorted(classified.items())},
        "files": all_files,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def mode_workspace_collect(args):
    """Copy new workspace documents into library directories."""
    state = _load_state()
    processed = state.get("workspace_processed", {})

    # First run workspace scan to find files
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        mode_workspace(args)
    scan_result = json.loads(buf.getvalue())

    new_files = [f for f in scan_result["files"] if f["is_new"]]
    if not new_files:
        print(json.dumps({"collected": 0, "message": "No new files to collect"}))
        return

    import shutil
    collected = []
    for entry in new_files:
        src = Path(entry["full_path"])
        domain = entry["domain"]

        # Determine target directory
        target_dir = LIBRARY_DIR / domain
        target_dir.mkdir(parents=True, exist_ok=True)

        # Use original filename
        target = target_dir / src.name

        # Avoid overwriting — append suffix if exists
        if target.exists():
            stem = target.stem
            suffix = target.suffix
            i = 1
            while target.exists():
                target = target_dir / f"{stem}-{i}{suffix}"
                i += 1

        shutil.copy2(str(src), str(target))

        # Mark as processed
        processed[entry["rel_key"]] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        collected.append({
            "source": entry["rel_key"],
            "target": str(target.relative_to(LIBRARY_DIR)),
            "domain": domain,
            "title": entry["title"],
        })

    state["workspace_processed"] = processed
    _save_state(state)

    print(json.dumps({
        "collected": len(collected),
        "files": collected,
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Mode: memory — scan agent memory directories for insight cards
# ---------------------------------------------------------------------------

def mode_memory(args):
    """Scan all agent memory directories for structured insight files, classify into library domains."""
    state = _load_state()
    processed = state.get("memory_processed", {})
    agent_filter = args.agent
    min_relevance = float(args.min_relevance) if hasattr(args, "min_relevance") and args.min_relevance else 0.0

    # Discover all workspace-*/memory/ directories
    agents = []
    for ws in sorted(WORKSPACE_DIR.glob("workspace-*")):
        agent_id = ws.name.replace("workspace-", "")
        if agent_filter and agent_id != agent_filter:
            continue
        mem_dir = ws / "memory"
        if mem_dir.is_dir():
            agents.append((agent_id, mem_dir))

    all_entries = []
    domain_counts = {}

    for agent_id, mem_dir in agents:
        default_domain = AGENT_LIBRARY_DOMAIN.get(agent_id, "developers")

        for md_file in mem_dir.rglob("*.md"):
            rel_key = f"{agent_id}/memory/{md_file.relative_to(mem_dir)}"

            meta = _parse_memory_file(md_file)
            if not meta:
                continue

            # Skip low-relevance files
            if meta["relevance"] < min_relevance:
                continue

            # Classify domain: normalize Domain field → fallback to agent default
            lib_domain = _normalize_memory_domain(meta["domain"], meta["tags"], meta["title"])
            if not lib_domain:
                # Try content-based classification
                content_text = f"{meta['title']} {meta['tags']} {meta['insight']}"
                lib_domain, score = classify_by_content(content_text)
                if score < 3:
                    lib_domain = default_domain

            is_new = rel_key not in processed

            entry = {
                "source_agent": agent_id,
                "workspace_agent": meta.get("agent", agent_id),
                "rel_key": rel_key,
                "title": meta["title"][:120],
                "source_url": meta["source"],
                "date": meta["date"][:10] if meta["date"] else "",
                "original_domain": meta["domain"],
                "library_domain": lib_domain,
                "tags": meta["tags"],
                "relevance": meta["relevance"],
                "type": meta["type"],
                "insight": meta["insight"][:300],
                "entities": meta["entities"],
                "is_new": is_new,
                "size": md_file.stat().st_size,
            }
            all_entries.append(entry)
            domain_counts[lib_domain] = domain_counts.get(lib_domain, 0) + 1

    new_entries = [e for e in all_entries if e["is_new"]]
    output = {
        "scanned_agents": len(agents),
        "total_files": len(all_entries),
        "new_files": len(new_entries),
        "by_domain": dict(sorted(domain_counts.items())),
        "domain_summary": {d: len([e for e in all_entries if e["library_domain"] == d])
                          for d in sorted(set(e["library_domain"] for e in all_entries))},
        "files": all_entries,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def mode_memory_collect(args):
    """Aggregate memory insights by domain into library/{domain}/memory-insights.md files."""
    state = _load_state()
    processed = state.get("memory_processed", {})

    # Run memory scan first
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        mode_memory(args)
    scan_result = json.loads(buf.getvalue())

    new_entries = [f for f in scan_result["files"] if f["is_new"]]
    if not new_entries:
        print(json.dumps({"collected": 0, "message": "No new memory files to collect"}))
        return

    # Group by library domain
    by_domain = {}
    for entry in new_entries:
        d = entry["library_domain"]
        by_domain.setdefault(d, []).append(entry)

    collected_summary = {}
    for domain, entries in sorted(by_domain.items()):
        target_dir = LIBRARY_DIR / domain
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "memory-insights.md"

        # Read existing content
        existing = ""
        if target_file.exists():
            existing = target_file.read_text(encoding="utf-8", errors="replace")

        # Build new entries (skip duplicates by source URL)
        new_lines = []
        for e in sorted(entries, key=lambda x: x.get("date", ""), reverse=True):
            if e["source_url"] and e["source_url"] in existing:
                continue
            date_str = e["date"] or "N/A"
            tags_str = e["tags"] if e["tags"] else ""
            relevance_str = f"{e['relevance']:.2f}" if e["relevance"] else ""

            new_lines.append(f"### {e['title'][:80]}")
            new_lines.append(f"- **Source**: {e['source_url']}")
            new_lines.append(f"- **Agent**: {e['source_agent']} | **Date**: {date_str} | **Relevance**: {relevance_str}")
            if tags_str:
                new_lines.append(f"- **Tags**: {tags_str}")
            if e["insight"]:
                new_lines.append(f"- **Insight**: {e['insight'][:200]}")
            new_lines.append("")

            # Mark as processed
            processed[e["rel_key"]] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        if not new_lines:
            continue

        # Append to file (or create with header)
        if not existing:
            header = f"# {domain.title()} — Memory Insights\n\n"
            header += f"> Bot memory에서 자동 수집된 인사이트 카드. 각 항목은 에이전트가 외부 소스에서 추출한 도메인 지식.\n\n"
            header += f"*Last updated: {time.strftime('%Y-%m-%d')}*\n\n---\n\n"
            content = header + "\n".join(new_lines)
        else:
            # Update timestamp in existing header
            content = re.sub(
                r"\*Last updated: \d{4}-\d{2}-\d{2}\*",
                f"*Last updated: {time.strftime('%Y-%m-%d')}*",
                existing
            )
            content = content.rstrip() + "\n\n" + "\n".join(new_lines)

        target_file.write_text(content, encoding="utf-8")
        collected_summary[domain] = len([l for l in new_lines if l.startswith("### ")])

    state["memory_processed"] = processed
    _save_state(state)

    print(json.dumps({
        "collected_domains": len(collected_summary),
        "total_insights": sum(collected_summary.values()),
        "by_domain": collected_summary,
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Library Scanner — Slack + Workspace → Library")
    parser.add_argument("--mode", required=True,
                       choices=["status", "scan", "fetch", "classify", "render",
                                "workspace", "workspace-collect",
                                "memory", "memory-collect"])
    parser.add_argument("--channel", help="Specific Slack channel ID")
    parser.add_argument("--agent", help="Specific agent ID for workspace/memory scan (e.g. art-master)")
    parser.add_argument("--min-relevance", dest="min_relevance", type=float, default=0.0,
                       help="Minimum relevance score for memory mode (0.0-1.0)")
    parser.add_argument("--limit", type=int, default=200, help="Messages per channel")
    parser.add_argument("--since", help="UNIX timestamp for incremental scan")
    parser.add_argument("--urls", help="JSON array of URLs (for fetch)")
    parser.add_argument("--input", help="Input JSON file path")
    parser.add_argument("--domain", help="Target domain (for render)")
    args = parser.parse_args()

    modes = {
        "status": mode_status,
        "scan": mode_scan,
        "fetch": mode_fetch,
        "classify": mode_classify,
        "render": mode_render,
        "workspace": mode_workspace,
        "workspace-collect": mode_workspace_collect,
        "memory": mode_memory,
        "memory-collect": mode_memory_collect,
    }
    modes[args.mode](args)


if __name__ == "__main__":
    main()
