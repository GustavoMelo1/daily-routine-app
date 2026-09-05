from collections.abc import Iterator
import sqlite3

from app.core.config import get_database_url

def get_database_connection() -> Iterator[sqlite3.Connection]:
    """Open a SQLite connection with foreign key enforcement enabled."""
    connection = sqlite3.connect(get_database_url())
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()
