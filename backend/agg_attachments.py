import psycopg2, os
conn=psycopg2.connect(os.getenv('DATABASE_URL','postgresql://user:password@localhost:5432/email_intelligence'))
cur=conn.cursor()
cur.execute("SELECT (payload->>'attachment_analysis') AS attachment_analysis, COUNT(*) FROM email_actions GROUP BY attachment_analysis ORDER BY COUNT(*) DESC LIMIT 20")
rows=cur.fetchall()
print('Top attachment_analysis values and counts:')
for r in rows:
    print(r)
cur.close()
conn.close()
