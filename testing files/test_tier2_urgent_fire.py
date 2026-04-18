"""
Test Script: Post Urgent_Fire v2 -- Tier 2 (Medium Urgency, 51-70%)
====================================================================
Tier 2 behaviour (50 < score <= 70):
  - Creates a Jira Task
  - Sends a Slack alert tagging @on-call
  - Sets status = 'flagged_medium'

Run:
  python "testing files/test_tier2_urgent_fire.py"           # dry run
  python "testing files/test_tier2_urgent_fire.py" --live    # hits real n8n
  python "testing files/test_tier2_urgent_fire.py" --live --score 65 --id 371
"""

import argparse
import json
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

N8N_WEBHOOK_URL  = "http://localhost:5678/webhook/c69bd0d4-a726-4c1c-a9a7-bf7a9337c32a"
TEST_WEBHOOK_URL = "http://localhost:5678/webhook-test/c69bd0d4-a726-4c1c-a9a7-bf7a9337c32a"
DB_URL           = "postgresql://user:password@localhost:5432/email_intelligence"


def get_latest_db_id() -> int:
    if not HAS_PSYCOPG2:
        return 1
    try:
        conn = psycopg2.connect(DB_URL)
        cur  = conn.cursor()
        cur.execute("SELECT id FROM email_actions ORDER BY id DESC LIMIT 1")
        row  = cur.fetchone()
        conn.close()
        return row[0] if row else 1
    except Exception:
        return 1


def build_tier2_payload(urgency_score: int = 60, card_id: int = 1) -> dict:
    """
    Tier 2 conditions:
      - status == 'escalated'          -> Status Switch routes to Urgency Tier Switch
      - 50 < analysis.urgency_score <= 70  -> output[1] (Tier 2)

    Expected n8n path:
      Webhook -> Status Switch [Escalate] -> Urgency Tier Switch [Tier 2]
      -> Tier 2: Jira Task -> Tier 2: Slack Alert
      -> Prepare flagged_medium -> Update Postgres -> Respond to Webhook
    """
    assert isinstance(card_id, int) and card_id > 0, (
        f"card_id must be a positive integer matching email_actions.id, got: {card_id!r}"
    )
    assert 51 <= urgency_score <= 70, (
        f"Tier 2 requires urgency_score in [51, 70], got {urgency_score}"
    )
    return {
        "status": "escalated",
        "card_id": card_id,
        "classification": "Urgent_Fire",
        "analysis": {
            "urgency_score": urgency_score,
            "summary": (
                f"[TIER 2 TEST] Medium-urgency alert -- score {urgency_score}%. "
                "API response times degraded on payment-service. "
                "P95 latency spiked to 3200ms (threshold: 1000ms). "
                "On-call intervention recommended."
            ),
            "entities": {
                "issue_type": "HighLatency",
                "affected_system": "payment-service",
                "routing": "Backend Engineering",
                "error_code": "LATENCY_P95"
            }
        },
        "mail": {
            "id": "mock-mail-tier2-001",
            "subject": "[TIER 2 TEST] Payment Service Latency Spike Detected",
            "body": "P95 latency on payment-service has exceeded SLO threshold. Immediate review required.",
            "sender_name": "SoMailer QA Suite",
            "sender_mail": "qa-tier2@somailer.local"
        },
        "alert": {
            "alert_message": f"Payment service P95 latency spike (score: {urgency_score}%)",
            "recipient_name": "Backend Engineering"
        },
        "jira": {
            "id": "TEST-002",
            "ticket_link": "https://jira.corporate.com/browse/TEST-002"
        }
    }


def validate_payload(payload: dict) -> list:
    issues = []
    score = payload.get("analysis", {}).get("urgency_score")
    if score is None:
        issues.append("[FAIL] Missing: analysis.urgency_score")
    elif not (51 <= score <= 70):
        issues.append(f"[FAIL] Tier 2 requires score 51-70, got {score}")

    card_id = payload.get("card_id")
    if not isinstance(card_id, int) or card_id <= 0:
        issues.append(f"[FAIL] card_id must be a positive integer, got: {card_id!r} ({type(card_id).__name__})")

    if payload.get("status") != "escalated":
        issues.append(f"[FAIL] status must be 'escalated', got '{payload.get('status')}'")

    for field in ["mail", "alert", "jira", "card_id"]:
        if field not in payload:
            issues.append(f"[FAIL] Missing required field: {field}")

    return issues


