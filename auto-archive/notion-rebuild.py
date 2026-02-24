#!/usr/bin/env python3
"""Rebuild Notion page '마야크루 팀별 폴더' with product-based structure."""

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
LIBRARY = "/Users/juno/F1/f1-mas/library/"


# ── Notion helpers ──────────────────────────────────────────────

def api_patch(path, body):
    url = "https://api.notion.com/v1" + path
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
        print("  ERROR %d: %s" % (e.code, e.read().decode()[:200]))
        return None


def api_get(path):
    url = "https://api.notion.com/v1" + path
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + TOKEN,
        "Notion-Version": "2022-06-28",
    })
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError:
        return None


def rt(content, bold=False, link=None):
    r = {"type": "text", "text": {"content": content}}
    if link:
        r["text"]["link"] = {"url": link}
    r["annotations"] = {
        "bold": bold, "italic": False, "strikethrough": False,
        "underline": False, "code": False, "color": "blue" if link else "default",
    }
    return r


def rt_gray(content):
    return {
        "type": "text",
        "text": {"content": content},
        "annotations": {
            "bold": False, "italic": False, "strikethrough": False,
            "underline": False, "code": False, "color": "gray",
        },
    }


def h1(text):
    return {"type": "heading_1", "heading_1": {"rich_text": [rt(text)]}}


def h2(text):
    return {"type": "heading_2", "heading_2": {"rich_text": [rt(text)]}}


def h3(text):
    return {"type": "heading_3", "heading_3": {"rich_text": [rt(text)]}}


def bullet(title, url=None, desc="", date=None):
    texts = []
    if url:
        texts.append(rt(title, bold=True, link=url))
    else:
        texts.append(rt(title))
    if desc:
        texts.append(rt("  —  " + desc))
    if date:
        texts.append(rt_gray("  [%s]" % date))
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": texts}}


def divider():
    return {"type": "divider", "divider": {}}


def callout(text, emoji="📌"):
    return {
        "type": "callout",
        "callout": {
            "rich_text": [rt(text)],
            "icon": {"type": "emoji", "emoji": emoji},
        },
    }


def toc():
    return {"type": "table_of_contents", "table_of_contents": {"color": "default"}}


def paragraph():
    return {"type": "paragraph", "paragraph": {"rich_text": []}}


# ── Markdown parser ─────────────────────────────────────────────

def parse_md_link(text):
    # Handle [[title](url) pattern (double bracket)
    m = re.search(r"\[\[([^\]]+)\]\]\(([^)]+)\)", text)
    if m:
        return "[" + m.group(1) + "]", m.group(2)
    m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if m:
        return m.group(1), m.group(2)
    return None, None


def extract_notion_id(url):
    if not url or "notion.so" not in url:
        return None
    url = url.split("?")[0].rstrip("/")
    m = re.search(r"([a-f0-9]{32})$", url.split("/")[-1])
    return m.group(1) if m else None


def parse_entries(filepath):
    """Parse all link entries from a references.md file."""
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    entries = []
    current_section = ""

    for line in lines:
        line = line.rstrip()
        if line.startswith("## "):
            current_section = line[3:].strip()
        elif line.startswith("### "):
            current_section = line[4:].strip()

        # Table rows with links
        if line.startswith("|") and "](http" in line:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            title, url = parse_md_link(line)
            if title and url:
                # Find description - last meaningful column
                desc = ""
                for c in reversed(cols):
                    c = c.strip()
                    if c and c not in ("Notion", "Notion DB", "") and "](http" not in c:
                        desc = c
                        break
                entries.append({
                    "title": title, "url": url, "desc": desc,
                    "section": current_section,
                })

        # Checkbox items with links
        if line.startswith("- [x] ") and "](http" in line:
            title, url = parse_md_link(line)
            if title and url:
                m = re.search(r"\)\s*[—–-]\s*(.+)$", line)
                desc = m.group(1) if m else ""
                entries.append({
                    "title": title, "url": url, "desc": desc,
                    "section": current_section,
                })

    return entries


# ── Date fetcher ────────────────────────────────────────────────

date_cache = {}


def get_date(url):
    if not url:
        return None
    pid = extract_notion_id(url)
    if not pid:
        return None
    if pid in date_cache:
        return date_cache[pid]
    data = api_get("/pages/" + pid)
    if data:
        d = data.get("created_time", "")[:10]
        date_cache[pid] = d
        return d
    date_cache[pid] = None
    return None


