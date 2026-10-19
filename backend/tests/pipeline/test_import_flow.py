import json
from pathlib import Path
import pytest
import requests
from pipeline import batch, import_client
from pipeline.tracking import calculate_image_hash


@pytest.fixture
def import_environment(client, monkeypatch, tmp_path):
    def request(method, url, **kwargs):
        assert kwargs.pop('timeout') == (5, 60)
        response = client.request(method, '/image-imports' + url.split('/image-imports', 1)[1], **kwargs)
        wrapped = requests.Response()
        wrapped.status_code = response.status_code
        wrapped._content = response.content
        wrapped.url = url
        return wrapped
    monkeypatch.setattr(import_client.requests, 'request', request)
    calls = []
    def extract(path):
        calls.append(path)
        return json.loads((Path(__file__).parents[1] / 'fixtures/ocr_result.json').read_text(encoding='utf-8'))
    monkeypatch.setattr(batch, 'extract', extract)
    image = tmp_path / 'sample.jpg'
    image.write_bytes(b'fictional image')
    return image, calls


def test_complete_import_is_not_repeated(import_environment, client):
    image, calls = import_environment
    assert batch.process_image(image) == 'completed'
    assert batch.process_image(image) == 'already_completed'
    assert len(calls) == 1
    assert client.get('/dias/2026-08-25').status_code == 200


def test_publication_retry_reuses_saved_ocr(import_environment, monkeypatch):
    image, calls = import_environment
    publish = import_client.publish_import
    def offline(*args):
        raise requests.ConnectionError('offline')
    monkeypatch.setattr(import_client, 'publish_import', offline)
    with pytest.raises(requests.ConnectionError):
        batch.process_image(image)
    monkeypatch.setattr(import_client, 'publish_import', publish)
    assert batch.process_image(image) == 'completed'
    assert len(calls) == 1


def test_lost_success_response_is_reconciled(import_environment, monkeypatch):
    image, calls = import_environment
    publish = import_client.publish_import
    def lost_response(*args):
        publish(*args)
        raise requests.Timeout('response lost')
    monkeypatch.setattr(import_client, 'publish_import', lost_response)
    assert batch.process_image(image) == 'completed'
    assert len(calls) == 1


def test_active_import_is_not_taken_over(import_environment):
    image, calls = import_environment
    record = import_client.get_or_create_import(calculate_image_hash(image))
    import_client.start_import(record['id'])
    assert batch.process_image(image) == 'busy'
    assert calls == []


def test_ocr_failure_can_be_retried(import_environment, monkeypatch):
    image, calls = import_environment
    extract = batch.extract
    def broken(_):
        raise ValueError('unreadable response')
    monkeypatch.setattr(batch, 'extract', broken)
    with pytest.raises(ValueError):
        batch.process_image(image)
    record = import_client.get_or_create_import(calculate_image_hash(image))
    assert record['status'] == 'failed'
    monkeypatch.setattr(batch, 'extract', extract)
    assert batch.process_image(image) == 'completed'
    assert len(calls) == 1


def test_existing_day_is_not_overwritten(import_environment, client):
    image, calls = import_environment
    original = {'data': '2026-08-25', 'minutos_estudados': 15,
                'frase_do_dia': 'original', 'autor_frase': '', 'tipo': 'normal'}
    assert client.post('/dias', json=original).status_code == 201
    with pytest.raises(requests.HTTPError):
        batch.process_image(image)
    saved = client.get('/dias/2026-08-25').json()
    assert saved['minutos_estudados'] == 15
    assert saved['tarefas'] == []


def test_photo_with_past_week_keeps_each_days_date(import_environment, client, monkeypatch):
    image, _ = import_environment
    days = [{'data': f'{day:02d}/10/2020', 'minutos_estudados': day,
             'itens': [{'texto': f'Exercício específico {day}', 'status': 'feito'}]}
            for day in range(12, 19)]
    monkeypatch.setattr(batch, 'extract', lambda _: {'dias': days})
    assert batch.process_image(image) == 'completed'
    for day in range(12, 19):
        saved = client.get(f'/dias/2020-10-{day}').json()
        assert saved['data'] == f'2020-10-{day}'
        assert saved['minutos_estudados'] == day
        assert saved['tarefas'][0]['descricao'] == f'Exercício específico {day}'
    assert batch.process_image(image) == 'already_completed'
