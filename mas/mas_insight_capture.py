"""MAS Insight Capture — extract [INSIGHT] blocks from agent output and persist to library."""

import os
import re
import time
import threading
from pathlib import Path

from . import mas_config as cfg

_INSIGHT_RE = re.compile(
    r"\[INSIGHT\]\s*(.*?)\s*\[/INSIGHT\]",
    re.DOTALL,
)

_write_lock = threading.Lock()

# Agent ID → library domain mapping
_AGENT_DOMAIN_MAP = {
    "dev-master": "developers",
    "mkt-master": "marketers",
    "art-master": "creatives",
    "commerce-master": "commerce",
    "sales-master": "sales",
    "uiux-master": "uiux",
    "cx-master": "cx",
}

# Persona category → library domain (direct mapping)
_CATEGORY_DOMAIN_MAP = {
    "developers": "developers",
    "marketers": "marketers",
    "creatives": "creatives",
    "commerce": "commerce",
    "sales": "sales",
    "uiux": "uiux",
    "cx": "cx",
    "models": "models",
}


def _log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [insight] {msg}", flush=True)


def _get_library_dir() -> Path:
    """Resolve library base directory from config or characters_base_dir."""
    explicit = cfg.get("library_base_dir", "")
    if explicit:
        return Path(explicit)
    # Derive from characters_base_dir (sibling directory)
    chars_dir = cfg.get("characters_base_dir", "")
    if chars_dir:
        return Path(chars_dir).parent / "library"
    # Fallback: relative to this file
    return Path(__file__).resolve().parent.parent / "library"


def extract_insights(text: str) -> list[dict]:
    """Extract [INSIGHT]...[/INSIGHT] blocks from text.

    Returns list of {"title", "context", "insight", "tags", "raw"}.
    """
    matches = _INSIGHT_RE.findall(text)
    results = []
    for raw in matches:
        entry = {"raw": raw.strip()}
        for line in raw.strip().splitlines():
            line = line.strip()
            if line.lower().startswith("title:"):
                entry["title"] = line[6:].strip()
            elif line.lower().startswith("context:"):
                entry["context"] = line[8:].strip()
            elif line.lower().startswith("insight:"):
                entry["insight"] = line[8:].strip()
            elif line.lower().startswith("tags:"):
                entry["tags"] = line[5:].strip()
        if entry.get("title") or entry.get("insight"):
            results.append(entry)
    return results


def strip_insights(text: str) -> str:
    """Remove [INSIGHT]...[/INSIGHT] blocks from text (for Slack delivery)."""
    return _INSIGHT_RE.sub("", text).strip()


def save_insights(domain: str, insights: list[dict], request_id: str = "",
                  source_agent: str = "") -> int:
    """Append insights to library/{domain}/insights.md.

    Returns number of insights saved.
    """
    if not insights:
        return 0

    library_dir = _get_library_dir()
    insights_file = library_dir / domain / "insights.md"

    if not insights_file.parent.exists():
        _log(f"Library dir not found: {insights_file.parent}")
        return 0

    date_str = time.strftime("%Y-%m-%d")
    entries = []

    for ins in insights:
        title = ins.get("title", "Untitled Insight")
        context = ins.get("context", "")
        insight_text = ins.get("insight", ins.get("raw", ""))
        tags = ins.get("tags", "")

        source = source_agent or f"request:{request_id[:8]}" if request_id else "unknown"

        entry_lines = [f"\n### [{date_str}] {title}"]
        entry_lines.append(f"- **Source**: {source}")
        if context:
            entry_lines.append(f"- **Context**: {context}")
        entry_lines.append(f"- **Insight**: {insight_text}")
        if tags:
            entry_lines.append(f"- **Tags**: {tags}")
        entry_lines.append("")

        entries.append("\n".join(entry_lines))

    with _write_lock:
        try:
            with open(insights_file, "a", encoding="utf-8") as f:
                for entry in entries:
                    f.write(entry + "\n")
            _log(f"Saved {len(entries)} insight(s) → {domain}/insights.md")
            return len(entries)
        except Exception as e:
            _log(f"Failed to save insights: {e}")
            return 0


def fetch_library_context(domain: str, max_refs_chars: int = None,
                          max_insights: int = 5) -> str:
    """Read library references + recent insights for a domain.

    Injected into agent prompts so they can leverage accumulated team knowledge.
    Returns formatted markdown string, or "" if nothing available.
    """
    if not cfg.get("library_injection", True):
        return ""

    if max_refs_chars is None:
        max_refs_chars = cfg.get("library_max_refs_chars", 6000)

    lib_domain = _CATEGORY_DOMAIN_MAP.get(domain, domain)
    library_dir = _get_library_dir()
    sections = []

    # 1. References (full file, truncated)
    refs_file = library_dir / lib_domain / "references.md"
    if refs_file.exists():
        try:
            content = refs_file.read_text(encoding="utf-8").strip()
            # Skip if only template (no real content filled in)
            if content and len(content) > 200:
                if len(content) > max_refs_chars:
                    content = content[:max_refs_chars] + "\n[... truncated ...]"
                sections.append(content)
        except Exception:
            pass

    # 2. Recent insights (last N entries)
    insights_file = library_dir / lib_domain / "insights.md"
    if insights_file.exists():
        try:
            content = insights_file.read_text(encoding="utf-8").strip()
            # Extract ### entries (newest first = bottom of file)
            entries = re.split(r"(?=^### \[)", content, flags=re.MULTILINE)
            real_entries = [e.strip() for e in entries if e.strip().startswith("### [")]
            if real_entries:
                recent = real_entries[-max_insights:]  # last N
                sections.append("## Recent Team Insights\n\n" + "\n\n".join(recent))
        except Exception:
            pass

    if not sections:
        return ""

    result = "\n\n## Team Library (" + lib_domain + ")\n\n" + "\n\n---\n\n".join(sections)
    _log(f"Library: injecting {len(result)} chars for domain={lib_domain}")
    return result


def process_synthesis(synthesis: str, domain: str, request_id: str = "",
                      source_agent: str = "") -> str:
    """Extract insights from synthesis, save them, return cleaned synthesis.

    This is the main entry point called from the orchestrator.
    """
    if not cfg.get("insight_capture_enabled", True):
        return synthesis

    insights = extract_insights(synthesis)
    if not insights:
        return synthesis

    # Map domain to library domain
    lib_domain = _CATEGORY_DOMAIN_MAP.get(domain, domain)

    saved = save_insights(lib_domain, insights, request_id=request_id,
                          source_agent=source_agent)
    _log(f"[{request_id}] Captured {saved} insight(s) for domain={lib_domain}")

    # Strip insight blocks from synthesis (clean output for Slack)
    return strip_insights(synthesis)
