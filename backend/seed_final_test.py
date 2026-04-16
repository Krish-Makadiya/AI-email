import psycopg2
import json

DATABASE_URL = "postgresql://user:password@localhost:5432/email_intelligence"

def seed():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. Create a brand new email action
    cur.execute("""
        INSERT INTO email_actions (payload, scheduling_status) 
        VALUES (%s, 'New') RETURNING id
    """, (json.dumps({
        'sender_email': 'brand_new_client@example.com', 
        'subject': 'Brand New Test Meeting', 
        'classification': 'Scheduling'
    }),))
    new_id = cur.fetchone()[0]
    
    # 2. Create the pending draft for it
    cur.execute("""
        INSERT INTO draft_replies (email_action_id, content, recipient, subject, type, tags, status, suggested_slots) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        new_id, 
        'Let\'s meet soon!', 
        'brand_new_client@example.com', 
        'Brand New Test Meeting', 
        'Scheduling Proposal', 
        ['Scheduling'], 
        'Pending', 
        json.dumps(['2026-04-25T10:00:00Z', '2026-04-26T10:00:00Z'])
    ))
    
    conn.commit()
    print(f"Seeded brand new email action AND draft with ID {new_id}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()