# ── Content builder ─────────────────────────────────────────────

def build_supermembers_blocks():
    """Build all blocks for 슈퍼멤버스 section."""
    blocks = []

    # Source files for supermembers content
    sources = {
        "sm_dev": LIBRARY + "supermembers/dev/references.md",
        "sm_mkt": LIBRARY + "supermembers/marketing/references.md",
        "sm_sales": LIBRARY + "supermembers/sales/references.md",
        "sm_cx": LIBRARY + "supermembers/cx/references.md",
        "commerce": LIBRARY + "commerce/references.md",
        "developers": LIBRARY + "developers/references.md",
        "marketers": LIBRARY + "marketers/references.md",
        "sales": LIBRARY + "sales/references.md",
        "cx": LIBRARY + "cx/references.md",
        "uiux": LIBRARY + "uiux/references.md",
    }

    all_entries = {}
    for key, path in sources.items():
        all_entries[key] = parse_entries(path)

    # ── 서비스 개요 & 온보딩 ──
    blocks.append(h2("서비스 개요 & 온보딩"))
    section_keys = ["서비스 개요 & 온보딩", "기존 Slack 소스"]
    for e in all_entries["commerce"]:
        if e["section"] in section_keys:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 제품 운영 정책 ──
    blocks.append(h2("제품 운영 정책"))
    for e in all_entries["commerce"]:
        if e["section"] == "제품 운영 정책":
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 매장 운영 프로세스 ──
    blocks.append(h2("매장 운영 프로세스"))
    for e in all_entries["commerce"]:
        if e["section"] == "매장 운영 프로세스":
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 결제 & 정산 ──
    blocks.append(h2("결제 & 정산"))
    for e in all_entries["commerce"]:
        if e["section"] in ("결제 & 정산", "개밥먹기 & 사용성"):
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 개발 ──
    blocks.append(h2("개발"))
    # From supermembers/dev
    for e in all_entries["sm_dev"]:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    # From developers (슈퍼멤버스 sections only, avoiding duplicates)
    sm_dev_urls = {e["url"] for e in all_entries["sm_dev"]}
    sm_dev_sections = [
        "앱 성능 & 아키텍처", "API 마이그레이션", "AI & 자동화",
        "챗봇 & 인수인계", "분석 & 테스트", "인프라 & 설정",
        "Slack 파일 업로드 (GDrive)", "Slack Snippets (Ads_Payment 정합성)"
    ]
    for e in all_entries["developers"]:
        if e["section"] in sm_dev_sections and e["url"] not in sm_dev_urls:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 마케팅 ──
    blocks.append(h2("마케팅"))
    # From supermembers/marketing
    for e in all_entries["sm_mkt"]:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    # From marketers (슈퍼멤버스 sections)
    sm_mkt_urls = {e["url"] for e in all_entries["sm_mkt"]}
    sm_mkt_sections = [
        "마케팅 전략 & 기획", "콘텐츠 마케팅 (블로그/SNS)",
        "인플루언서 마케팅", "광고 성과 분석 & 보고",
    ]
    for e in all_entries["marketers"]:
        if e["section"] in sm_mkt_sections and e["url"] not in sm_mkt_urls:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 세일즈 ──
    blocks.append(h2("세일즈"))
    # From supermembers/sales
    for e in all_entries["sm_sales"]:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    # From sales (슈퍼멤버스 sections)
    sm_sales_urls = {e["url"] for e in all_entries["sm_sales"]}
    sm_sales_sections = [
        "사장님 여정 & 리텐션", "이탈 분석", "퍼널 & 전환 최적화",
        "경쟁사 분석", "고객 성공 사례", "Slack 핀 (GDrive)"
    ]
    for e in all_entries["sales"]:
        if e["section"] in sm_sales_sections and e["url"] not in sm_sales_urls:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── CX ──
    blocks.append(h2("CX (고객경험)"))
    # From supermembers/cx
    for e in all_entries["sm_cx"]:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    # From cx (슈퍼멤버스 sections)
    sm_cx_urls = {e["url"] for e in all_entries["sm_cx"]}
    sm_cx_sections = [
        "VOC & CS 운영", "CX 팀 온보딩", "전화 스크립트",
        "블로거 관리", "Slack 파일 업로드 (GDrive)", "Slack 핀 (GDrive)",
        "CS Operations",
    ]
    for e in all_entries["cx"]:
        if e["section"] in sm_cx_sections and e["url"] not in sm_cx_urls:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── UX/UI 설계 ──
    blocks.append(h2("UX/UI 설계"))
    sm_uiux_sections = [
        "슈퍼멤버스 UX 설계", "UI 개선 이슈 (Notion)",
    ]
    for e in all_entries["uiux"]:
        if e["section"] in sm_uiux_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    return blocks


