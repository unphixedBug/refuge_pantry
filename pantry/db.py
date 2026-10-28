"""Opening a connection, and resetting the pantry database."""

from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as Connection

from pantry.config import db_settings

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def get_connection() -> Connection:
    """Open and return a new connection to the pantry database.

    The caller is responsible for closing it (try / finally, see the playground).
    """
    # TODO(step 1): use db_settings() and psycopg2.connect(...). One line is enough.
    raise NotImplementedError("TODO step 1")


def reset_database(conn: Connection) -> None:
    """Drop and recreate the tables, then load the reference dataset (PROVIDED).

    Ids restart at 1, so your results match the expected ones.
    """
    with conn:  # commit on success, rollback on error
        with conn.cursor() as cur:
            cur.execute((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
            cur.execute((SQL_DIR / "seed.sql").read_text(encoding="utf-8"))
