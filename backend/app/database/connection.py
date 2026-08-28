import sqlite3

from app.core.config import get_database_url


def get_database_connection() -> sqlite3.Connection:
    """Open a SQLite connection with foreign key enforcement enabled."""
    connection = sqlite3.connect(get_database_url())
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
