import psycopg2
conn = psycopg2.connect('postgresql://user:password@localhost:5432/email_intelligence')
cur = conn.cursor()
cur.execute("SELECT data_type FROM information_schema.columns WHERE table_name = 'email_actions' AND column_name = 'payload'")
print(cur.fetchone()[0])
conn.close()
