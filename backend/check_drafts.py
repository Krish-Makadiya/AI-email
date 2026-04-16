import psycopg2
from psycopg2.extras import RealDictCursor
try:
    c = psycopg2.connect('postgresql://user:password@localhost:5432/email_intelligence')
    cur = c.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, email_action_id, content FROM draft_replies WHERE content ILIKE '%confirm%'")
    rows = cur.fetchall()
    print(f"CONFIRM_DRAFT_COUNT: {len(rows)}")
    for r in rows:
        print(r)
    c.close()
except Exception as e:
    print(f"ERROR: {e}")
