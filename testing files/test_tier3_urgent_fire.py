"""
Test Script: Post Urgent_Fire v2 -- Tier 3 (High Urgency, 71-85%)
==================================================================
Tier 3 behaviour (70 < score <= 85):
  - Sends a Twilio SMS/WhatsApp alert
  - Creates a Jira Bug (High Priority)
  - Sets status = 'flagated_high'

Run:
  python "testing files/test_tier3_urgent_fire.py"           # dry run
  python "testing files/test_tier3_urgent_fire.py" --live    # hits real n8n
  python "testing files/test_tier3_urgent_fire.py" --live --score 80 --id 371
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


def build_tier3_payload(urgency_score: int = 78, card_id: int = 1) -> dict:
    """
    Tier 3 conditions:
      - status == 'escalated'               -> Status Switch routes to Urgency Tier Switch
      - 70 < analysis.urgency_score <= 85   -> output[2] (Tier 3)

    Expected n8n path:
      Webhook -> Status Switch [Escalate] -> Urgency Tier Switch [Tier 3]
      -> Tier 3: Twilio SMS -> Tier 3: Jira Bug (High Priority)
      -> Prepare flagated_high -> Update Postgres -> Respond to Webhook
    """
    assert isinstance(card_id, int) and card_id > 0, (
        f"card_id must be a positive integer matching email_actions.id, got: {card_id!r}"
    )
    assert 71 <= urgency_score <= 85, (
        f"Tier 3 requires urgency_score in [71, 85], got {urgency_score}"
    )
    return {
        "status": "escalated",
        "card_id": card_id,
        "classification": "Urgent_Fire",
        "analysis": {
            "urgency_score": urgency_score,
            "summary": (
                f"[TIER 3 TEST] High-urgency alert -- score {urgency_score}%. "
                "Database replication lag exceeded 60 seconds on prod-db-replica-02. "
                "Write transactions are queuing. Immediate DBA intervention required."
            ),
            "entities": {
                "issue_type": "ReplicationLag",
                "affected_system": "prod-db-replica-02",
                "routing": "Database Engineering",
                "error_code": "REPL_LAG_60S"
            }
        },
        "mail": {
            "id": "mock-mail-tier3-001",
            "subject": "[TIER 3 TEST] CRITICAL: DB Replication Lag on prod-db-replica-02",
            "body": "Replication lag on prod-db-replica-02 has exceeded 60s. DBA action needed immediately.",
            "sender_name": "SoMailer QA Suite",
            "sender_mail": "qa-tier3@somailer.local"
        },
        "alert": {
            "alert_message": f"DB replication lag >60s on prod-db-replica-02 (score: {urgency_score}%)",
            "recipient_name": "Database Engineering"
        },
        "jira": {
            "id": "TEST-003",
            "ticket_link": "https://jira.corporate.com/browse/TEST-003"
        }
    }


def validate_payload(payload: dict) -> list:
    issues = []
    score = payload.get("analysis", {}).get("urgency_score")
    if score is None:
        issues.append("[FAIL] Missing: analysis.urgency_score")
    elif not (71 <= score <= 85):
        issues.append(f"[FAIL] Tier 3 requires score 71-85, got {score}")

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
    print("  POST URGENT_FIRE v2 -- TIER 3 DRY RUN")
    print("=" * 62)
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print(f"  Tier       : 3 -- High Urgency (71-85%)")
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
        print("\n[VALIDATION] PASS - All checks passed -- payload is Tier 3 compliant.\n")

    print("[EXPECTED BEHAVIOUR IN n8n]")
    print("  1. Webhook                  -> receives POST body")
    print("  2. Status Switch            -> routes to 'Escalate' output")
    print("  3. Urgency Tier Switch      -> 70 < score <= 85 -> output[2]")
    print("  4. Tier 3: Twilio SMS       -> sends WhatsApp/SMS alert")
    print("  5. Tier 3: Jira Bug         -> creates High Priority Jira Bug")
    print("  6. Prepare flagated_high    -> sets scheduling_status = 'flagated_high'")
    print("  7. Update Postgres          -> persists status in email_actions")
    print("  8. Respond to Webhook       -> 200 OK\n")

    print("[PAYLOAD PREVIEW]")
    print(json.dumps(payload, indent=2))
    print()


def live_run(payload: dict, url: str) -> None:
    if not HAS_REQUESTS:
        print("[ERROR] 'requests' library not installed. Run: pip install requests")
        sys.exit(1)

    print("\n" + "=" * 62)
    print("  POST URGENT_FIRE v2 -- TIER 3 LIVE TEST")
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

    print("[>>] Sending Tier 3 payload to n8n...")
    try:
        resp = requests.post(url, json=payload, timeout=15)
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
        print("[ERROR] TIMEOUT - n8n did not respond within 15 seconds.")
        print("        NOTE: Tier 3 makes a real Twilio SMS call which may take longer.")
        sys.exit(1)
    print()


def main():
    default_id = get_latest_db_id()

    parser = argparse.ArgumentParser(
        description="Test Tier 3 of the Post Urgent_Fire v2 n8n workflow."
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
        default=78,
        help="Urgency score (must be 71-85 for Tier 3). Default: 78"
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

    payload = build_tier3_payload(urgency_score=args.score, card_id=args.id)

    if args.live:
        url = TEST_WEBHOOK_URL if args.test_mode else N8N_WEBHOOK_URL
        live_run(payload, url)
    else:
        dry_run(payload)


if __name__ == "__main__":
    main()
