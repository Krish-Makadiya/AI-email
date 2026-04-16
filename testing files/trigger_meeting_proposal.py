import requests
import json
import time

# Configuration
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/meeting-logic"
API_BASE = "http://localhost:8000"

def simulate_proposal():
    print("--- Simulating Incoming Scheduling Email ---")
    
    # Fetch a valid email action ID from the database
    try:
        import psycopg2
        conn = psycopg2.connect("postgresql://user:password@localhost:5432/email_intelligence")
        cur = conn.cursor()
        cur.execute("SELECT id FROM email_actions ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            print("No email actions found in the database. Cannot simulate.")
            return
        valid_id = row[0]
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to fetch valid ID: {e}")
        return
        
    print(f"Using valid email_action_id: {valid_id}")

    # 1. Payload simulating a 'Scheduling' classification from the AI Brain
    payload = {
        "action": "propose_times",
        "email_action_id": valid_id,
        "mail": {
            "sender_name": "John Doe",
            "sender_mail": "johndoe@example.com",
            "subject": "Quick chat about the project?",
            "content": "Hi there, I'd love to jump on a call next week to discuss our progress. When are you free?"
        }
    }

    try:
        # 2. Trigger the n8n Master Meeting Controller (Propose Branch)
        print(f"[STEP 1] Sending signal to n8n at: {N8N_WEBHOOK_URL}...")
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        
        if response.status_code == 200:
            print(f"SUCCESS: n8n processed the proposal (Status {response.status_code})")
            print("\nCheck your dashboard at http://localhost:5173 to see the new draft!")
        else:
            print(f"FAILED: n8n returned error {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERROR: Could not connect to the system: {e}")

if __name__ == "__main__":
    simulate_proposal()
