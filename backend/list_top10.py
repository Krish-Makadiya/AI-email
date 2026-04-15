import psycopg2, json, os
conn = psycopg2.connect(os.getenv('DATABASE_URL','postgresql://user:password@localhost:5432/email_intelligence'))
cursor = conn.cursor()
cursor.execute("SELECT id, created_at, email_received_at, payload FROM email_actions ORDER BY COALESCE(email_received_at, created_at) DESC LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    id_, created_at, email_received_at, payload = row
    if isinstance(payload, str):
        payload = json.loads(payload)
    subject = payload.get('subject')
    received_field = payload.get('received_at')
    print(f"ID:{id_} created_at:{created_at} email_received_at:{email_received_at} payload.received_at:{received_field} subject:{subject}")
cursor.close()
conn.close()
