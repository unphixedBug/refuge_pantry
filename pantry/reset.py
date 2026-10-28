"""Reset the pantry database: python -m pantry.reset (PROVIDED, works once step 1 is done)."""

from pantry.db import get_connection, reset_database


def main() -> None:
    """Reload schema.sql and seed.sql."""
    conn = get_connection()
    try:
        reset_database(conn)
        print("🧹 Pantry reset: 8 foods, 6 feedings.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
