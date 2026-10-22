import sqlite3

import pytest

from db.backup import create_backup


def test_backup_is_readable_and_does_not_replace_previous_backup(tmp_path):
    source = tmp_path / 'routine.db'
    connection = sqlite3.connect(source)
    try:
        connection.execute('CREATE TABLE entries (title TEXT)')
        connection.execute('INSERT INTO entries VALUES (?)', ('Estudar SQL',))
        connection.commit()
        first = create_backup(source, tmp_path / 'backups')
        second = create_backup(source, tmp_path / 'backups')
        assert first != second
        assert first.is_file()
        restored = sqlite3.connect(second)
        try:
            assert restored.execute('SELECT title FROM entries').fetchall() == [('Estudar SQL',)]
            assert restored.execute('PRAGMA integrity_check').fetchone() == ('ok',)
        finally:
            restored.close()
    finally:
        connection.close()


def test_backup_does_not_create_a_missing_source(tmp_path):
    source = tmp_path / 'missing.db'
    with pytest.raises(FileNotFoundError):
        create_backup(source, tmp_path / 'backups')
    assert not source.exists()
