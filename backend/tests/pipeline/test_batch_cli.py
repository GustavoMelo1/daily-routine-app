import logging
import pytest
from pipeline import batch


@pytest.mark.parametrize('failures, expected', [([], 0), ([{'error': 'failure'}], 1)])
def test_exit_code_and_log_file(tmp_path, monkeypatch, failures, expected):
    monkeypatch.setattr(batch, 'process_folder', lambda _: failures)
    # Keep pytest's capture handlers intact while exercising the real file handler.
    root = logging.getLogger()
    previous_handlers, previous_level = root.handlers[:], root.level
    root.handlers = []
    path = tmp_path / 'batch.log'
    try:
        assert batch.main(['--folder', str(tmp_path), '--log-file', str(path)]) == expected
        for handler in root.handlers:
            handler.flush()
        assert 'Lote encerrado' in path.read_text(encoding='utf-8')
    finally:
        for handler in root.handlers:
            handler.close()
        root.handlers = previous_handlers
        root.setLevel(previous_level)
