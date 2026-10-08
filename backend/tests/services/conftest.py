import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def database_connection(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        yield connection
    finally:
        connection.close()