def build_superchart_blocks():
    """Build all blocks for 슈퍼차트 section."""
    blocks = []

    sc_mkt = parse_entries(LIBRARY + "superchart/marketing/references.md")
    sc_sales = parse_entries(LIBRARY + "superchart/sales/references.md")
    dev_entries = parse_entries(LIBRARY + "developers/references.md")

    # ── 개발 ──
    blocks.append(h2("개발"))
    for e in dev_entries:
        if e["section"] == "Infrastructure":
            # API servers are shared between supermembers and superchart
            if "슈퍼차트" in e["desc"] or "API Server" in e["title"]:
                blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 마케팅 ──
    blocks.append(h2("마케팅"))
    for e in sc_mkt:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 세일즈 ──
    blocks.append(h2("세일즈"))
    for e in sc_sales:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # Also pull AE sheets from sales that are superchart specific
    sales_entries = parse_entries(LIBRARY + "sales/references.md")
    sc_sales_urls = {e["url"] for e in sc_sales}
    for e in sales_entries:
        if e["section"] == "AE (Account Executive) 운영 시트" and e["url"] not in sc_sales_urls:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 리드 관리 ──
    blocks.append(h2("리드 관리"))
    for e in sales_entries:
        if e["section"] == "Lead Management":
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    return blocks


def build_cosduck_blocks():
    """Build all blocks for 코스덕 section."""
    blocks = []

    cd_mkt = parse_entries(LIBRARY + "cosduck/marketing/references.md")
    cd_dev = parse_entries(LIBRARY + "cosduck/dev/references.md")
    cd_plan = parse_entries(LIBRARY + "cosduck/planning/references.md")
    commerce = parse_entries(LIBRARY + "commerce/references.md")
    creatives = parse_entries(LIBRARY + "creatives/references.md")
    uiux = parse_entries(LIBRARY + "uiux/references.md")

    # ── 서비스 방향성 & OKR ──
    blocks.append(h2("서비스 방향성 & OKR"))
    if cd_plan:
        for e in cd_plan:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    cosduck_sections = ["Cosduck (K-Beauty E-commerce)"]
    for e in commerce:
        if e["section"] in cosduck_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 틱톡샵 운영 & GMV MAX ──
    blocks.append(h2("틱톡샵 운영 & GMV MAX"))
    tiktok_sections = ["틱톡샵 & K-Beauty", "틱톡 세미나 & 트렌드"]
    for e in cd_mkt:
        if e["section"] in tiktok_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 마케팅 ──
    blocks.append(h2("마케팅"))
    cd_mkt_urls = set()
    for e in cd_mkt:
        if e["section"] not in tiktok_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
            cd_mkt_urls.add(e["url"])

    # ── 개발 ──
    blocks.append(h2("개발"))
    for e in cd_dev:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 디자인 ──
    blocks.append(h2("디자인"))
    cosduck_design_sections = ["Design System"]
    for e in uiux:
        if e["section"] in cosduck_design_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    # UX 설계
    cosduck_ux_sections = ["UX 설계 & 개선 프로젝트"]
    for e in uiux:
        if e["section"] in cosduck_ux_sections:
            if "코스덕" in e["title"] or "Cosduck" in e["title"]:
                blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 크리에이티브 ──
    blocks.append(h2("크리에이티브"))
    for e in creatives:
        if "코스덕" in e["title"] or "Cosduck" in e["title"] or "코스덕" in e["desc"]:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
    # Brand content guides
    for e in creatives:
        if e["section"] in ("콘텐츠 가이드 & 영상 소스", "브랜드 콘텐츠 가이드 (Notion)", "브랜딩 & 디자인 요청"):
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 물류 & 입고 ──
    blocks.append(h2("물류 & 입고"))
    logistics_sections = ["물류 & 입고 프로세스 (Notion)"]
    for e in commerce:
        if e["section"] in logistics_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 광고 & 캠페인 ──
    blocks.append(h2("광고 & 캠페인"))
    ad_sections = ["광고 & 캠페인 프로세스", "콘텐츠 분석 & 전략"]
    for e in commerce:
        if e["section"] in ad_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 플랫폼 가이드 ──
    blocks.append(h2("플랫폼 가이드"))
    for e in commerce:
        if e["section"] in ("플랫폼 가이드 (Notion)", "Slack 핀 (GDrive)"):
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    return blocks


