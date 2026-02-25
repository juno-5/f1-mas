#!/usr/bin/env python3
"""
Update Notion Library page (311983e32b3280788ac5c9d8ecb279d7) with all references.md content.
Runs on ai1 server where NOTION_API_TOKEN is available.
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

PAGE_ID = "311983e32b3280788ac5c9d8ecb279d7"
NOTION_VERSION = "2022-06-28"
TOKEN = os.environ.get("NOTION_API_TOKEN", "")

DOMAIN_CONFIG = [
    ("developers", "Developers", "개발팀 참조 문서, 가이드, 도구 링크"),
    ("marketers", "Marketers", "마케팅팀 참조 문서, 플랫폼 정책, 브랜드 가이드"),
    ("creatives", "Creatives", "크리에이티브팀 참조 가이드, AI 도구 레퍼런스"),
    ("commerce", "Commerce", "커머스팀 참조 문서, 플랫폼 API, 운영 가이드"),
    ("sales", "Sales", "세일즈팀 참조 문서, 방법론, CRM 가이드"),
    ("uiux", "UIUX", "UI/UX팀 참조 문서, 디자인 시스템, 리서치 방법론"),
    ("cx", "CX", "고객경험팀 참조 문서, CS 운영 매뉴얼, SLA 기준"),
    ("models", "Models", "모델팀 참조 문서, 촬영 가이드, 에이전시 정보"),
]

# Also include product-specific subdirectories
PRODUCT_REFS = [
    ("supermembers/operations", "Supermembers Operations", "슈퍼멤버스 서비스 운영, 제품/매장 프로세스, 결제"),
]


def notion_request(method, path, body=None):
    """Make a Notion API request."""
    url = f"https://api.notion.com/v1/{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"  API error {e.code}: {err_body[:200]}")
        return None


def get_all_children(block_id):
    """Get all child blocks of a page/block."""
    blocks = []
    cursor = None
    while True:
        path = f"blocks/{block_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        result = notion_request("GET", path)
        if not result:
            break
        blocks.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    return blocks


def delete_block(block_id):
    """Archive (delete) a block."""
    return notion_request("DELETE", f"blocks/{block_id}")


def append_children(block_id, children):
    """Append children blocks (max 100 per call)."""
    for i in range(0, len(children), 100):
        batch = children[i:i+100]
        result = notion_request("PATCH", f"blocks/{block_id}/children", {"children": batch})
        if not result:
            print(f"  Failed to append batch {i//100 + 1}")
            return False
        time.sleep(0.35)  # Rate limit
    return True


# --- Block builders ---

def heading1(text):
    return {"type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def heading2(text):
    return {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def heading3(text):
    return {"type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def paragraph(text):
    return {"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}] if text else []}}

def divider():
    return {"type": "divider", "divider": {}}

def callout(text, emoji="📚"):
    return {
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": emoji},
            "rich_text": [{"type": "text", "text": {"content": text}}],
        }
    }

def bulleted_item_link(title, url, desc=""):
    """Create a bulleted list item with a link and optional description."""
    rich = []
    if url and url.startswith("http"):
        rich.append({"type": "text", "text": {"content": title, "link": {"url": url}}, "annotations": {"bold": True}})
    else:
        rich.append({"type": "text", "text": {"content": title}, "annotations": {"bold": True}})
    if desc:
        rich.append({"type": "text", "text": {"content": f" — {desc}"}})
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich}}

def bulleted_item_text(text):
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def todo_item(text, checked=False):
    return {"type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": text}}], "checked": checked}}

def toc():
    return {"type": "table_of_contents", "table_of_contents": {"color": "default"}}


# --- Markdown parser ---

def parse_references_md(filepath):
    """Parse a references.md file and return structured blocks."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return []

    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip empty lines, blockquotes, last-updated lines, horizontal rules
        if not line or line.startswith('>') or line.startswith('*Last updated') or line == '---':
            i += 1
            continue

        # H1 - skip (we add our own domain heading)
        if line.startswith('# '):
            i += 1
            continue

        # H2
        if line.startswith('## '):
            title = line[3:].strip()
            blocks.append(heading3(title))
            i += 1
            continue

        # H3
        if line.startswith('### '):
            title = line[4:].strip()
            blocks.append(heading3(title))
            i += 1
            continue

        # Table header detection
        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|--'):
            # Parse table
            headers = [h.strip() for h in line.split('|')[1:-1]]
            i += 2  # Skip header + separator

            while i < len(lines) and lines[i].strip().startswith('|'):
                row = lines[i].strip()
                cells = [c.strip() for c in row.split('|')[1:-1]]
                if len(cells) >= 1:
                    # Extract link from first cell
                    first_cell = cells[0] if cells else ""
                    desc_cell = cells[-1] if len(cells) > 1 else ""

                    # Check for strikethrough (deleted/private items)
                    if first_cell.startswith('~~') or '🔒' in row or '🗑' in row:
                        # Skip deleted/private items
                        i += 1
                        continue

                    # Extract markdown link [text](url)
                    link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', first_cell)
                    if link_match:
                        title = link_match.group(1)
                        url = link_match.group(2)
                        blocks.append(bulleted_item_link(title, url, desc_cell))
                    elif first_cell and first_cell != '':
                        text = first_cell
                        if desc_cell:
                            text += f" — {desc_cell}"
                        blocks.append(bulleted_item_text(text))
                i += 1
            continue

        # Checklist items
        if line.startswith('- [x] '):
            text = line[6:].strip()
            link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', text)
            if link_match:
                title = link_match.group(1)
                url = link_match.group(2)
                rest = text[link_match.end():].strip()
                if rest.startswith('—'):
                    rest = rest[1:].strip()
                blocks.append(bulleted_item_link(title, url, rest))
            else:
                blocks.append(todo_item(text, checked=True))
            i += 1
            continue

        if line.startswith('- [ ] '):
            text = line[6:].strip()
            blocks.append(todo_item(text, checked=False))
            i += 1
            continue

        # Regular list items
        if line.startswith('- '):
            text = line[2:].strip()
            blocks.append(bulleted_item_text(text))
            i += 1
            continue

        i += 1

    return blocks


