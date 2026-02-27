#!/usr/bin/env python3
"""
Upload local MD files to Notion as sub-pages under the Library page.
Outputs JSON mapping: original_path -> notion_page_url
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

PARENT_PAGE_ID = "311983e32b3280788ac5c9d8ecb279d7"  # Library page
NOTION_VERSION = "2022-06-28"
TOKEN = os.environ.get("NOTION_API_TOKEN", "")

# Files to upload: (title, server_path, product)
FILES = [
    ("슈퍼멤버스 광고 프로젝트", "~/.f1crew/workspace-art-master/supermembers/PROJECT.md", "supermembers"),
    ("상위 광고 소재 딥 분석", "~/.f1crew/workspace-art-master/supermembers/ads/deep-analysis.md", "supermembers"),
    ("Meta 광고 소재 분석 리포트", "~/.f1crew/workspace-art-master/supermembers/ads/meta-ads-analysis.md", "supermembers"),
    ("영상 기획안 v2", "~/.f1crew/workspace-art-master/supermembers/ads/video-planning-v2.md", "supermembers"),
    ("프로덕션 레디 스크립트", "~/.f1crew/workspace-art-master/supermembers/ads/production-ready-scripts.md", "supermembers"),
    ("소재 자동 베리에이션 워크플로우", "~/.f1crew/workspace-art-master/supermembers/ads/variation-workflow.md", "supermembers"),
    ("Amazon Seller Central — 완전 메뉴 가이드", "~/.f1crew/workspace-mkt-master/amazon-seller-central-final-menu-guide.md", "commerce"),
    ("Amazon Seller Central — 메뉴 구조 맵", "~/.f1crew/workspace-mkt-master/amazon-seller-central-complete-menu-structure.md", "commerce"),
    ("TikTok 250만 팔로워 — AI 인플루언서 가이드", "~/.f1crew/workspace-art-master/video/biggie-ai-tiktok-influencer-guide.md", "cosduck"),
]


def notion_request(method, path, body=None, timeout=30, retries=3):
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
                time.sleep(2 ** (attempt + 1))
            else:
                print(f"  Failed: {e}")
                return None


def md_to_notion_blocks(content):
    """Convert markdown content to Notion block objects."""
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Empty line -> skip
        if not stripped:
            i += 1
            continue

        # Headings
        if stripped.startswith('#### '):
            blocks.append(make_heading(stripped[5:].strip(), 3))
            i += 1
            continue
        if stripped.startswith('### '):
            blocks.append(make_heading(stripped[4:].strip(), 3))
            i += 1
            continue
        if stripped.startswith('## '):
            blocks.append(make_heading(stripped[3:].strip(), 2))
            i += 1
            continue
        if stripped.startswith('# '):
            blocks.append(make_heading(stripped[2:].strip(), 1))
            i += 1
            continue

        # Horizontal rule
        if stripped in ('---', '***', '___'):
            blocks.append({"type": "divider", "divider": {}})
            i += 1
            continue

        # Blockquote
        if stripped.startswith('> '):
            text = stripped[2:].strip()
            blocks.append({
                "type": "quote",
                "quote": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Code block
        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].rstrip().startswith('```'):
                code_lines.append(lines[i].rstrip())
                i += 1
            i += 1  # skip closing ```
            code_text = '\n'.join(code_lines)
            if len(code_text) > 1950:
                code_text = code_text[:1950] + '\n... (truncated)'
            blocks.append({
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": code_text}}],
                    "language": lang if lang else "plain text",
                }
            })
            continue

        # Bullet list
        if stripped.startswith('- ') or stripped.startswith('* '):
            text = stripped[2:].strip()
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            text = m.group(2).strip()
            blocks.append({
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Table (simple: collect rows, split into chunks if > 2000 chars)
        if stripped.startswith('|') and '|' in stripped[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].rstrip())
                i += 1
            # Split into chunks to stay under 2000 char limit
            chunk = []
            chunk_len = 0
            for tl in table_lines:
                if chunk_len + len(tl) + 1 > 1900 and chunk:
                    blocks.append({
                        "type": "code",
                        "code": {
                            "rich_text": [{"type": "text", "text": {"content": '\n'.join(chunk)}}],
                            "language": "plain text",
                        }
                    })
                    chunk = []
                    chunk_len = 0
                chunk.append(tl)
                chunk_len += len(tl) + 1
            if chunk:
                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": '\n'.join(chunk)}}],
                        "language": "plain text",
                    }
                })
            continue

        # Regular paragraph
        # Collect consecutive non-special lines
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].rstrip()
            if not next_line or next_line.startswith('#') or next_line.startswith('```') \
               or next_line.startswith('- ') or next_line.startswith('* ') \
               or next_line.startswith('> ') or next_line.startswith('|') \
               or next_line in ('---', '***', '___') \
               or re.match(r'^\d+\.\s+', next_line):
                break
            para_lines.append(next_line)
            i += 1

        text = ' '.join(para_lines)
        if len(text) > 2000:
            text = text[:2000] + '...'
        blocks.append({
            "type": "paragraph",
            "paragraph": {"rich_text": parse_inline(text)}
        })

    return blocks


def make_heading(text, level):
    key = f"heading_{level}"
    return {"type": key, key: {"rich_text": parse_inline(text)}}


def parse_inline(text):
    """Parse inline markdown (bold, italic, code, links) into Notion rich_text."""
    rich = []
    pos = 0

    while pos < len(text):
        # Code: `text`
        m = re.search(r'`([^`]+)`', text[pos:])
        m_bold = re.search(r'\*\*(.+?)\*\*', text[pos:])
        m_link = re.search(r'\[([^\]]+)\]\(([^)]+)\)', text[pos:])

        # Find earliest match
        matches = []
        if m:
            matches.append(('code', m, pos + m.start()))
        if m_bold:
            matches.append(('bold', m_bold, pos + m_bold.start()))
        if m_link:
            matches.append(('link', m_link, pos + m_link.start()))

        if not matches:
            remaining = text[pos:]
            if remaining:
                rich.append({"type": "text", "text": {"content": remaining}})
            break

        matches.sort(key=lambda x: x[2])
        kind, match, abs_start = matches[0]

        # Text before match
        if abs_start > pos:
            rich.append({"type": "text", "text": {"content": text[pos:abs_start]}})

        if kind == 'code':
            rich.append({
                "type": "text",
                "text": {"content": match.group(1)},
                "annotations": {"code": True}
            })
            pos = abs_start + match.end()
        elif kind == 'bold':
            rich.append({
                "type": "text",
                "text": {"content": match.group(1)},
                "annotations": {"bold": True}
            })
            pos = abs_start + match.end()
        elif kind == 'link':
            url = match.group(2)
            link_text = match.group(1)
            rt = {"type": "text", "text": {"content": link_text}}
            if url.startswith('http'):
                rt["text"]["link"] = {"url": url}
            rich.append(rt)
            pos = abs_start + match.end()

    if not rich:
        rich.append({"type": "text", "text": {"content": text}})

    return rich


def create_page(title, blocks, icon_emoji="📄"):
    """Create a Notion page under the library parent."""
    # Notion API: max 100 children per create call
    first_batch = blocks[:100]
    body = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": icon_emoji},
        "properties": {
            "title": [{"type": "text", "text": {"content": title}}]
        },
        "children": first_batch,
    }
    result = notion_request("POST", "pages", body, timeout=60)
    if not result:
        return None

    page_id = result["id"]
    page_url = result.get("url", f"https://www.notion.so/{page_id.replace('-', '')}")

    # Append remaining blocks
    if len(blocks) > 100:
        for i in range(100, len(blocks), 100):
            batch = blocks[i:i+100]
            notion_request("PATCH", f"blocks/{page_id}/children", {"children": batch}, timeout=60)
            time.sleep(0.5)

    return page_url


def main():
    if not TOKEN:
        print("ERROR: NOTION_API_TOKEN not set")
        sys.exit(1)

    print("=== Upload Local MD Files to Notion ===")

    product_emoji = {
        "supermembers": "🏪",
        "superchart": "📊",
        "cosduck": "🦆",
        "commerce": "🛒",
    }

    results = {}  # title -> {url, product, original_path}

    # Filter: --only "title1" "title2" to retry specific files
    only = set()
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        only = set(sys.argv[idx+1:])

    for title, server_path, product in FILES:
        if only and title not in only:
            continue
        path = os.path.expanduser(server_path)
        emoji = product_emoji.get(product, "📄")

        print(f"\n  [{product}] {title}")

        if not os.path.exists(path):
            print(f"    SKIP: file not found at {path}")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        size = len(content)
        print(f"    Size: {size} bytes")

        # Convert MD to Notion blocks
        blocks = md_to_notion_blocks(content)
        print(f"    Blocks: {len(blocks)}")

        # Add source info callout at top
        source_block = {
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "📁"},
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"원본: {server_path}\n제품: {product}\n이 페이지는 서버의 MD 파일을 Notion에서 열람하기 위해 자동 생성되었습니다."}
                }]
            }
        }
        blocks.insert(0, source_block)

        # Create Notion page
        page_url = create_page(f"[{product.upper()}] {title}", blocks, emoji)

        if page_url:
            print(f"    OK: {page_url}")
            results[title] = {
                "url": page_url,
                "product": product,
                "original_path": server_path,
            }
        else:
            print(f"    FAILED")

        time.sleep(1)

    # Output results
    print(f"\n=== Done: {len(results)}/{len(FILES)} uploaded ===")
    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
