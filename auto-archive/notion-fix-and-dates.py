#!/usr/bin/env python3
"""Fix broken links + add creation dates to Notion page blocks."""

import json
import re
import ssl
import sys
import time
import urllib.request
import urllib.error

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
PAGE_ID = "311983e32b3280788ac5c9d8ecb279d7"


def api_get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + TOKEN,
        "Notion-Version": "2022-06-28",
    })
    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        return json.loads(resp.read())


def api_patch(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": "Bearer " + TOKEN,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }, method="PATCH")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200]
        print("  PATCH ERROR %d: %s" % (e.code, err))
        return None


def rt(content, bold=False, link=None):
    r = {"type": "text", "text": {"content": content}}
    if link:
        r["text"]["link"] = {"url": link}
    r["annotations"] = {
        "bold": bold, "italic": False, "strikethrough": False,
        "underline": False, "code": False, "color": "blue" if link else "default"
    }
    return r


def rt_gray(content):
    r = {"type": "text", "text": {"content": content}}
    r["annotations"] = {
        "bold": False, "italic": False, "strikethrough": False,
        "underline": False, "code": False, "color": "gray"
    }
    return r


def extract_notion_page_id(url):
    """Extract Notion page ID from URL."""
    if not url or "notion.so" not in url:
        return None
    # Remove query params
    url = url.split("?")[0]
    # Get last segment
    parts = url.rstrip("/").split("/")
    last = parts[-1]
    # ID is last 32 chars (no dashes) or UUID format
    m = re.search(r"([a-f0-9]{32})$", last)
    if m:
        return m.group(1)
    m = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", last)
    if m:
        return m.group(1).replace("-", "")
    return None


def get_notion_page_date(page_id):
    """Fetch created_time for a Notion page."""
    url = "https://api.notion.com/v1/pages/" + page_id
    try:
        data = api_get(url)
        created = data.get("created_time", "")[:10]  # YYYY-MM-DD
        return created
    except Exception as e:
        return None


def parse_broken_block(text):
    """Parse a broken block that has raw markdown link in text."""
    # Pattern: [title](url)
    m = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", text)
    if not m:
        return None
    title = m.group(1)
    url = m.group(2)

    # Get description - everything after the link
    after = text[m.end():]
    # Remove leading pipe/spaces
    after = re.sub(r"^\s*\|\s*", "", after)
    # Remove "Notion" or "Notion DB" prefix
    after = re.sub(r"^Notion\s*(DB)?\s*\|\s*", "", after)
    desc = after.strip().rstrip("|").strip()

    # Get prefix - everything before the link
    before = text[:m.start()].strip().rstrip("|").strip()

    return {"title": title, "url": url, "desc": desc, "prefix": before}


def main():
    if not TOKEN:
        print("Usage: python3 notion-fix-and-dates.py <NOTION_API_TOKEN>")
        sys.exit(1)

    print("=== Phase 1: Collect all blocks ===\n")

    cursor = None
    all_blocks = []  # (block_id, has_link, url, text, rich_text)

    while True:
        url = "https://api.notion.com/v1/blocks/%s/children?page_size=100" % PAGE_ID
        if cursor:
            url += "&start_cursor=" + cursor
        data = api_get(url)
        for b in data["results"]:
            if b["type"] == "bulleted_list_item":
                rts = b["bulleted_list_item"]["rich_text"]
                txt = "".join(r["plain_text"] for r in rts)
                has_link = any(r.get("text", {}).get("link") for r in rts)
                link_url = None
                if has_link:
                    for r in rts:
                        lnk = r.get("text", {}).get("link")
                        if lnk:
                            link_url = lnk.get("url", "")
                            break
                all_blocks.append({
                    "id": b["id"],
                    "has_link": has_link,
                    "url": link_url,
                    "text": txt,
                    "rich_text": rts,
                })
        if not data["has_more"]:
            break
        cursor = data["next_cursor"]

    print("Total bullet blocks: %d" % len(all_blocks))

    # Identify broken blocks
    broken = [b for b in all_blocks if not b["has_link"] and "](http" in b["text"]]
    linked = [b for b in all_blocks if b["has_link"]]

    print("Linked blocks: %d" % len(linked))
    print("Broken blocks: %d" % len(broken))

    print("\n=== Phase 2: Fix broken links ===\n")

    for b in broken:
        parsed = parse_broken_block(b["text"])
        if not parsed:
            print("  SKIP (cant parse): %s" % b["text"][:60])
            continue

        texts = []
        if parsed["prefix"]:
            texts.append(rt(parsed["prefix"] + " — "))
        texts.append(rt(parsed["title"], bold=True, link=parsed["url"]))
        if parsed["desc"]:
            texts.append(rt("  —  " + parsed["desc"]))

        result = api_patch(
            "https://api.notion.com/v1/blocks/" + b["id"],
            {"bulleted_list_item": {"rich_text": texts}}
        )
        if result:
            print("  Fixed: %s" % parsed["title"][:60])
            # Update in our list
            b["has_link"] = True
            b["url"] = parsed["url"]
        time.sleep(0.35)

    print("\n=== Phase 3: Fetch Notion page creation dates ===\n")

    # Collect all blocks that link to Notion
    notion_blocks = []
    for b in all_blocks:
        url = b.get("url", "")
        if not url:
            # Check if just fixed
            continue
        if "notion.so" in url:
            page_id = extract_notion_page_id(url)
            if page_id:
                notion_blocks.append({"block": b, "page_id": page_id})

    # Also check broken blocks we just fixed
    for b in broken:
        parsed = parse_broken_block(b["text"])
        if parsed and "notion.so" in parsed["url"]:
            page_id = extract_notion_page_id(parsed["url"])
            if page_id and not any(nb["page_id"] == page_id for nb in notion_blocks):
                notion_blocks.append({"block": b, "page_id": page_id, "parsed": parsed})

    print("Notion-linked blocks to fetch dates: %d" % len(notion_blocks))

    # Fetch dates (with rate limiting)
    dates = {}  # page_id -> date string
    fetched = 0
    errors = 0
    for nb in notion_blocks:
        pid = nb["page_id"]
        if pid in dates:
            continue
        date = get_notion_page_date(pid)
        if date:
            dates[pid] = date
            fetched += 1
        else:
            errors += 1
        if (fetched + errors) % 20 == 0:
            print("  Fetched %d/%d (errors: %d)" % (fetched, len(notion_blocks), errors))
        time.sleep(0.35)

    print("  Done: %d dates fetched, %d errors" % (fetched, errors))

    print("\n=== Phase 4: Update blocks with dates ===\n")

    updated = 0
    for b in all_blocks:
        url = b.get("url", "")
        if not url:
            continue

        page_id = extract_notion_page_id(url) if "notion.so" in url else None
        date = dates.get(page_id) if page_id else None

        if not date:
            continue

        # Rebuild rich_text with date appended
        existing_rt = b["rich_text"]

        # Check if date is already in the text
        if date in b["text"]:
            continue

        # Append date in gray
        new_rt = list(existing_rt) + [rt_gray("  [%s]" % date)]

        result = api_patch(
            "https://api.notion.com/v1/blocks/" + b["id"],
            {"bulleted_list_item": {"rich_text": new_rt}}
        )
        if result:
            updated += 1
        if updated % 20 == 0 and updated > 0:
            print("  Updated %d blocks..." % updated)
        time.sleep(0.35)

    # Also handle the broken blocks we fixed
    for br in broken:
        parsed = parse_broken_block(br["text"])
        if not parsed:
            continue
        page_id = extract_notion_page_id(parsed["url"]) if "notion.so" in parsed["url"] else None
        date = dates.get(page_id) if page_id else None
        if not date:
            continue

        texts = []
        if parsed["prefix"]:
            texts.append(rt(parsed["prefix"] + " — "))
        texts.append(rt(parsed["title"], bold=True, link=parsed["url"]))
        if parsed["desc"]:
            texts.append(rt("  —  " + parsed["desc"]))
        texts.append(rt_gray("  [%s]" % date))

        result = api_patch(
            "https://api.notion.com/v1/blocks/" + br["id"],
            {"bulleted_list_item": {"rich_text": texts}}
        )
        if result:
            updated += 1
        time.sleep(0.35)

    print("\nTotal blocks updated with dates: %d" % updated)
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