def build_commerce_blocks():
    """Build all blocks for 커머스 (공통) section."""
    blocks = []
    commerce = parse_entries(LIBRARY + "commerce/references.md")

    # ── 플랫폼 API ──
    blocks.append(h2("플랫폼 API & 인프라"))
    blocks.append(bullet("Amazon SP-API", None, "HEEDA + KIMCHIP 셀러"))
    blocks.append(bullet("Qoo10 Japan API", None, "$QOO10_CERT_KEY"))
    blocks.append(bullet("TikTok Shop API", None, "commerce-api.json"))

    # ── 분석 & 데이터 ──
    blocks.append(h2("분석 & 데이터"))
    blocks.append(bullet("Supabase (커머스 분석 DB)", "https://supabase.com/dashboard", "커머스 데이터 분석 대시보드 — $SUPABASE_URL"))
    blocks.append(bullet("Development 스프레드시트", "https://docs.google.com/spreadsheets/d/1Pct6TMAW1dQsU3dZBg9EFW6kRTW1ZQRzaaRWAf77Is8/", "개발 트래킹"))
    for e in commerce:
        if e["section"] == "Operations (Slack 파일 업로드)":
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 수출바우처 ──
    blocks.append(h2("수출바우처"))
    for e in commerce:
        if "바우처" in e["title"] or "바우처" in e["desc"]:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 브랜드별 ──
    # Read brand sub-products
    brands = [
        ("HEEDA (희다 화장품)", "commerce/heeda/references.md"),
        ("KIMCHIP", "commerce/kimchip/references.md"),
        ("MAPDA", "commerce/mapda/references.md"),
        ("MEDIHAIR", "commerce/medihair/references.md"),
    ]
    for brand_name, brand_path in brands:
        blocks.append(h2(brand_name))
        brand_entries = parse_entries(LIBRARY + brand_path)
        if brand_entries:
            for e in brand_entries:
                blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))
        # Also pull from commerce main
        for e in commerce:
            if brand_name.split(" ")[0].lower() in e["title"].lower() or brand_name.split(" ")[0].lower() in e["desc"].lower():
                if e["url"] and not any(be["url"] == e["url"] for be in brand_entries):
                    blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    return blocks


def build_common_blocks():
    """Build blocks for 공통 참조 section."""
    blocks = []

    dev = parse_entries(LIBRARY + "developers/references.md")
    mkt = parse_entries(LIBRARY + "marketers/references.md")
    uiux_entries = parse_entries(LIBRARY + "uiux/references.md")
    models = parse_entries(LIBRARY + "models/references.md")
    creatives = parse_entries(LIBRARY + "creatives/references.md")

    # ── 개발 공통 ──
    blocks.append(h2("개발 공통"))
    dev_common_sections = ["Internal Tools", "External References"]
    for e in dev:
        if e["section"] in dev_common_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 마케팅 공통 ──
    blocks.append(h2("마케팅 공통"))
    mkt_common_sections = [
        "TikTok & K-Beauty", "Conferences & Learnings",
        "바우처 & 프로모션", "운영 시트 & 작업 문서",
    ]
    for e in mkt:
        if e["section"] in mkt_common_sections:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 디자인 공통 ──
    blocks.append(h2("디자인 공통"))
    design_common = ["Design System", "디자인 레퍼런스 공통"]
    for e in uiux_entries:
        if e["section"] in design_common:
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── AI & 크리에이티브 도구 ──
    blocks.append(h2("AI & 크리에이티브 도구"))
    for e in creatives:
        if e["section"] in ("Production Resources", "Slack 파일 업로드 (GDrive)"):
            blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    # ── 모델 & 촬영 ──
    blocks.append(h2("모델 & 촬영"))
    for e in models:
        blocks.append(bullet(e["title"], e["url"], e["desc"], get_date(e["url"])))

    return blocks


