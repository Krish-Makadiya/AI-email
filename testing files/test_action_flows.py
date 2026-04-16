import requests
import json

URL = "http://127.0.0.1:8000/process-email"

def test_scheduling():
    payload = {
        "sender_email": "client@example.com",
        "subject": "Meeting Request",
        "content": "Hi Tanishq, can we schedule a 30-minute meeting tomorrow morning to discuss the new milestone?",
        "id": "mock_sched_123"
    }
    print("Sending Scheduling Test...")
    res = requests.post(URL, json=payload)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

def test_urgent():
    payload = {
        "sender_email": "devops@example.com",
        "subject": "CRITICAL: Database failure",
        "content": "The primary database is down and payment processing is failing. Immediate action required.",
        "id": "mock_urgent_124"
    }
    print("\nSending Urgent Fire Test...")
    res = requests.post(URL, json=payload)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    print("--- SoMailer Workflow Tester ---")
    print("1. Test Post Scheduling Workflow")
    print("2. Test Post Urgent Fire Workflow")
    print("3. Run All Tests")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        test_scheduling()
    elif choice == "2":
        test_urgent()
    elif choice == "3":
        test_scheduling()
        test_urgent()
    else:
        print("Invalid choice. Exiting.")
