import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def deployment():
    path = Path(__file__).resolve().parents[3] / 'deploy/start.py'
    spec = importlib.util.spec_from_file_location('deployment_start', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_deployment_migrates_before_starting_server(deployment, tmp_path, monkeypatch):
    database = tmp_path / 'routine.db'
    monkeypatch.setenv('DB_URL', str(database))
    launches = []
    def launch(command, args):
        assert database.is_file()
        launches.append(args)
    monkeypatch.setattr(deployment.os, 'execvp', launch)
    deployment.main()
    assert launches[0][launches[0].index('--workers') + 1] == '1'
    assert '--reload' not in launches[0]


def test_failed_migration_does_not_start_api(deployment, tmp_path, monkeypatch):
    monkeypatch.setenv('DB_URL', str(tmp_path / 'routine.db'))
    monkeypatch.setattr(deployment, 'migrate', Mock(side_effect=RuntimeError('migration failed')))
    launch = Mock()
    monkeypatch.setattr(deployment.os, 'execvp', launch)
    with pytest.raises(RuntimeError, match='migration failed'):
        deployment.main()
    launch.assert_not_called()


def test_deployment_rejects_relative_database_path(deployment, monkeypatch):
    monkeypatch.setenv('DB_URL', 'db/rotina.db')
    with pytest.raises(ValueError, match='absoluto'):
        deployment.main()
