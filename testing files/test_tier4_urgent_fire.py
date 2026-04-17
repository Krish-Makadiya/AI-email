"""
Test Script: Post Urgent_Fire v2 -- Tier 4 (Critical, 86-100%)
===============================================================
Tier 4 behaviour (score > 85):
  - Triggers a Twilio Voice Call
  - Creates an Emergency Jira Bug
  - Sends <!channel> Slack broadcast
  - Sets status = 'critical_escalation'

Run:
  python "testing files/test_tier4_urgent_fire.py"           # dry run
  python "testing files/test_tier4_urgent_fire.py" --live    # hits real n8n
  python "testing files/test_tier4_urgent_fire.py" --live --score 92 --id 371
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


def build_tier4_payload(urgency_score: int = 92, card_id: int = 1) -> dict:
    """
    Tier 4 conditions:
      - status == 'escalated'           -> Status Switch routes to Urgency Tier Switch
      - analysis.urgency_score > 85     -> output[3] (Tier 4)

    Expected n8n path:
      Webhook -> Status Switch [Escalate] -> Urgency Tier Switch [Tier 4]
      -> Tier 4: Twilio Call -> Tier 4: Emergency Jira
      -> Tier 4: Slack <!channel> -> Prepare critical
      -> Update Postgres -> Respond to Webhook

    WARNING: This test triggers a REAL Twilio voice call to +919370811516.
    """
    assert isinstance(card_id, int) and card_id > 0, (
        f"card_id must be a positive integer matching email_actions.id, got: {card_id!r}"
    )
    assert 86 <= urgency_score <= 100, (
        f"Tier 4 requires urgency_score in [86, 100], got {urgency_score}"
    )
    return {
        "status": "escalated",
        "card_id": card_id,
        "classification": "Urgent_Fire",
        "analysis": {
            "urgency_score": urgency_score,
            "summary": (
                f"[TIER 4 TEST] CRITICAL alert -- score {urgency_score}%. "
                "Complete production database outage on prod-db-primary. "
                "All write operations failing. Revenue impact active. "
                "Immediate executive and engineering leadership escalation required."
            ),
            "entities": {
                "issue_type": "DatabaseOutage",
                "affected_system": "prod-db-primary",
                "routing": "Executive Escalation",
                "error_code": "DB_OUTAGE_PROD"
            }
        },
        "mail": {
            "id": "mock-mail-tier4-001",
            "subject": "[TIER 4 TEST] PROD OUTAGE: prod-db-primary completely down",
            "body": "prod-db-primary is unreachable. All write operations are failing. Business impact: CRITICAL.",
            "sender_name": "SoMailer QA Suite",
            "sender_mail": "qa-tier4@somailer.local"
        },
        "alert": {
            "alert_message": f"PROD DB OUTAGE on prod-db-primary (score: {urgency_score}%)",
            "recipient_name": "Executive Escalation"
        },
        "jira": {
            "id": "TEST-004",
            "ticket_link": "https://jira.corporate.com/browse/TEST-004"
        }
    }


def validate_payload(payload: dict) -> list:
    issues = []
    score = payload.get("analysis", {}).get("urgency_score")
    if score is None:
        issues.append("[FAIL] Missing: analysis.urgency_score")
    elif not (86 <= score <= 100):
        issues.append(f"[FAIL] Tier 4 requires score 86-100, got {score}")

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
    print("  POST URGENT_FIRE v2 -- TIER 4 DRY RUN")
    print("=" * 62)
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print(f"  Tier       : 4 -- CRITICAL (86-100%)")
    print(f"  Score      : {payload['analysis']['urgency_score']}%")
    print(f"  Status     : {payload['status']}")
    print(f"  Card ID    : {payload['card_id']}")
    print("=" * 62)
    print()
    print("  [!] WARNING: --live will trigger a REAL Twilio voice call.")
    print()

    errors = validate_payload(payload)
    if errors:
        print("[VALIDATION] FAILED:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("[VALIDATION] PASS - All checks passed -- payload is Tier 4 compliant.\n")

    print("[EXPECTED BEHAVIOUR IN n8n]")
    print("  1. Webhook                   -> receives POST body")
    print("  2. Status Switch             -> routes to 'Escalate' output")
    print("  3. Urgency Tier Switch       -> score > 85 -> output[3]")
    print("  4. Tier 4: Twilio Call       -> places a VOICE CALL to +919370811516")
    print("  5. Tier 4: Emergency Jira    -> creates Emergency Jira Bug")
    print("  6. Tier 4: Slack <!channel>  -> broadcasts to entire channel")
    print("  7. Prepare critical          -> sets scheduling_status = 'critical_escalation'")
    print("  8. Update Postgres           -> persists status in email_actions")
    print("  9. Respond to Webhook        -> 200 OK\n")

    print("[PAYLOAD PREVIEW]")
    print(json.dumps(payload, indent=2))
    print()


def live_run(payload: dict, url: str) -> None:
    if not HAS_REQUESTS:
        print("[ERROR] 'requests' library not installed. Run: pip install requests")
        sys.exit(1)

    print("\n" + "=" * 62)
    print("  POST URGENT_FIRE v2 -- TIER 4 LIVE TEST")
    print("=" * 62)
    print(f"  Target URL : {url}")
    print(f"  Score      : {payload['analysis']['urgency_score']}%")
    print(f"  Card ID    : {payload['card_id']}")
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print("=" * 62)
    print()
    print("  [!] A real Twilio VOICE CALL will be placed to +919370811516.")
    print("      Timeout is set to 30s to allow the call to initiate.")
    print()

    errors = validate_payload(payload)
    if errors:
        print("[VALIDATION] FAILED -- aborting live call:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("[>>] Sending Tier 4 CRITICAL payload to n8n...")
    try:
        resp = requests.post(url, json=payload, timeout=30)
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
        print("[ERROR] TIMEOUT - n8n did not respond within 30 seconds.")
        print("        The Twilio voice call may still have been initiated.")
        sys.exit(1)
    print()


def main():
    default_id = get_latest_db_id()

    parser = argparse.ArgumentParser(
        description="Test Tier 4 (CRITICAL) of the Post Urgent_Fire v2 n8n workflow."
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
        default=92,
        help="Urgency score (must be 86-100 for Tier 4). Default: 92"
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

    payload = build_tier4_payload(urgency_score=args.score, card_id=args.id)

    if args.live:
        url = TEST_WEBHOOK_URL if args.test_mode else N8N_WEBHOOK_URL
        live_run(payload, url)
    else:
        dry_run(payload)


if __name__ == "__main__":
    main()