def dry_run(payload: dict) -> None:
    print("\n" + "=" * 62)
    print("  POST URGENT_FIRE v2 -- TIER 2 DRY RUN")
    print("=" * 62)
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print(f"  Tier       : 2 -- Medium Urgency (51-70%)")
    print(f"  Score      : {payload['analysis']['urgency_score']}%")
    print(f"  Status     : {payload['status']}")
    print(f"  Card ID    : {payload['card_id']}")
    print("=" * 62)

    errors = validate_payload(payload)
    if errors:
        print("\n[VALIDATION] FAILED:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("\n[VALIDATION] PASS - All checks passed -- payload is Tier 2 compliant.\n")

    print("[EXPECTED BEHAVIOUR IN n8n]")
    print("  1. Webhook               -> receives POST body")
    print("  2. Status Switch         -> routes to 'Escalate' output")
    print("  3. Urgency Tier Switch   -> 51 < score <= 70 -> output[1]")
    print("  4. Tier 2: Jira Task     -> creates a Jira Task")
    print("  5. Tier 2: Slack Alert   -> sends @on-call Slack message")
    print("  6. Prepare flagged_medium -> sets scheduling_status = 'flagged_medium'")
    print("  7. Update Postgres       -> persists status in email_actions")
    print("  8. Respond to Webhook    -> 200 OK\n")

    print("[PAYLOAD PREVIEW]")
    print(json.dumps(payload, indent=2))
    print()


def live_run(payload: dict, url: str) -> None:
    if not HAS_REQUESTS:
        print("[ERROR] 'requests' library not installed. Run: pip install requests")
        sys.exit(1)

    print("\n" + "=" * 62)
    print("  POST URGENT_FIRE v2 -- TIER 2 LIVE TEST")
    print("=" * 62)
    print(f"  Target URL : {url}")
    print(f"  Score      : {payload['analysis']['urgency_score']}%")
    print(f"  Card ID    : {payload['card_id']}")
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print("=" * 62 + "\n")

    errors = validate_payload(payload)
    if errors:
        print("[VALIDATION] FAILED -- aborting live call:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("[>>] Sending Tier 2 payload to n8n...")
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"[<<] HTTP {resp.status_code}")
        if resp.status_code in (200, 201):
            print("[PASS] SUCCESS - n8n accepted the payload.")
            try:
                print(f"   Response  : {resp.json()}")
            except Exception:
                print(f"   Response  : {resp.text[:200]}")
        else:
            print(f"[WARN] UNEXPECTED STATUS - n8n returned {resp.status_code}")
            print(f"   Body      : {resp.text[:400]}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] CONNECTION REFUSED - is n8n running on localhost:5678?")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("[ERROR] TIMEOUT - n8n did not respond within 10 seconds.")
        sys.exit(1)
    print()


def main():
    default_id = get_latest_db_id()

    parser = argparse.ArgumentParser(
        description="Test Tier 2 of the Post Urgent_Fire v2 n8n workflow."
    )
    parser.add_argument(
        "--id",
        type=int,
        default=default_id,
        help=f"Integer ID of the email_actions row to update. Auto-detected: {default_id}"
    )
    parser.add_argument(
        "--score",
        type=int,
        default=60,
        help="Urgency score (must be 51-70 for Tier 2). Default: 60"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Send payload to real n8n webhook (default: dry run)"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Use webhook-test URL instead of live webhook"
    )
    args = parser.parse_args()

    payload = build_tier2_payload(urgency_score=args.score, card_id=args.id)

    if args.live:
        url = TEST_WEBHOOK_URL if args.test_mode else N8N_WEBHOOK_URL
        live_run(payload, url)
    else:
        dry_run(payload)


if __name__ == "__main__":
    main()