def main():
    if not TOKEN:
        print("ERROR: NOTION_API_TOKEN not set")
        sys.exit(1)

    print(f"=== Notion Library Page Updater ===")
    print(f"Page: {PAGE_ID}")

    # Step 1: Get existing blocks
    print("\n[1] Fetching existing blocks...")
    existing = get_all_children(PAGE_ID)
    print(f"  Found {len(existing)} blocks")

    # Step 2: Delete non-archived blocks
    print(f"\n[2] Deleting non-archived blocks...")
    to_delete = [b for b in existing if not b.get("archived", False)]
    print(f"  {len(to_delete)} active blocks to delete ({len(existing) - len(to_delete)} already archived)")
    deleted = 0
    for block in to_delete:
        result = delete_block(block["id"])
        if result:
            deleted += 1
        time.sleep(0.15)
        if deleted % 20 == 0 and deleted > 0:
            print(f"  Deleted {deleted}/{len(to_delete)}...")
    print(f"  Deleted {deleted} blocks")

    # Step 3: Build new content
    print("\n[3] Building new content...")

    # Library base path
    lib_base = os.path.expanduser("~/f1-mas/library")
    if not os.path.exists(lib_base):
        # Try alternative path
        lib_base = os.path.expanduser("~/.f1crew/f1-mas/library")
    if not os.path.exists(lib_base):
        print(f"  ERROR: Library path not found. Trying to use provided content...")
        lib_base = None

    all_blocks = []

    # Page header
    all_blocks.append(callout(
        "F1 Library — 팀별 참조 문서 모음\n"
        "AI 에이전트 시스템(MAS)이 자동으로 수집·분류한 전사 참조 문서입니다.\n"
        "비공개/삭제된 항목은 제외되어 있습니다.",
        "📚"
    ))
    all_blocks.append(paragraph(""))
    all_blocks.append(toc())
    all_blocks.append(paragraph(""))
    all_blocks.append(divider())

    # Process each domain
    domain_emoji = {
        "developers": "🔧",
        "marketers": "📣",
        "creatives": "🎨",
        "commerce": "🛒",
        "sales": "💰",
        "uiux": "🎯",
        "cx": "💬",
        "models": "📷",
        "supermembers/operations": "⚙️",
    }

    configs = DOMAIN_CONFIG + PRODUCT_REFS

    for domain_dir, domain_name, domain_desc in configs:
        emoji = domain_emoji.get(domain_dir, "📄")
        print(f"  Processing {domain_name}...")

        all_blocks.append(heading1(f"{emoji} {domain_name}"))
        all_blocks.append(paragraph(domain_desc))
        all_blocks.append(paragraph(""))

        if lib_base:
            filepath = os.path.join(lib_base, domain_dir, "references.md")
            domain_blocks = parse_references_md(filepath)
            if domain_blocks:
                all_blocks.extend(domain_blocks)
                print(f"    → {len(domain_blocks)} blocks")
            else:
                all_blocks.append(paragraph("(참조 문서 없음)"))
                print(f"    → no content")

        all_blocks.append(paragraph(""))
        all_blocks.append(divider())

    # Footer
    all_blocks.append(paragraph(""))
    all_blocks.append(callout(
        "이 페이지는 Auto×Library 시스템이 자동으로 업데이트합니다.\n"
        f"마지막 업데이트: {time.strftime('%Y-%m-%d')}",
        "🤖"
    ))

    print(f"\n  Total blocks: {len(all_blocks)}")

    # Step 4: Append new content
    print(f"\n[4] Uploading {len(all_blocks)} blocks...")
    success = append_children(PAGE_ID, all_blocks)
    if success:
        print("  Upload complete!")
    else:
        print("  Upload had errors")

    print(f"\n=== Done ===")
    print(f"View: https://www.notion.so/mayacrew/{PAGE_ID}")


if __name__ == "__main__":
    main()
