import sqlite3
from pathlib import Path

from app.repositories.image_import import find_image_import_by_hash, insert_image_import, start_image_import, fail_image_import


def test_insert_image_import_returns_id_and_starts_pending(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))

        import_id = insert_image_import(connection, "a" * 64)
        row = connection.execute(
            "SELECT id, image_hash, status, error_message FROM image_imports"
        ).fetchone()

        assert isinstance(import_id, int)
        assert row == (import_id, "a" * 64, "pending", None)
        assert connection.in_transaction
        connection.rollback()
        assert connection.execute("SELECT COUNT(*) FROM image_imports").fetchone() == (0,)
    finally:
        connection.close()


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

def test_start_image_import_only_starts_once(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        import_id = insert_image_import(connection, "a" * 64)

        first_attempt = start_image_import(connection, import_id)
        second_attempt = start_image_import(connection, import_id)
        row = find_image_import_by_hash(connection, "a" * 64)

        assert first_attempt == 1
        assert second_attempt == 0
        assert row[2] == "processing"
    finally:
        connection.close()

def test_fail_image_import_records_error(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        import_id = insert_image_import(connection, "a" * 64)
        start_image_import(connection, import_id)

        affected_rows = fail_image_import(
            connection, import_id, "Falha no OCR"
        )
        row = find_image_import_by_hash(connection, "a" * 64)

        assert affected_rows == 1
        assert row[2] == "failed"
        assert row[3] == "Falha no OCR"
    finally:
        connection.close()

def test_fail_image_import_does_not_change_pending_import(tmp_path):
    schema_path = Path(__file__).resolve().parents[2] / "db/schema.sql"
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        import_id = insert_image_import(connection, "a" * 64)

        affected_rows = fail_image_import(connection, import_id, "Falha no OCR")
        row = find_image_import_by_hash(connection, "a" * 64)

        assert affected_rows == 0
        assert row[2] == "pending"
        assert row[3] is None
    finally:
        connection.close()
