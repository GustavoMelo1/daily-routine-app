import os

from dotenv import load_dotenv


load_dotenv()


def get_database_url() -> str:
    """Return the configured database URL."""
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise RuntimeError("DB_URL not configured")
    return db_url
