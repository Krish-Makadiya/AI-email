import psycopg2
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/email_intelligence'))
cursor = conn.cursor()
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position", ('email_actions',))
cols = cursor.fetchall()
print("Columns in email_actions table:")
for col in cols:
    print(f"  - {col[0]}")
cursor.close()
conn.close()
