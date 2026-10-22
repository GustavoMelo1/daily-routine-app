import pytest

from app.core.config import BACKEND_DIRECTORY, get_database_url


def test_relative_database_path_does_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('DB_URL', 'db/rotina.db')
    assert get_database_url() == str((BACKEND_DIRECTORY / 'db/rotina.db').resolve())


def test_absolute_database_path_is_preserved(tmp_path, monkeypatch):
    path = tmp_path / 'routine.db'
    monkeypatch.setenv('DB_URL', str(path))
    assert get_database_url() == str(path.resolve())


@pytest.mark.parametrize('value', ['', '   '])
def test_database_configuration_is_required(monkeypatch, value):
    monkeypatch.setenv('DB_URL', value)
    with pytest.raises(RuntimeError, match='DB_URL'):
        get_database_url()
