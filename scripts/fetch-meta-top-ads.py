#!/usr/bin/env python3
"""
Meta Ads Top Performers — 성과 상위 광고 + 포스트 링크
에이전트가 "성과 좋은 소재 보여줘" 요청 시 실행.

Usage:
  python3 fetch-meta-top-ads.py                 # 최근 7일, 상위 10개
  python3 fetch-meta-top-ads.py --days 30       # 최근 30일
  python3 fetch-meta-top-ads.py --limit 5       # 상위 5개
  python3 fetch-meta-top-ads.py --sort ctr      # CTR 기준 정렬 (기본: spend)
  python3 fetch-meta-top-ads.py --sort lead      # 리드 기준 정렬
"""
import os, sys, json, datetime, argparse, requests


def load_env():
    env_path = os.path.expanduser("~/.f1crew/credentials/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    val = val.strip().strip("'").strip('"')
                    os.environ.setdefault(key.strip(), val)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--sort", choices=["spend", "ctr", "lead", "click"], default="spend")
    args = parser.parse_args()

    load_env()
    token = os.environ.get("META_ACCESS_TOKEN", "")
    act_id = os.environ.get("META_AD_ACCOUNT_ID", "")
    if not token or not act_id:
        print(json.dumps({"error": "META_ACCESS_TOKEN or META_AD_ACCOUNT_ID not set"}))
        return
    if not act_id.startswith("act_"):
        act_id = f"act_{act_id}"

    today = datetime.date.today()
    since = (today - datetime.timedelta(days=args.days)).isoformat()
    until = today.isoformat()

    sort_map = {
        "spend": "spend_descending",
        "ctr": "impressions_descending",  # will re-sort by CTR after
        "lead": "impressions_descending",
        "click": "clicks_descending",
    }

    # Step 1: Get ad insights
    url = f"https://graph.facebook.com/v21.0/{act_id}/insights"
    params = {
        "access_token": token,
        "level": "ad",
        "fields": "ad_id,ad_name,spend,impressions,clicks,ctr,actions,cost_per_action_type",
        "time_range": json.dumps({"since": since, "until": until}),
        "sort": sort_map.get(args.sort, "spend_descending"),
        "limit": min(args.limit * 2, 50),  # fetch extra for re-sorting
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        print(json.dumps({"error": f"Insights API HTTP {r.status_code}", "body": r.text[:500]}))
        return

    insights = r.json().get("data", [])
    if not insights:
        print(json.dumps({"error": "No ad data found for this period"}))
        return

    # Parse actions
    for ad in insights:
        ad["_spend"] = float(ad.get("spend", 0))
        ad["_ctr"] = float(ad.get("ctr", 0))
        ad["_leads"] = 0
        ad["_checkouts"] = 0
        ad["_clicks"] = int(ad.get("clicks", 0))
        for action in ad.get("actions", []):
            if action["action_type"] == "lead":
                ad["_leads"] = int(action["value"])
            elif action["action_type"] == "omni_initiated_checkout":
                ad["_checkouts"] = int(action["value"])

    # Re-sort if needed
    if args.sort == "ctr":
        insights.sort(key=lambda x: x["_ctr"], reverse=True)
    elif args.sort == "lead":
        insights.sort(key=lambda x: x["_leads"], reverse=True)

    insights = insights[:args.limit]

    # Step 2: Get creative post links for each ad
    ad_ids = [ad["ad_id"] for ad in insights]

    for ad in insights:
        ad_id = ad["ad_id"]
        try:
            cr = requests.get(
                f"https://graph.facebook.com/v21.0/{ad_id}",
                params={
                    "access_token": token,
                    "fields": "creative{effective_object_story_id,thumbnail_url}",
                },
                timeout=10,
            )
            if cr.status_code == 200:
                creative = cr.json().get("creative", {})
                story_id = creative.get("effective_object_story_id", "")
                if story_id and "_" in story_id:
                    page_id, post_id = story_id.split("_", 1)
                    ad["_post_url"] = f"https://www.facebook.com/{page_id}/posts/{post_id}"
                else:
                    ad["_post_url"] = None
                ad["_thumbnail"] = creative.get("thumbnail_url")
            else:
                ad["_post_url"] = None
                ad["_thumbnail"] = None
        except Exception:
            ad["_post_url"] = None
            ad["_thumbnail"] = None

    # Output
    result = {
        "period": {"since": since, "until": until, "days": args.days},
        "sort_by": args.sort,
        "total_ads": len(insights),
        "ads": [],
    }

    for i, ad in enumerate(insights):
        result["ads"].append({
            "rank": i + 1,
            "name": ad.get("ad_name", ""),
            "ad_id": ad.get("ad_id", ""),
            "spend": ad["_spend"],
            "impressions": int(ad.get("impressions", 0)),
            "clicks": ad["_clicks"],
            "ctr": round(ad["_ctr"], 2),
            "leads": ad["_leads"],
            "checkouts": ad["_checkouts"],
            "post_url": ad.get("_post_url"),
            "thumbnail": ad.get("_thumbnail"),
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
