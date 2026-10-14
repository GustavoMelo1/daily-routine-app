"""Versioned SQLite migrations with a backup before changing an existing file."""
import argparse
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_DIRECTORY = Path(__file__).resolve().parent


def execute_sql(connection, sql):
    statement = ""
    for line in sql.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            connection.execute(statement)
            statement = ""
    if statement.strip():
        raise ValueError("SQL incompleto na migração")


def migrate(database_path):
    database_path = Path(database_path).resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    existed = database_path.exists()
    backup_path = None
    connection = sqlite3.connect(database_path)
    try:
        if existed:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup_path = database_path.with_name(f"{database_path.name}.{stamp}.backup")
            backup = sqlite3.connect(backup_path)
            try:
                connection.backup(backup)
            finally:
                backup.close()
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            fresh = not tables
            if fresh:
                execute_sql(connection, (DB_DIRECTORY / "schema.sql").read_text(encoding="utf-8"))
            connection.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, checksum TEXT NOT NULL)")
            for path in sorted((DB_DIRECTORY / "migrations").glob("*.sql")):
                sql = path.read_text(encoding="utf-8")
                checksum = hashlib.sha256(sql.encode()).hexdigest()
                applied = connection.execute("SELECT checksum FROM schema_migrations WHERE version=?", (path.name,)).fetchone()
                if applied:
                    if applied[0] != checksum:
                        raise ValueError(f"Migração já aplicada foi alterada: {path.name}")
                    continue
                columns = {row[1] for row in connection.execute("PRAGMA table_info(image_imports)")}
                adopted = False
                if path.name.startswith("001_") and columns:
                    required = {"id", "image_hash", "status", "error_message", "created_at", "updated_at"}
                    if not required <= columns:
                        raise ValueError("Tabela image_imports incompatível")
                    adopted = True
                if path.name.startswith("002_"):
                    additions = {"attempt_token", "extracted_payload", "publication_digest"}
                    if additions & columns and not additions <= columns:
                        raise ValueError("Migração 002 parcialmente aplicada")
                    adopted = additions <= columns
                if not fresh and not adopted:
                    execute_sql(connection, sql)
                connection.execute("INSERT INTO schema_migrations VALUES (?, ?)", (path.name, checksum))
        return backup_path
    finally:
        connection.close()


def main():
    from dotenv import load_dotenv
    import os
    load_dotenv(DB_DIRECTORY.parent / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=os.getenv("DB_URL", "db/rotina.db"))
    args = parser.parse_args()
    path = Path(args.database)
    if not path.is_absolute():
        path = DB_DIRECTORY.parent / path
    backup = migrate(path)
    print(f"Banco atualizado: {path.resolve()}")
    if backup:
        print(f"Backup preservado: {backup}")


if __name__ == "__main__":
    main()
