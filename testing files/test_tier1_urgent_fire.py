"""
Test Script: Post Urgent_Fire v2 — Tier 1 (Low Urgency, 0–50%)
================================================================
Tier 1 behaviour (score <= 50):
  - Sends a Slack message to #prod-issues
  - Sets status = 'flagged_low'

Workflow webhook path:
  POST http://localhost:5678/webhook/c69bd0d4-a726-4c1c-a9a7-bf7a9337c32a

Run:
  python "testing files/test_tier1_urgent_fire.py"
  python "testing files/test_tier1_urgent_fire.py" --score 35   # custom score
  python "testing files/test_tier1_urgent_fire.py" --live       # hits real n8n
"""

import argparse
import json
import sys
from datetime import datetime, timezone

# Force UTF-8 output on Windows terminals to avoid cp1252 encoding errors
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Optional requests import ──────────────────────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Config ────────────────────────────────────────────────────────
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/c69bd0d4-a726-4c1c-a9a7-bf7a9337c32a"
TEST_WEBHOOK_URL = "http://localhost:5678/webhook-test/c69bd0d4-a726-4c1c-a9a7-bf7a9337c32a"


def build_tier1_payload(urgency_score: int = 30, card_id: int = 1) -> dict:
    """
    Constructs a minimal, valid webhook payload that will route
    the Post Urgent_Fire v2 workflow into Tier 1.

    Tier 1 conditions:
      - status == 'escalated'           -> routes into Urgency Tier Switch
      - analysis.urgency_score <= 50    -> falls into output[0] of the Switch

    IMPORTANT: card_id must be a real integer that exists in the
    email_actions table, otherwise Postgres Update will fail with
    'row not found'. Run this to find a valid ID:
      SELECT id FROM email_actions LIMIT 5;
    """
    assert isinstance(card_id, int) and card_id > 0, (
        f"card_id must be a positive integer matching email_actions.id, got: {card_id!r}"
    )
    assert 0 <= urgency_score <= 50, (
        f"Tier 1 requires urgency_score in [0, 50], got {urgency_score}"
    )

    return {
        "status": "escalated",        # triggers the Escalate branch in Status Switch
        "card_id": card_id,
        "classification": "Urgent_Fire",
        "analysis": {
            "urgency_score": urgency_score,
            "summary": (
                f"[TIER 1 TEST] Low-urgency alert — score {urgency_score}%. "
                "Disk utilisation crossed 75%% on staging-worker-01. "
                "No immediate production impact anticipated."
            ),
            "entities": {
                "issue_type": "DiskSpaceWarning",
                "affected_system": "staging-worker-01",
                "routing": "DevOps",
                "error_code": "DISK_75PCT"
            }
        },
        "mail": {
            "id": "mock-mail-tier1-001",
            "subject": "[TIER 1 TEST] Disk Usage Warning on staging-worker-01",
            "body": "Disk usage has exceeded 75% on staging-worker-01. Please review.",
            "sender_name": "SoMailer Test Suite",
            "sender_mail": "test@somailer.local"
        },
        "alert": {
            "alert_message": f"Disk at 75% on staging-worker-01 (score: {urgency_score}%)",
            "recipient_name": "DevOps"
        },
        "jira": {
            "id": "TEST-001",
            "ticket_link": "https://jira.corporate.com/browse/TEST-001"
        }
    }


def validate_payload(payload: dict) -> list[str]:
    """Returns a list of validation errors (empty = all good)."""
    issues = []

    score = payload.get("analysis", {}).get("urgency_score")
    if score is None:
        issues.append("[FAIL] Missing: analysis.urgency_score")
    elif not (0 <= score <= 50):
        issues.append(f"[FAIL] Tier 1 requires score 0-50, got {score}")

    card_id = payload.get("card_id")
    if not isinstance(card_id, int) or card_id <= 0:
        issues.append(f"[FAIL] card_id must be a positive integer, got: {card_id!r} ({type(card_id).__name__})")

    if payload.get("status") != "escalated":
        issues.append(
            f"[FAIL] status must be 'escalated' for Tier 1 routing, got '{payload.get('status')}'"
        )

    for field in ["mail", "alert", "jira", "card_id"]:
        if field not in payload:
            issues.append(f"[FAIL] Missing required field: {field}")

    return issues


def dry_run(payload: dict) -> None:
    """Prints the payload and validation results without making any network call."""
    print("\n" + "=" * 62)
    print("  POST URGENT_FIRE v2 — TIER 1 DRY RUN")
    print("=" * 62)
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print(f"  Tier       : 1 — Low Urgency (≤ 50%)")
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
        print("\n[VALIDATION] PASS - All checks passed -- payload is Tier 1 compliant.\n")

    print("[EXPECTED BEHAVIOUR IN n8n]")
    print("  1. Webhook               → receives POST body")
    print("  2. Status Switch         → routes to 'Escalate' output")
    print("  3. Urgency Tier Switch   → score ≤ 50 → output[0]")
    print("  4. Tier 1: Slack         → posts to #prod-issues")
    print("  5. Prepare flagged_low   → sets status = 'flagged_low'")
    print("  6. Postgres Update       → persists status in email_actions")
    print("  7. Respond to Webhook    → 200 OK\n")

    print("[PAYLOAD PREVIEW]")
    print(json.dumps(payload, indent=2))
    print()


def live_run(payload: dict, url: str) -> None:
    """Fires the payload at the live n8n webhook and prints the result."""
    if not HAS_REQUESTS:
        print("[ERROR] 'requests' library not installed. Run: pip install requests")
        sys.exit(1)

    print("\n" + "=" * 62)
    print("  POST URGENT_FIRE v2 — TIER 1 LIVE TEST")
    print("=" * 62)
    print(f"  Target URL : {url}")
    print(f"  Score      : {payload['analysis']['urgency_score']}%")
    print(f"  Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print("=" * 62 + "\n")

    errors = validate_payload(payload)
    if errors:
        print("[VALIDATION] FAILED — aborting live call:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print(f"[>>] Sending Tier 1 payload to n8n...")
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
    # Auto-detect a valid ID from the database if --id is not supplied
    default_id = 1
    try:
        import psycopg2
        _conn = psycopg2.connect("postgresql://user:password@localhost:5432/email_intelligence")
        _cur = _conn.cursor()
        _cur.execute("SELECT id FROM email_actions ORDER BY id DESC LIMIT 1")
        _row = _cur.fetchone()
        if _row:
            default_id = _row[0]
        _conn.close()
    except Exception:
        pass  # Fall back to 1 if DB is unreachable

    parser = argparse.ArgumentParser(
        description="Test Tier 1 of the Post Urgent_Fire v2 n8n workflow."
    )
    parser.add_argument(
        "--id",
        type=int,
        default=default_id,
        help=f"Integer ID of the email_actions row to update (must exist in DB). Auto-detected: {default_id}"
    )
    parser.add_argument(
        "--score",
        type=int,
        default=30,
        help="Urgency score to send (must be 0-50 for Tier 1). Default: 30"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Send the payload to the real n8n webhook (default: dry run / preview only)"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Use webhook-test URL (for n8n manual test mode) instead of the live webhook"
    )
    args = parser.parse_args()

    payload = build_tier1_payload(urgency_score=args.score, card_id=args.id)

    if args.live:
        url = TEST_WEBHOOK_URL if args.test_mode else N8N_WEBHOOK_URL
        live_run(payload, url)
    else:
        dry_run(payload)


if __name__ == "__main__":
    main()
