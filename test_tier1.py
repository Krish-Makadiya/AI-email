import requests
import json
import time
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = "http://127.0.0.1:8000/process-email"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/email_intelligence")

def get_random_card_id():
    """Fetches a random numeric ID from the email_actions table."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM email_actions ORDER BY RANDOM() LIMIT 1;")
        row = cursor.fetchone()
        conn.close()
        return int(row[0]) if row else 1
    except Exception as e:
        print(f"[QA] DB Lookup Error: {e}. Falling back to ID 1.")
        return 1

def run_tier1_test():
    """
    Simulates a low-urgency student outreach to verify Tier 1 Escalation logic.
    Constraint: Should result in urgency_score < 50% and 'flagged_low' status.
    """
    dynamic_id = get_random_card_id()
    payload = {
        "sender_email": "tester@qa.internal",
        "subject": "INCIDENT (Low Priority): Minor bug on your LinkedIn project page",
        "content": "Hey, just noticed a small bug in your project description. Not critical!",
        "is_1on1": True,
        "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "card_id": dynamic_id
    }

    print(f"[QA] Dispatching Tier 1 Test Signal to Gateway...")
    print(f"Endpoint: {API_URL}")
    print(f"Subject: {payload['subject']}")

    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print("\n[QA] Gateway Response Received!")
        print(f"Status: {result.get('status')}")
        
        cmd = result.get('command_package', {})
        analysis = cmd.get('payload', {}).get('analysis', {})
        score = analysis.get('urgency_score', 0)
        
        print(f"AI Calculated Urgency: {score}%")
        print(f"Action: {cmd.get('action')}")
        
        if score <= 50:
            print(f"SUCCESS: Signal correctly categorized as Tier 1 (Low Urgency).")
        else:
            print(f"WARNING: Signal scored {score}%. Logic may be too aggressive for Tier 1.")
            
    except Exception as e:
        print(f"ERROR: [QA] Test Failed: {str(e)}")

if __name__ == "__main__":
    run_tier1_test()
