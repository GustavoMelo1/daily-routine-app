import sqlite3
from pathlib import Path

from app.repositories.image_import import find_image_import_by_hash


def test_find_image_import_returns_none_when_missing(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))

        result = find_image_import_by_hash(connection, "a" * 64)

        assert result is None
    finally:
        connection.close()

def test_find_image_import_returns_matching_record(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO image_imports (image_hash) VALUES (?)",
            ("a" * 64,),
        )
        cursor = connection.execute(
            "INSERT INTO image_imports (image_hash) VALUES (?)",
            ("b" * 64,),
        )
        expected_id = cursor.lastrowid

        result = find_image_import_by_hash(connection, "b" * 64)

        assert result == (expected_id, "b" * 64, "pending", None)
    finally:
        connection.close()