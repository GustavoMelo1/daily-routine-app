import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database.connection import get_database_connection
from app.main import app

@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "teste.db"
    schema_path = (
        Path(__file__).parent.parent / "db" / "schema.sql"
    )

    setup_connection = sqlite3.connect(database_path)
    schema = schema_path.read_text(encoding="utf-8")
    setup_connection.executescript(schema)
    setup_connection.close()

    def database_connection():
        connection = sqlite3.connect(database_path, check_same_thread=False)
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    app.dependency_overrides[get_database_connection] = database_connection

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_database_connection, None)
