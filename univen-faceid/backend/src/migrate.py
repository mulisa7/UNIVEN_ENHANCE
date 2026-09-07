import os
import sys
import time

import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://faceid:faceid@localhost:5433/faceid"
)
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "migrations")


def _connect_with_retry(attempts=10, delay=2):
    """Postgres in a freshly-started container isn't always ready to accept
    connections the instant it's up, so retry briefly instead of failing
    the first time this runs right after `docker compose up`."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return psycopg2.connect(DATABASE_URL)
        except psycopg2.OperationalError as e:
            last_error = e
            print(f"Database not ready yet (attempt {attempt}/{attempts}): {e}")
            time.sleep(delay)
    raise last_error


def migrate():
    files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql"))
    conn = _connect_with_retry()
    try:
        with conn.cursor() as cur:
            for filename in files:
                path = os.path.join(MIGRATIONS_DIR, filename)
                print(f"Running migration: {path}")
                with open(path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
        conn.commit()
        print("Migration complete")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
