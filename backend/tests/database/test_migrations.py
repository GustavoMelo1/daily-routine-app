import sqlite3
import pytest
from pathlib import Path

def test_image_import_starts_pending(tmp_path):
    migration_path = (
        Path(__file__).resolve().parents[2]
        / "db/migrations/001_create_image_imports.sql"
    )
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(migration_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO image_imports (image_hash) VALUES (?)",
            ("a" * 64,),
        )
        row = connection.execute(
            "SELECT status, error_message FROM image_imports"
        ).fetchone()

        assert row == ("pending", None)
    finally:
        connection.close()

def test_image_import_rejects_duplicate_hash(tmp_path):
    migration_path = (
        Path(__file__).resolve().parents[2]
        / "db/migrations/001_create_image_imports.sql"
    )
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(migration_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO image_imports (image_hash) VALUES (?)",
            ("a" * 64,),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO image_imports (image_hash) VALUES (?)",
                ("a" * 64,),
            )
    finally:
        connection.close()

def test_image_import_rejects_invalid_status(tmp_path):
    migration_path = (
        Path(__file__).resolve().parents[2]
        / "db/migrations/001_create_image_imports.sql"
    )
    connection = sqlite3.connect(tmp_path / "test.db")

    try:
        connection.executescript(migration_path.read_text(encoding="utf-8"))

        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            connection.execute(
                "INSERT INTO image_imports (image_hash, status) VALUES (?, ?)",
                ("a" * 64, "banana"),
            )
    finally:
        connection.close()