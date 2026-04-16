import psycopg2
from psycopg2.extras import RealDictCursor
try:
    c = psycopg2.connect('postgresql://user:password@localhost:5432/email_intelligence')
    cur = c.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, scheduling_status, scheduled_time FROM email_actions WHERE scheduling_status = 'Confirmed'")
    rows = cur.fetchall()
    print(f"CONFIRMED_COUNT: {len(rows)}")
    for r in rows:
        print(r)
    c.close()
except Exception as e:
    print(f"ERROR: {e}")
