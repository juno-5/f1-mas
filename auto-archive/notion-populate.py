#!/usr/bin/env python3
"""Populate Notion page '마야크루 팀별 폴더' with library references."""

import json
import re
import ssl
import sys
import time
import urllib.request

# Fix SSL cert issue on macOS
SSL_CTX = ssl.create_default_context()
try:
    import certifi
    SSL_CTX.load_verify_locations(certifi.where())
except ImportError:
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE

NOTION_TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
PAGE_ID = "311983e32b3280788ac5c9d8ecb279d7"
NOTION_VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"

DOMAINS = [
    {
        "emoji": "\U0001F4BB",
        "name": "개발팀 (Developers)",
        "file": "developers/references.md",
    },
    {
        "emoji": "\U0001F4E2",
        "name": "마케팅팀 (Marketers)",
        "file": "marketers/references.md",
    },
    {
        "emoji": "\U0001F3A8",
        "name": "크리에이티브팀 (Creatives)",
        "file": "creatives/references.md",
    },
    {
        "emoji": "\U0001F6D2",
        "name": "커머스팀 (Commerce)",
        "file": "commerce/references.md",
    },
    {
        "emoji": "\U0001F4B0",
        "name": "세일즈팀 (Sales)",
        "file": "sales/references.md",
    },
    {
        "emoji": "\U0001F3AF",
        "name": "UI/UX팀",
        "file": "uiux/references.md",
    },
    {
        "emoji": "\U0001F91D",
        "name": "고객경험팀 (CX)",
        "file": "cx/references.md",
    },
    {
        "emoji": "\U0001F4F7",
        "name": "모델팀 (Models)",
        "file": "models/references.md",
    },
]

LIBRARY_BASE = "/Users/juno/F1/f1-mas/library/"


def notion_request(method, path, body=None):
    """Make a Notion API request."""
    url = f"{BASE}{path}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"  ERROR {e.code}: {err_body[:200]}")
        return None


def rich_text(content, bold=False, link=None):
    """Create a rich text object."""
    rt = {"type": "text", "text": {"content": content}}
    if link:
        rt["text"]["link"] = {"url": link}
    if bold or link:
        rt["annotations"] = {
            "bold": bold,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default",
        }
        if link:
            rt["annotations"]["color"] = "blue"
    return rt


def heading_block(level, text):
    """Create a heading block."""
    key = f"heading_{level}"
    return {"type": key, key: {"rich_text": [rich_text(text)]}}


def bullet_block(texts):
    """Create a bulleted list item. texts is a list of rich_text objects."""
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": texts},
    }


def divider_block():
    return {"type": "divider", "divider": {}}


def callout_block(text, emoji="📌"):
    return {
        "type": "callout",
        "callout": {
            "rich_text": [rich_text(text)],
            "icon": {"type": "emoji", "emoji": emoji},
        },
    }


def toc_block():
    return {"type": "table_of_contents", "table_of_contents": {"color": "default"}}


def parse_md_link(text):
    """Extract (title, url) from markdown link [title](url)."""
    m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if m:
        return m.group(1), m.group(2)
    return None, None


