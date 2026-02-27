#!/usr/bin/env python3
"""
Update Notion Library page (311983e32b3280788ac5c9d8ecb279d7) with 4-product references.md content.
Products: supermembers, superchart, cosduck, commerce
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

PRODUCT_CONFIG = [
    ("supermembers", "슈퍼멤버스", "블로그 체험단 플랫폼 — 운영, 개발, 마케팅, 세일즈, CX, UX"),
    ("superchart", "슈퍼차트", "인플루언서 마케팅 대행 — 개발, 마케팅, 세일즈, 데이터바우처"),
    ("cosduck", "코스덕", "K-Beauty 틱톡샵 에이전시 — 틱톡샵, 크리에이티브, 디자인, 물류"),
    ("commerce", "커머스", "자체 브랜드 이커머스 — HEEDA, KIMCHIP, MAPDA, Medihair"),
]

PRODUCT_EMOJI = {
    "supermembers": "🏪",
    "superchart": "📊",
    "cosduck": "🦆",
    "commerce": "🛒",
}

# Sections to exclude from Notion upload (matched against H2/H3 titles)
SKIP_SECTIONS = ["수출바우처"]


def notion_request(method, path, body=None, timeout=30, retries=3):
    """Make a Notion API request with retry."""
    url = f"https://api.notion.com/v1/{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"  API error {e.code}: {err_body[:200]}")
            return None
        except (TimeoutError, urllib.error.URLError) as e:
            if attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Timeout (attempt {attempt+1}/{retries}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"  Failed after {retries} attempts: {e}")
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
    """Archive (delete) a block. Fast fail for already-archived blocks."""
    return notion_request("DELETE", f"blocks/{block_id}", timeout=10, retries=1)


def append_children(block_id, children, batch_size=50):
    """Append children blocks in batches."""
    total = len(children)
    for i in range(0, total, batch_size):
        batch = children[i:i+batch_size]
        batch_num = i // batch_size + 1
        result = notion_request("PATCH", f"blocks/{block_id}/children", {"children": batch}, timeout=60)
        if not result:
            print(f"  Failed batch {batch_num} (items {i}-{i+len(batch)})")
            return False
        print(f"  Uploaded {min(i+batch_size, total)}/{total} blocks...")
        time.sleep(0.5)
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

def bulleted_item_link(title, url, desc="", date="", source_icon=""):
    """Create a bulleted list item with source icon, link, optional description, and code-formatted date."""
    rich = []
    # Source type icon prefix (🅽, Ⓖ, 💻, 💬)
    if source_icon:
        rich.append({"type": "text", "text": {"content": f"{source_icon} "}, "annotations": {"color": "gray"}})
    if url and url.startswith("http"):
        rich.append({"type": "text", "text": {"content": title, "link": {"url": url}}, "annotations": {"bold": True}})
    else:
        rich.append({"type": "text", "text": {"content": title}, "annotations": {"bold": True}})
    if desc:
        rich.append({"type": "text", "text": {"content": f" — {desc}"}})
    if date:
        rich.append({"type": "text", "text": {"content": "  "}})
        rich.append({"type": "text", "text": {"content": date}, "annotations": {"code": True, "color": "gray"}})
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich}}

def bulleted_item_text(text, date=""):
    rich = [{"type": "text", "text": {"content": text}}]
    if date:
        rich.append({"type": "text", "text": {"content": "  "}})
        rich.append({"type": "text", "text": {"content": date}, "annotations": {"code": True, "color": "gray"}})
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich}}

def toc():
    return {"type": "table_of_contents", "table_of_contents": {"color": "default"}}


# --- Markdown parser ---

def parse_references_md(filepath):
    """Parse a product references.md file and return structured blocks.

    Table format: | 문서명 | 링크 | 등록일 | 비고 |
    - Column 1: title (plain text)
    - Column 2: link ([Source](url)) or [Local MD](path)
    - Column 3: date (YYYY-MM-DD)
    - Column 4: description
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return []

    blocks = []
    lines = content.split('\n')
    i = 0
    skipping = False  # True when inside a SKIP_SECTIONS section
    skip_level = 0    # heading level that triggered skip (2 or 3)

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip empty lines, blockquotes, last-updated lines, horizontal rules
        if not line or line.startswith('>') or line.startswith('*Last updated') or line == '---':
            i += 1
            continue

        # H1 - skip (we add our own product heading)
        if line.startswith('# '):
            skipping = False
            i += 1
            continue

        # H2 → Notion heading_2
        if line.startswith('## '):
            title = line[3:].strip()
            if any(s in title for s in SKIP_SECTIONS):
                skipping = True
                skip_level = 2
                i += 1
                continue
            skipping = False
            blocks.append(heading2(title))
            i += 1
            continue

        # H3 → Notion heading_3
        if line.startswith('### '):
            title = line[4:].strip()
            if skipping and skip_level <= 2:
                # H3 inside a skipped H2 — keep skipping
                i += 1
                continue
            if any(s in title for s in SKIP_SECTIONS):
                skipping = True
                skip_level = 3
                i += 1
                continue
            skipping = False
            blocks.append(heading3(title))
            i += 1
            continue

        # Skip all content inside a skipped section
        if skipping:
            i += 1
            continue

        # Table header detection
        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|--'):
            # Parse table rows
            i += 2  # Skip header + separator

            while i < len(lines) and lines[i].strip().startswith('|'):
                row = lines[i].strip()
                cells = [c.strip() for c in row.split('|')[1:-1]]

                if len(cells) >= 2:
                    title_cell = cells[0] if cells else ""
                    link_cell = cells[1] if len(cells) > 1 else ""

                    # Detect 5-column (생성일|등록일|비고) vs 4-column (등록일|비고)
                    if len(cells) >= 5:
                        created_cell = cells[2].strip().strip('`') if cells[2].strip() != '—' else ""
                        reg_cell = cells[3].strip().strip('`') if cells[3].strip() != '—' else ""
                        desc_cell = cells[4] if len(cells) > 4 else ""
                    elif len(cells) >= 4:
                        created_cell = ""
                        reg_cell = cells[2].strip().strip('`') if cells[2].strip() != '—' else ""
                        desc_cell = cells[3] if len(cells) > 3 else ""
                    else:
                        created_cell = ""
                        reg_cell = ""
                        desc_cell = cells[2] if len(cells) > 2 else ""

                    # Build date display: "생성일 (등록일)" or just one
                    date_str = created_cell or reg_cell or ""

                    # Skip strikethrough (deleted/private items)
                    if title_cell.startswith('~~') or '🔒' in row or '🗑' in row:
                        i += 1
                        continue

                    # Extract URL and source icon from link column: [🅽 Notion](url)
                    link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', link_cell)
                    url = ""
                    source_icon = ""
                    if link_match:
                        source_label = link_match.group(1)
                        url = link_match.group(2)
                        # Extract icon from source label (e.g., "🅽 Notion" → "🅽")
                        for icon in ["🅽", "Ⓖ", "💻", "💬"]:
                            if icon in source_label:
                                source_icon = icon
                                break

                    # Also check if link is in title cell (old format fallback)
                    if not url:
                        title_link = re.search(r'\[([^\]]+)\]\(([^)]+)\)', title_cell)
                        if title_link:
                            title_cell = title_link.group(1)
                            url = title_link.group(2)

                    title = title_cell.strip()
                    if not title:
                        i += 1
                        continue

                    if url and url.startswith("http"):
                        blocks.append(bulleted_item_link(title, url, desc_cell, date_str, source_icon))
                    else:
                        text = title
                        if desc_cell:
                            text += f" — {desc_cell}"
                        blocks.append(bulleted_item_text(text, date_str))

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

    skip_delete = "--skip-delete" in sys.argv

    print(f"=== Notion Library Page Updater (4-Product Structure) ===")
    print(f"Page: {PAGE_ID}")

    if skip_delete:
        print("\n[1-2] Skipping delete (--skip-delete)")
    else:
        # Step 1: Get existing blocks
        print("\n[1] Fetching existing blocks...")
        existing = get_all_children(PAGE_ID)
        print(f"  Found {len(existing)} blocks")

    # Step 2: Delete active blocks (silently skip archived)
    if not skip_delete:
        print(f"\n[2] Deleting existing blocks...")
        total = len(existing)
        print(f"  {total} blocks to process")
        deleted = 0
        skipped = 0
        preserved = 0
        for block in existing:
            btype = block.get("type", "")
            if btype in ("child_page", "child_database"):
                preserved += 1
            elif block.get("archived", False):
                skipped += 1
            else:
                result = delete_block(block["id"])
                if result:
                    deleted += 1
                else:
                    skipped += 1  # archived at API level or failed — skip silently
            time.sleep(0.1)
            done = deleted + skipped + preserved
            if done % 50 == 0 and done > 0:
                print(f"  Progress {done}/{total} (deleted={deleted}, skipped={skipped}, preserved={preserved})...")
        print(f"  Done: {deleted} deleted, {skipped} skipped, {preserved} child pages preserved")

    # Step 3: Build new content
    print("\n[3] Building new content...")

    lib_base = os.path.expanduser("~/f1-mas/library")
    if not os.path.exists(lib_base):
        lib_base = os.path.expanduser("~/.f1crew/f1-mas/library")
    if not os.path.exists(lib_base):
        print(f"  ERROR: Library path not found")
        sys.exit(1)

    all_blocks = []

    # Page header
    all_blocks.append(callout(
        "F1 Library — 제품별 참조 문서 모음\n"
        "AI 에이전트 시스템(MAS)이 자동으로 수집·분류한 전사 참조 문서입니다.\n"
        "4개 제품: 슈퍼멤버스 · 슈퍼차트 · 코스덕 · 커머스",
        "📚"
    ))
    all_blocks.append(paragraph(""))
    all_blocks.append(toc())
    all_blocks.append(paragraph(""))
    all_blocks.append(divider())

    # Process each product
    for product_dir, product_name, product_desc in PRODUCT_CONFIG:
        emoji = PRODUCT_EMOJI.get(product_dir, "📄")
        print(f"  Processing {product_name}...")

        all_blocks.append(heading1(f"{emoji} {product_name}"))
        all_blocks.append(paragraph(product_desc))
        all_blocks.append(paragraph(""))

        filepath = os.path.join(lib_base, product_dir, "references.md")
        product_blocks = parse_references_md(filepath)
        if product_blocks:
            all_blocks.extend(product_blocks)
            print(f"    -> {len(product_blocks)} blocks")
        else:
            all_blocks.append(paragraph("(참조 문서 없음)"))
            print(f"    -> no content")

        all_blocks.append(paragraph(""))
        all_blocks.append(divider())

    # Footer
    all_blocks.append(paragraph(""))
    all_blocks.append(callout(
        "이 페이지는 Auto×Library 시스템이 자동으로 업데이트합니다.\n"
        f"마지막 업데이트: {time.strftime('%Y-%m-%d')}\n"
        "구조: 슈퍼멤버스 / 슈퍼차트 / 코스덕 / 커머스 (4개 제품)",
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
