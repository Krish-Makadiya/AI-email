import psycopg2
import json

DATABASE_URL = "postgresql://user:password@localhost:5432/email_intelligence"

def seed():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Target distinct email action IDs that are marked as 'Scheduling'
        target_ids = [299, 297, 295]
        
        for action_id in target_ids:
            # Check if a pending draft already exists (due to our new constraint)
            cur.execute("SELECT id FROM draft_replies WHERE email_action_id = %s AND status = 'Pending'", (action_id,))
            if cur.fetchone():
                print(f"Draft for {action_id} already exists. Skipping.")
                continue
                
            # Insert a unique scheduling draft
            slots = ["2026-04-18T10:00:00Z", "2026-04-18T11:00:00Z", "2026-04-19T14:30:00Z"]
            cur.execute("""
                INSERT INTO draft_replies (email_action_id, content, recipient, subject, type, tags, reasoning, status, suggested_slots)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                action_id, 
                f"Hi,\n\nI've reviewed the request (ID {action_id}). Here are some slots that work for me. Please let me know if any of these suit you.\n\nBest regards,\nTanishq",
                f"client_{action_id}@example.com",
                f"Re: Meeting Request (Action {action_id})",
                "Scheduling Proposal",
                ['Scheduling', 'AI-Generated'],
                "Seeded for unique ID verification.",
                'Pending',
                json.dumps(slots)
            ))
            print(f"Seeded unique draft for {action_id}")
            
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    seed()
