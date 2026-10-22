import os
from pathlib import Path
from dotenv import load_dotenv


BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIRECTORY / '.env')

def get_database_url() -> str:
    """Return the configured database URL."""
    db_url = os.getenv("DB_URL", '').strip()
    if not db_url:
        raise RuntimeError("DB_URL not configured")
    path = Path(db_url)
    if not path.is_absolute():
        path = BACKEND_DIRECTORY / path
    return str(path.resolve())
