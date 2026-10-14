import sqlite3
from pathlib import Path
from db.migrate import migrate


def test_migrates_legacy_database_with_backup(tmp_path):
    path = tmp_path / 'legacy.db'
    schema = (Path(__file__).parents[2] / 'db/schema.sql').read_text(encoding='utf-8')
    with sqlite3.connect(path) as connection:
        legacy_schema = 'CREATE TABLE dias' + schema.split('CREATE TABLE dias', 1)[1].split('CREATE TABLE image_imports')[0]
        connection.executescript(legacy_schema)
        connection.execute("INSERT INTO dias(data,minutos_estudados) VALUES ('2026-01-01',60)")
    backup = migrate(path)
    assert backup.exists()
    for database in (path, backup):
        with sqlite3.connect(database) as connection:
            assert connection.execute('SELECT minutos_estudados FROM dias').fetchone() == (60,)
    migrate(path)
    with sqlite3.connect(path) as connection:
        assert 'attempt_token' in {row[1] for row in connection.execute('PRAGMA table_info(image_imports)')}


def test_initializes_empty_database(tmp_path):
    path = tmp_path / 'new.db'
    assert migrate(path) is None
    with sqlite3.connect(path) as connection:
        assert connection.execute('SELECT count(*) FROM image_imports').fetchone() == (0,)
