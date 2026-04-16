import psycopg2
from psycopg2.extras import RealDictCursor
c = psycopg2.connect('postgresql://user:password@localhost:5432/email_intelligence')
cur = c.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT id, payload->>'sender_email' as sender, payload->>'subject' as subject, scheduling_status, google_event_id FROM email_actions WHERE scheduling_status != 'New' ORDER BY COALESCE(scheduled_time, '3000-01-01') ASC")
print(cur.fetchall())
c.close()
