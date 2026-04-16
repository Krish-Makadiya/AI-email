import requests
import json
import time

API_BASE = "http://localhost:8000"
N8N_WEBHOOK = "http://localhost:5678/webhook-test/meeting-logic"

def test_full_lifecycle():
    print("Starting SoMailer Live Fire Test...")
    
    # 1. Trigger Initial Ingestion & Probe
    payload = {
        "email_action_id": 99999, # Mock ID for tracking
        "action": "propose_times",
        "mail": {
            "sender_name": "Tanishq-Test",
            "sender_mail": "tanishq-test@example.com",
            "subject": "Collaboration on Agentic AI Project",
            "content": "I'd love to schedule a 30-minute call to discuss your work on the SoMailer hub."
        }
    }
    
    print(f"\n[PHASE 1] Sending signal to Master Controller...")
    try:
        resp = requests.post(N8N_WEBHOOK, json=payload, timeout=60)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"FAILED: {e}")
        return

    print("\n[PHASE 1] Verifying Database Staging...")
    time.sleep(2) # Wait for n8n to process
    
    try:
        drafts_resp = requests.get(f"{API_BASE}/drafts")
        drafts = drafts_resp.json().get('drafts', [])
        test_draft = next((d for d in drafts if d['recipient'] == "tanishq-test@example.com"), None)
        
        if test_draft:
            print("SUCCESS: Draft created in database.")
            print(f"Type: {test_draft['type']}")
            print(f"Tags: {test_draft['tags']}")
            print(f"Content Snapshot: {test_draft['content'][:100]}...")
        else:
            print("FAILURE: No draft found for test sender.")
    except Exception as e:
        print(f"DB CHECK FAILED: {e}")

if __name__ == "__main__":
    test_full_lifecycle()
