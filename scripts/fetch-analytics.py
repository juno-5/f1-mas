#!/usr/bin/env python3
"""
Analytics Data Fetcher — API 실제 호출 → JSON 출력
마스터 에이전트가 분석 전에 반드시 실행해야 하는 데이터 수집기.
할루시네이션 방지: 이 스크립트 출력만이 유일한 데이터 소스.

Usage:
  python3 fetch-analytics.py                  # 전일 데이터 (기본)
  python3 fetch-analytics.py --date 2026-02-24
  python3 fetch-analytics.py --today          # 오늘 현재까지
  python3 fetch-analytics.py --week           # 최근 7일
"""
import os, sys, json, datetime, base64, argparse

def load_env():
    """~/.f1crew/credentials/.env에서 환경변수 로드"""
    env_path = os.path.expanduser("~/.f1crew/credentials/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    val = val.strip().strip("'").strip('"')
                    os.environ.setdefault(key.strip(), val)

def fetch_meta_ads(since_date, until_date):
    """Meta Ads Graph API v21.0 — 캠페인별 성과"""
    import requests
    token = os.environ.get("META_ACCESS_TOKEN", "")
    act_id = os.environ.get("META_AD_ACCOUNT_ID", "")
    if not token or not act_id:
        return {"error": "META_ACCESS_TOKEN or META_AD_ACCOUNT_ID not set"}

    # Account-level summary
    # act_id may already include "act_" prefix
    if not act_id.startswith("act_"):
        act_id = f"act_{act_id}"
    url = f"https://graph.facebook.com/v21.0/{act_id}/insights"
    params = {
        "access_token": token,
        "time_range": json.dumps({"since": since_date, "until": until_date}),
        "fields": "spend,impressions,clicks,ctr,cpc,cpm,actions,cost_per_action_type",
        "limit": 1,
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        summary = r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}", "body": r.text[:500]}
    except Exception as e:
        summary = {"error": str(e)}

    # Campaign-level breakdown
    params["level"] = "campaign"
    params["fields"] = "campaign_name,spend,impressions,clicks,ctr,actions,cost_per_action_type"
    params["limit"] = 20
    try:
        r = requests.get(url, params=params, timeout=30)
        campaigns = r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        campaigns = {"error": str(e)}

    # Ad-level top performers (by spend)
    params["level"] = "ad"
    params["fields"] = "ad_name,spend,impressions,clicks,ctr,actions"
    params["sort"] = "spend_descending"
    params["limit"] = 5
    try:
        r = requests.get(url, params=params, timeout=30)
        top_ads = r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        top_ads = {"error": str(e)}

    return {
        "source": "meta_ads_api",
        "period": {"since": since_date, "until": until_date},
        "account_summary": summary,
        "campaigns": campaigns,
        "top_ads": top_ads,
    }


def fetch_ga4(since_date, until_date):
    """GA4 Data API v1beta — 두 프로퍼티 (앱 + 사장님사이트)"""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric
        )
        from google.oauth2 import service_account
    except ImportError:
        return {"error": "google-analytics-data package not installed. pip install google-analytics-data"}

    sa_path = os.path.expanduser("~/.f1crew/credentials/analytics/google-ga4-service-account.json")
    if not os.path.exists(sa_path):
        sa_path = os.path.expanduser("~/.f1crew/credentials/google-ga4-service-account.json")
    if not os.path.exists(sa_path):
        return {"error": f"Service account file not found"}

    creds = service_account.Credentials.from_service_account_file(
        sa_path, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = BetaAnalyticsDataClient(credentials=creds)

    properties = {
        "app": "325653255",
        "admin_site": "283026891",
    }

    metrics_list = [
        "activeUsers", "sessions", "newUsers",
        "screenPageViews", "bounceRate",
        "averageSessionDuration", "sessionsPerUser",
    ]

    results = {}
    for name, prop_id in properties.items():
        try:
            request = RunReportRequest(
                property=f"properties/{prop_id}",
                date_ranges=[DateRange(start_date=since_date, end_date=until_date)],
                metrics=[Metric(name=m) for m in metrics_list],
            )
            response = client.run_report(request)
            row_data = {}
            if response.rows:
                for i, header in enumerate(response.metric_headers):
                    val = response.rows[0].metric_values[i].value
                    try:
                        val = float(val)
                        if val == int(val):
                            val = int(val)
                    except ValueError:
                        pass
                    row_data[header.name] = val
            results[name] = row_data
        except Exception as e:
            results[name] = {"error": str(e)}

    return {
        "source": "ga4_data_api",
        "period": {"since": since_date, "until": until_date},
        "properties": results,
    }


def fetch_mixpanel(since_date, until_date):
    """Mixpanel Segmentation API — 주요 이벤트 카운트 + 유니크 유저"""
    import requests
    secret = os.environ.get("MIXPANEL_API_SECRET", "")
    if not secret:
        return {"error": "MIXPANEL_API_SECRET not set"}

    auth = base64.b64encode(f"{secret}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Accept": "application/json"}

    key_events = [
        "signIn", "impressionHome", "viewCampaignList", "viewCampaignDetail",
        "clickCampaignApplyBtn", "writeApplication", "viewSubmitApplication",
        "submitApplicationComplete", "writeAccountInfo", "registerSucceeded",
    ]

    url_seg = "https://mixpanel.com/api/2.0/segmentation"

    def _mixpanel_get(params, max_retries=3):
        """Rate-limit aware GET with exponential backoff"""
        import time
        for attempt in range(max_retries):
            try:
                r = requests.get(url_seg, params=params, headers=headers, timeout=15)
                if r.status_code == 200:
                    return r.json()
                elif r.status_code == 429:
                    wait = min(2 ** attempt * 5, 30)  # 5s, 10s, 20s
                    time.sleep(wait)
                    continue
                else:
                    return {"error": f"HTTP {r.status_code}"}
            except Exception as e:
                return {"error": str(e)}
        return {"error": "rate_limit_exceeded_after_retries"}

    # Event counts (general)
    event_counts = {}
    rate_limited = False
    for evt in key_events:
        params = {
            "from_date": since_date,
            "to_date": until_date,
            "event": evt,
            "type": "general",
            "unit": "day",
        }
        result = _mixpanel_get(params)
        if isinstance(result, dict) and "error" in result:
            event_counts[evt] = None
            if "rate_limit" in str(result.get("error", "")):
                rate_limited = True
        else:
            vals = result.get("data", {}).get("values", {})
            count = 0
            for k, v in vals.items():
                if isinstance(v, dict):
                    count += sum(v.values())
            event_counts[evt] = count

    # Unique users for key events
    unique_users = {}
    for evt in ["signIn", "impressionHome", "submitApplicationComplete"]:
        params = {
            "from_date": since_date,
            "to_date": until_date,
            "event": evt,
            "type": "unique",
            "unit": "day",
        }
        result = _mixpanel_get(params)
        if isinstance(result, dict) and "error" in result:
            unique_users[evt] = None
        else:
            vals = result.get("data", {}).get("values", {})
            count = 0
            for k, v in vals.items():
                if isinstance(v, dict):
                    count += sum(v.values())
            unique_users[evt] = count

    total = sum(v for v in event_counts.values() if isinstance(v, int))
    resp = {
        "source": "mixpanel_segmentation_api",
        "period": {"since": since_date, "until": until_date},
        "event_counts": event_counts,
        "unique_users": unique_users,
        "total_events": total,
        "note": "No 'purchase' event exists in this Mixpanel project. Closest: submitApplicationComplete",
    }
    if rate_limited:
        resp["warning"] = "Some events returned None due to Mixpanel rate limit (60 req/hour). Retry later."
    return resp


def main():
    parser = argparse.ArgumentParser(description="Fetch analytics data from Meta Ads, GA4, Mixpanel")
    parser.add_argument("--date", help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="Today's data (partial)")
    parser.add_argument("--week", action="store_true", help="Last 7 days")
    parser.add_argument("--source", choices=["meta", "ga4", "mixpanel", "all"], default="all")
    args = parser.parse_args()

    load_env()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    if args.today:
        since_date = today.isoformat()
        until_date = today.isoformat()
        period_label = "today"
    elif args.week:
        since_date = (today - datetime.timedelta(days=7)).isoformat()
        until_date = today.isoformat()
        period_label = "week"
    elif args.date:
        since_date = args.date
        until_date = args.date
        period_label = args.date
    else:
        since_date = yesterday.isoformat()
        until_date = yesterday.isoformat()
        period_label = "yesterday"

    result = {
        "fetch_timestamp": datetime.datetime.now().isoformat(),
        "period_label": period_label,
        "period": {"since": since_date, "until": until_date},
    }

    if args.source in ("meta", "all"):
        result["meta_ads"] = fetch_meta_ads(since_date, until_date)

    if args.source in ("ga4", "all"):
        result["ga4"] = fetch_ga4(since_date, until_date)

    if args.source in ("mixpanel", "all"):
        result["mixpanel"] = fetch_mixpanel(since_date, until_date)

    # Output as JSON — this is the ONLY source of truth
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
