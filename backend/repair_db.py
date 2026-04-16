import psycopg2
try:
    c = psycopg2.connect('postgresql://user:password@localhost:5432/email_intelligence')
    cur = c.cursor()
    # Repair any 'Confirmed' items that have NULL time, so they show up in lifecycle hub
    cur.execute("UPDATE email_actions SET scheduled_time = '2026-04-20 10:00:00' WHERE scheduling_status = 'Confirmed' AND scheduled_time IS NULL")
    c.commit()
    print("REPAIRED_ROWS:", cur.rowcount)
    c.close()
except Exception as e:
    print(f"ERROR: {e}")
