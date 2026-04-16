import psycopg2
conn = psycopg2.connect('postgresql://user:password@localhost:5432/email_intelligence')
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'email_actions' AND column_name IN ('email_received_at', 'created_at')")
print(cur.fetchall())
conn.close()
