from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest

from app.database.connection import get_database_connection


def test_connection_can_be_used_and_closed_on_another_thread(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_URL', str(tmp_path / 'threads.db'))
    dependency = get_database_connection()
    connection = next(dependency)
    try:
        with ThreadPoolExecutor(max_workers=1) as worker:
            def query():
                assert connection.execute('PRAGMA foreign_keys').fetchone() == (1,)
                return connection.execute('SELECT 1').fetchone()

            assert worker.submit(query).result() == (1,)
            worker.submit(dependency.close).result()
        with pytest.raises(sqlite3.ProgrammingError, match='closed'):
            connection.execute('SELECT 1')
    finally:
        dependency.close()


def test_each_request_gets_its_own_connection(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_URL', str(tmp_path / 'requests.db'))
    first = get_database_connection()
    second = get_database_connection()
    try:
        first_connection = next(first)
        second_connection = next(second)
        assert first_connection is not second_connection
        first.close()
        assert second_connection.execute('SELECT 1').fetchone() == (1,)
    finally:
        first.close()
        second.close()