def parse_references_md(filepath):
    """Parse a references.md file into structured sections."""
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"  File not found: {filepath}")
        return []

    sections = []
    current_h2 = None
    current_h3 = None
    current_items = []
    skip_header = True

    for line in lines:
        line = line.rstrip()

        # Skip the first H1 and description
        if line.startswith("# ") and skip_header:
            skip_header = False
            continue
        if line.startswith("> "):
            continue

        # Skip metadata lines
        if line.startswith("*Last updated:") or line == "---":
            continue

        # H2
        if line.startswith("## "):
            # Save previous section
            if current_h3:
                sections.append(
                    {"level": 3, "title": current_h3, "items": current_items}
                )
                current_items = []
                current_h3 = None
            if current_h2 and current_items:
                sections.append(
                    {"level": 2, "title": current_h2, "items": current_items}
                )
                current_items = []
            elif current_h2 and not current_items:
                sections.append({"level": 2, "title": current_h2, "items": []})

            current_h2 = line[3:].strip()
            current_h3 = None
            current_items = []
            continue

        # H3
        if line.startswith("### "):
            if current_h3 and current_items:
                sections.append(
                    {"level": 3, "title": current_h3, "items": current_items}
                )
                current_items = []
            elif current_h3:
                sections.append({"level": 3, "title": current_h3, "items": []})
            current_h3 = line[4:].strip()
            current_items = []
            continue

        # Table rows (skip header/separator)
        if line.startswith("|") and not line.startswith("|--") and not line.startswith("| Resource") and not line.startswith("| Platform") and not line.startswith("| Tool") and not line.startswith("| Agency") and not line.startswith("| Source"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 1:
                title, url = parse_md_link(cols[0])
                if title and url:
                    desc = cols[-1] if len(cols) >= 2 else ""
                    # Clean up desc - skip if it's just "Notion" or URL
                    if desc in ("Notion", "Notion DB", ""):
                        desc = cols[2] if len(cols) >= 3 else ""
                    if desc in ("Notion", "Notion DB", ""):
                        desc = cols[-1] if len(cols) > 2 else ""
                    current_items.append(
                        {"title": title, "url": url, "desc": desc.strip()}
                    )
                elif cols[0].strip() and not cols[0].startswith("---"):
                    # Non-link table row
                    text = " | ".join(c for c in cols if c.strip())
                    if text and not text.startswith("---"):
                        current_items.append({"title": text, "url": None, "desc": ""})
            continue

        # Checkbox items
        if line.startswith("- [x] "):
            content = line[6:].strip()
            title, url = parse_md_link(content)
            if title and url:
                desc_match = re.search(r"\)\s*[—–-]\s*(.+)$", content)
                desc = desc_match.group(1) if desc_match else ""
                current_items.append({"title": title, "url": url, "desc": desc})
            else:
                current_items.append({"title": content, "url": None, "desc": ""})
            continue

        if line.startswith("- [ ] "):
            content = line[6:].strip()
            current_items.append(
                {"title": f"(미작성) {content}", "url": None, "desc": ""}
            )
            continue

    # Save last section
    if current_h3 and current_items:
        sections.append({"level": 3, "title": current_h3, "items": current_items})
    elif current_h3:
        sections.append({"level": 3, "title": current_h3, "items": []})
    if current_h2 and current_items:
        sections.append({"level": 2, "title": current_h2, "items": current_items})
    elif current_h2 and not any(
        s["title"] == current_h2 for s in sections
    ):
        sections.append({"level": 2, "title": current_h2, "items": current_items})

    return sections


def build_domain_blocks(domain_info):
    """Build Notion blocks for a single domain."""
    blocks = []
    filepath = LIBRARY_BASE + domain_info["file"]
    sections = parse_references_md(filepath)

    if not sections:
        blocks.append(
            bullet_block([rich_text("(레퍼런스 문서가 비어있습니다)", bold=False)])
        )
        return blocks

    for section in sections:
        # Add section heading
        blocks.append(heading_block(section["level"], section["title"]))

        # Add items
        for item in section["items"]:
            texts = []
            if item["url"]:
                texts.append(rich_text(item["title"], bold=True, link=item["url"]))
            else:
                texts.append(rich_text(item["title"]))
            if item["desc"]:
                texts.append(rich_text(f"  —  {item['desc']}"))
            blocks.append(bullet_block(texts))

        if not section["items"]:
            pass  # Empty section, heading only

    return blocks


def append_blocks(page_id, blocks):
    """Append blocks to a Notion page, batching by 100."""
    total = len(blocks)
    for i in range(0, total, 100):
        batch = blocks[i : i + 100]
        print(f"  Sending blocks {i+1}-{min(i+100, total)} of {total}...")
        result = notion_request(
            "PATCH",
            f"/blocks/{page_id}/children",
            {"children": batch},
        )
        if result is None:
            print("  FAILED! Stopping.")
            return False
        time.sleep(0.5)  # Rate limit
    return True


def main():
    if not NOTION_TOKEN:
        print("Usage: python3 notion-populate.py <NOTION_API_TOKEN>")
        sys.exit(1)

    print("=== Populating Notion page: 마야크루 팀별 폴더 ===\n")

    all_blocks = []

    # Intro callout
    all_blocks.append(
        callout_block(
            "마야크루 팀별 참조 문서 모음입니다. 각 팀의 핵심 문서, 가이드, 운영 시트를 한곳에서 확인할 수 있습니다.\n마지막 업데이트: 2026-02-24",
            "📚",
        )
    )
    all_blocks.append({"type": "paragraph", "paragraph": {"rich_text": []}})

    # Table of contents
    all_blocks.append(toc_block())
    all_blocks.append({"type": "paragraph", "paragraph": {"rich_text": []}})

    # Build blocks for each domain
    entry_count = 0
    for domain in DOMAINS:
        print(f"Processing {domain['name']}...")
        all_blocks.append(divider_block())
        all_blocks.append(
            heading_block(1, f"{domain['emoji']} {domain['name']}")
        )

        domain_blocks = build_domain_blocks(domain)
        all_blocks.extend(domain_blocks)
        entry_count += sum(
            1 for b in domain_blocks if b.get("type") == "bulleted_list_item"
        )
        print(
            f"  → {sum(1 for b in domain_blocks if b.get('type') == 'bulleted_list_item')} entries"
        )

    all_blocks.append(divider_block())
    all_blocks.append(
        callout_block(
            f"총 {entry_count}개 참조 문서가 등록되어 있습니다. Auto×Library 시스템이 Slack/Notion/Google Drive에서 자동 수집합니다.",
            "🤖",
        )
    )

    print(f"\nTotal blocks: {len(all_blocks)}")
    print(f"Total entries: {entry_count}")
    print()

    # Send to Notion
    success = append_blocks(PAGE_ID, all_blocks)
    if success:
        print("\n✅ Done! Page populated successfully.")
    else:
        print("\n❌ Failed to populate page.")
        sys.exit(1)


if __name__ == "__main__":
    main()