# ── Main ────────────────────────────────────────────────────────

def append_blocks(blocks):
    total = len(blocks)
    for i in range(0, total, 100):
        batch = blocks[i:i+100]
        print("  Sending blocks %d-%d of %d..." % (i+1, min(i+100, total), total))
        result = api_patch(
            "/blocks/%s/children" % PAGE_ID,
            {"children": batch},
        )
        if result is None:
            print("  FAILED!")
            return False
        time.sleep(0.5)
    return True


def main():
    if not TOKEN:
        print("Usage: python3 notion-rebuild.py <NOTION_API_TOKEN>")
        sys.exit(1)

    print("=== Rebuilding Notion page: 마야크루 팀별 폴더 (제품 기반) ===\n")

    all_blocks = []

    # Intro
    all_blocks.append(callout(
        "마야크루 제품/서비스별 참조 문서 모음입니다.\n"
        "슈퍼멤버스 · 슈퍼차트 · 코스덕 · 커머스 4개 영역으로 정리되어 있습니다.\n"
        "마지막 업데이트: 2026-02-24",
        "\U0001F4DA"
    ))
    all_blocks.append(paragraph())
    all_blocks.append(toc())
    all_blocks.append(paragraph())

    # ── 슈퍼멤버스 ──
    print("Building 슈퍼멤버스...")
    all_blocks.append(divider())
    all_blocks.append(h1("\U0001F3EA 슈퍼멤버스"))
    sm_blocks = build_supermembers_blocks()
    all_blocks.extend(sm_blocks)
    sm_count = sum(1 for b in sm_blocks if b["type"] == "bulleted_list_item")
    print("  → %d entries" % sm_count)

    # ── 슈퍼차트 ──
    print("Building 슈퍼차트...")
    all_blocks.append(divider())
    all_blocks.append(h1("\U0001F4CA 슈퍼차트"))
    sc_blocks = build_superchart_blocks()
    all_blocks.extend(sc_blocks)
    sc_count = sum(1 for b in sc_blocks if b["type"] == "bulleted_list_item")
    print("  → %d entries" % sc_count)

    # ── 코스덕 ──
    print("Building 코스덕...")
    all_blocks.append(divider())
    all_blocks.append(h1("\U0001F338 코스덕"))
    cd_blocks = build_cosduck_blocks()
    all_blocks.extend(cd_blocks)
    cd_count = sum(1 for b in cd_blocks if b["type"] == "bulleted_list_item")
    print("  → %d entries" % cd_count)

    # ── 커머스 ──
    print("Building 커머스...")
    all_blocks.append(divider())
    all_blocks.append(h1("\U0001F6D2 커머스 (공통)"))
    cm_blocks = build_commerce_blocks()
    all_blocks.extend(cm_blocks)
    cm_count = sum(1 for b in cm_blocks if b["type"] == "bulleted_list_item")
    print("  → %d entries" % cm_count)

    # ── 공통 참조 ──
    print("Building 공통 참조...")
    all_blocks.append(divider())
    all_blocks.append(h1("\U0001F4D6 공통 참조"))
    common_blocks = build_common_blocks()
    all_blocks.extend(common_blocks)
    common_count = sum(1 for b in common_blocks if b["type"] == "bulleted_list_item")
    print("  → %d entries" % common_count)

    # Footer
    total_entries = sm_count + sc_count + cd_count + cm_count + common_count
    all_blocks.append(divider())
    all_blocks.append(callout(
        "총 %d개 참조 문서 | Notion %d건 생성일 표기\nAuto×Library 시스템이 자동 수집합니다." % (total_entries, len(date_cache)),
        "\U0001F916"
    ))

    print("\nTotal blocks: %d" % len(all_blocks))
    print("Total entries: %d" % total_entries)
    print("Dates fetched: %d" % len(date_cache))
    print()

    # Send to Notion
    success = append_blocks(all_blocks)
    if success:
        print("\n✅ Done!")
    else:
        print("\n❌ Failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
