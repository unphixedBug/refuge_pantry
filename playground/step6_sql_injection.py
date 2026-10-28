"""Step 6 — Why %s matters.  Run: python -m playground.step6_sql_injection

PROVIDED demo: read it, run it, explain the difference in your notes.
"""

from psycopg2.extras import RealDictCursor

from pantry.db import get_connection


def search_unsafe(conn, name: str) -> list[str]:
    """❌ NEVER do this: the value is pasted INTO the SQL text."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT name FROM foods WHERE name = '{name}'")
        return [row["name"] for row in cur.fetchall()]


def search_safe(conn, name: str) -> list[str]:
    """✅ The value travels separately from the SQL text."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT name FROM foods WHERE name = %s", (name,))
        return [row["name"] for row in cur.fetchall()]


conn = get_connection()
try:
    evil = "x' OR '1'='1"
    print("unsafe ->", search_unsafe(conn, evil))  # every food leaks out
    print("safe   ->", search_safe(conn, evil))    # nothing: no food has that name
    print("safe   ->", search_safe(conn, "Moon Clover"))

    with conn.cursor() as cur:  # what psycopg2 actually sends for the safe version
        print(cur.mogrify("SELECT name FROM foods WHERE name = %s", (evil,)).decode())
finally:
    conn.close()
