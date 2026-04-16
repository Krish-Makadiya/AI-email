import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = "postgresql://user:password@localhost:5432/email_intelligence"

def trace_fetch():
    print("--- TRACING DATABASE FETCH ---")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check raw row count
        cursor.execute("SELECT COUNT(*) as count FROM email_actions")
        count = cursor.fetchone()['count']
        print(f"Total Rows in email_actions: {count}")
        
        # 2. Fetch the last 5 rows to analyze them
        cursor.execute("SELECT * FROM email_actions ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows for analysis.")
        
        for i, row in enumerate(rows):
            print(f"\n[Row {i+1}] ID: {row['id']}")
            p = row['payload']
            print(f"Payload Type: {type(p)}")
            
            # 3. Simulate the formatting logic from main.py
            try:
                formatted = {
                    "id": row['id'],
                    "sender_email": p.get('sender_email', 'unknown'),
                    "subject": p.get('subject', 'no subject'),
                    "classification": p.get('classification', 'FYI_Read')
                }
                print(f"Successfully formatted: {formatted['sender_email']} | {formatted['classification']}")
            except Exception as fe:
                print(f"!!! FORMATTING ERROR on Row {row['id']}: {fe}")
                print(f"Full Payload: {json.dumps(p)[:200]}...")

        conn.close()
    except Exception as e:
        print(f"CRITICAL TRACE ERROR: {e}")

if __name__ == "__main__":
    trace_fetch()
