#!/usr/bin/env python3
"""
Fetch creation dates for all documents in library references.md files.
Sources: Notion API (created_time), Google Drive API (createdTime).
Outputs JSON mapping: url -> YYYY-MM-DD
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

NOTION_TOKEN = os.environ.get("NOTION_API_TOKEN", "")
NOTION_VERSION = "2022-06-28"

# Google service account
GOOGLE_SA_PATH = os.path.expanduser("~/.f1crew/credentials/google-service-account.json")

LIBRARY_BASE = os.path.expanduser("~/f1-mas/library")
PRODUCTS = ["supermembers", "superchart", "cosduck", "commerce"]


def notion_get_page(page_id):
    """Get Notion page metadata including created_time."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        code = e.code
        if code == 404:
            return None  # page not accessible
        body = e.read().decode()[:100]
        print(f"  Notion error {code} for {page_id}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Notion timeout for {page_id}: {e}", file=sys.stderr)
        return None


def notion_get_db(db_id):
    """Get Notion database metadata including created_time."""
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def get_google_access_token():
    """Get OAuth2 access token from service account."""
    import base64
    import hashlib
    import hmac

    try:
        with open(GOOGLE_SA_PATH, 'r') as f:
            sa = json.load(f)
    except FileNotFoundError:
        print("  Google SA not found", file=sys.stderr)
        return None

    # Build JWT
    now = int(time.time())
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).rstrip(b'=')
    claim = base64.urlsafe_b64encode(json.dumps({
        "iss": sa["client_email"],
        "scope": "https://www.googleapis.com/auth/drive.readonly",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }).encode()).rstrip(b'=')

    # Sign with RSA
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        private_key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
        signature = private_key.sign(
            header + b"." + claim,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=')
    except ImportError:
        # Try subprocess with openssl
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(sa["private_key"])
            key_path = f.name
        try:
            proc = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", key_path],
                input=header + b"." + claim,
                capture_output=True
            )
            sig_b64 = base64.urlsafe_b64encode(proc.stdout).rstrip(b'=')
        finally:
            os.unlink(key_path)

    jwt_token = (header + b"." + claim + b"." + sig_b64).decode()

    # Exchange for access token
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt_token,
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("access_token")
    except Exception as e:
        print(f"  Google auth failed: {e}", file=sys.stderr)
        return None


import urllib.parse

def google_get_file(file_id, access_token):
    """Get Google Drive file metadata including createdTime."""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=createdTime,name"
    headers = {"Authorization": f"Bearer {access_token}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        return None
    except Exception:
        return None


def extract_notion_id(url):
    """Extract 32-char Notion page/db ID from URL."""
    # Pattern: last 32 hex chars (possibly with dashes)
    match = re.search(r'([0-9a-f]{32})(?:\?|$|/)', url)
    if match:
        return match.group(1)
    # Try with dashes: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', url)
    if match:
        return match.group(1).replace('-', '')
    return None


def extract_google_id(url):
    """Extract Google Drive file ID from URL."""
    # /d/{id}/ pattern
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    # /folders/{id}
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None


def extract_urls_from_references(filepath):
    """Extract all URLs and their row info from a references.md file."""
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return entries

    for i, line in enumerate(lines):
        line = line.rstrip()
        if not line.startswith('|') or line.startswith('|--') or line.startswith('| 문서명') or line.startswith('|-----'):
            continue
        # Skip strikethrough
        if '~~' in line or '🔒' in line or '🗑' in line:
            continue

        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) < 2:
            continue

        title = cells[0]
        link_cell = cells[1] if len(cells) > 1 else ""

        # Extract URL
        link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', link_cell)
        if link_match:
            source = link_match.group(1)
            url = link_match.group(2)
            entries.append({
                "title": title,
                "source": source,
                "url": url,
                "line": i,
                "file": filepath,
            })

    return entries


def main():
    if not NOTION_TOKEN:
        print("ERROR: NOTION_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    print("=== Fetching Document Creation Dates ===", file=sys.stderr)

    # Collect all entries
    all_entries = []
    for product in PRODUCTS:
        filepath = os.path.join(LIBRARY_BASE, product, "references.md")
        entries = extract_urls_from_references(filepath)
        all_entries.extend(entries)
        print(f"  {product}: {len(entries)} entries", file=sys.stderr)

    print(f"  Total: {len(all_entries)} entries", file=sys.stderr)

    # Classify by source
    notion_entries = []
    google_entries = []
    other_entries = []
    for e in all_entries:
        if 'notion.so' in e['url'] or 'notion.site' in e['url']:
            e['notion_id'] = extract_notion_id(e['url'])
            if e['notion_id']:
                notion_entries.append(e)
            else:
                other_entries.append(e)
        elif 'google.com' in e['url'] or 'drive.google.com' in e['url']:
            e['google_id'] = extract_google_id(e['url'])
            if e['google_id']:
                google_entries.append(e)
            else:
                other_entries.append(e)
        else:
            other_entries.append(e)

    print(f"  Notion: {len(notion_entries)}, Google: {len(google_entries)}, Other: {len(other_entries)}", file=sys.stderr)

    results = {}  # url -> date string

    # Fetch Notion creation dates
    print(f"\n[Notion] Fetching {len(notion_entries)} pages...", file=sys.stderr)
    notion_ok = 0
    notion_fail = 0
    for i, e in enumerate(notion_entries):
        nid = e['notion_id']
        is_db = e['source'] == 'Notion DB'

        if is_db:
            data = notion_get_db(nid)
        else:
            data = notion_get_page(nid)

        if data and 'created_time' in data:
            created = data['created_time'][:10]  # YYYY-MM-DD
            results[e['url']] = created
            notion_ok += 1
        else:
            # Try as database if page fails
            if not is_db:
                data = notion_get_db(nid)
                if data and 'created_time' in data:
                    created = data['created_time'][:10]
                    results[e['url']] = created
                    notion_ok += 1
                else:
                    notion_fail += 1
            else:
                notion_fail += 1

        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{len(notion_entries)} (ok={notion_ok}, fail={notion_fail})", file=sys.stderr)
        time.sleep(0.35)  # Rate limit ~3/sec

    print(f"  Notion done: {notion_ok} ok, {notion_fail} failed", file=sys.stderr)

    # Fetch Google creation dates
    if google_entries:
        print(f"\n[Google] Authenticating...", file=sys.stderr)
        access_token = get_google_access_token()
        if access_token:
            print(f"[Google] Fetching {len(google_entries)} files...", file=sys.stderr)
            google_ok = 0
            google_fail = 0
            for i, e in enumerate(google_entries):
                gid = e['google_id']
                data = google_get_file(gid, access_token)
                if data and 'createdTime' in data:
                    created = data['createdTime'][:10]
                    results[e['url']] = created
                    google_ok += 1
                else:
                    google_fail += 1

                if (i + 1) % 20 == 0:
                    print(f"  Progress: {i+1}/{len(google_entries)}", file=sys.stderr)
                time.sleep(0.2)

            print(f"  Google done: {google_ok} ok, {google_fail} failed", file=sys.stderr)
        else:
            print("  Google auth failed, skipping", file=sys.stderr)

    # Output results as JSON to stdout
    print(f"\n=== Results: {len(results)} dates found ===", file=sys.stderr)
    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
