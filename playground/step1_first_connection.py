"""Step 1 — First connection.  Run: python -m playground.step1_first_connection

PROVIDED: works as soon as db_settings() and get_connection() are written.
"""

from pantry.db import get_connection

conn = get_connection()
try:
    with conn.cursor() as cur:  # a plain cursor: rows are tuples
        cur.execute("SELECT version()")
        print(cur.fetchone()[0])

        cur.execute("SELECT current_database(), current_user")
        dbname, user = cur.fetchone()  # a tuple can be unpacked
        print(f"🔌 Connected to {dbname} as {user}")

        cur.execute("SELECT COUNT(*) FROM foods")
        print(f"🥕 {cur.fetchone()[0]} foods in the pantry")
finally:
    conn.close()  # always, even after an error
    print("🔌 Connection closed")
