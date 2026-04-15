import psycopg2
import json
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/email_intelligence'))
cursor = conn.cursor()
cursor.execute('SELECT id, payload, email_received_at, created_at FROM email_actions ORDER BY id DESC LIMIT 1')
row = cursor.fetchone()

if row:
    print(f"Email ID: {row[0]}")
    print(f"email_received_at: {row[2]}")
    print(f"created_at: {row[3]}")
    print(f"\nPayload content:")
    payload = json.loads(row[1]) if isinstance(row[1], str) else row[1]
    print(json.dumps(payload, indent=2))
else:
    print("No emails found")

cursor.close()
conn.close()
