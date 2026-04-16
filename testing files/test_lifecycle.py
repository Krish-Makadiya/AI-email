import requests
import json
import time

API_BASE = "http://localhost:8000"
N8N_WEBHOOK = "http://localhost:5678/webhook-test/meeting-logic"

def run_test(action="propose_times", start_time=None):
    print(f"\n--- Starting SoMailer Test: ACTION='{action}' ---")
    
    payload = {
        "email_action_id": 99999,
        "action": action,
        "recipient": "tanishq-test@example.com",
        "mail": {
            "sender_name": "Tanishq-Test",
            "sender_mail": "tanishq-test@example.com",
            "subject": f"Test {action} Loop"
        }
    }
    
    if start_time:
        payload["start_time"] = start_time
    elif action == "confirm":
        payload["start_time"] = "2026-04-20T10:00:00Z"

    print(f"[STEP 1] Sending signal to n8n...")
    try:
        response = requests.post(N8N_WEBHOOK, json=payload, timeout=60)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Error calling webhook: {e}")
        return

    print(f"[STEP 2] Verifying via API for '{action}' response...")
    time.sleep(3) # Give n8n time to process
    
    try:
        drafts_resp = requests.get(f"{API_BASE}/drafts")
        drafts = drafts_resp.json().get('drafts', [])
        # Find the most recent draft for our test recipient
        test_draft = next((d for d in reversed(drafts) if d['recipient'] == "tanishq-test@example.com"), None)
        
        if test_draft:
            print(f"SUCCESS: Draft created!")
            print(f"Draft Type: {test_draft['type']}")
            print(f"Subject: {test_draft['subject']}")
            print(f"Reasoning: {test_draft.get('reasoning', 'N/A')}")
        else:
            print(f"FAILURE: No draft found for this operation.")
            
    except Exception as e:
        print(f"API Check error: {e}")

if __name__ == "__main__":
    import sys
    action_to_run = sys.argv[1] if len(sys.argv) > 1 else "confirm"
    run_test(action_to_run)
