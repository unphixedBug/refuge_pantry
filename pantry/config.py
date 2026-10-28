"""Read the database settings from the .env file."""

import os

from dotenv import load_dotenv


def db_settings(dbname: str | None = None) -> dict[str, str]:
    """Return the connection parameters for psycopg2.connect(**settings).

    Keys: host, port, dbname, user, password.
    - host and port have defaults ("localhost", "5432") -> os.getenv(KEY, default)
    - dbname, user and password are mandatory          -> os.environ[KEY] (KeyError if missing)
    - the optional ``dbname`` argument overrides DB_NAME (useful for a test database).
    """
    # TODO(step 1): call load_dotenv(), then build and return the dict.
    raise NotImplementedError("TODO step 1")
