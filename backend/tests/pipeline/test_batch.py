import logging
import pytest
from pipeline import batch


def test_missing_folder(tmp_path):
    with pytest.raises(NotADirectoryError):
        batch.find_image_files(tmp_path / 'missing')


def test_filters_images(tmp_path):
    for name in ('a.JPG', 'b.png', 'notes.md'):
        (tmp_path / name).write_bytes(b'image')
    assert [p.name for p in batch.find_image_files(tmp_path)] == ['a.JPG', 'b.png']


def test_empty_folder_does_not_contact_api(tmp_path, monkeypatch):
    def unexpected():
        pytest.fail('Empty folder must not contact API')
    monkeypatch.setattr(batch.import_client, 'check_import_api', unexpected)
    assert batch.process_folder(tmp_path) == []


def test_continues_after_failure(tmp_path, monkeypatch, caplog):
    for name in ('a.jpg', 'b.jpg', 'c.jpg'):
        (tmp_path / name).write_bytes(b'image')
    visited = []
    def process(path):
        visited.append(path.name)
        if path.name == 'b.jpg':
            raise ValueError('invalid image')
        return 'completed'
    monkeypatch.setattr(batch.import_client, 'check_import_api', lambda: None)
    monkeypatch.setattr(batch, 'process_image', process)
    with caplog.at_level(logging.INFO):
        failures = batch.process_folder(tmp_path)
    assert visited == ['a.jpg', 'b.jpg', 'c.jpg']
    assert len(failures) == 1
    assert failures[0]['error'] == 'invalid image'
    assert any(record.exc_info for record in caplog.records)


def test_preflight_prevents_ocr(tmp_path, monkeypatch):
    (tmp_path / 'a.jpg').write_bytes(b'image')
    def unavailable():
        raise ConnectionError('offline')
    monkeypatch.setattr(batch.import_client, 'check_import_api', unavailable)
    monkeypatch.setattr(batch, 'process_image', lambda _: pytest.fail('OCR must not run'))
    with pytest.raises(ConnectionError):
        batch.process_folder(tmp_path)
