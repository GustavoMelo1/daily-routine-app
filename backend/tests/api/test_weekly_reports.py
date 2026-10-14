import pytest
from app.main import app
from app.schemas.weekly_report import WeeklyProgress
from app.services.weekly_comparison import get_comparison_generator, ComparisonUnavailable


def report(date='2026-10-04', content='Estudei SELECT.'):
    return {'report_date': date, 'title': 'Semana de estudos', 'filename': date + '.md', 'content': content}


@pytest.fixture
def generator():
    calls = []
    def generate(previous, current):
        calls.append((previous, current))
        return WeeklyProgress(summary='O relato agora menciona JOIN.', advances=[{
            'title': 'Consultas SQL', 'explanation': 'Novas consultas foram documentadas.',
            'previous_evidence': previous, 'current_evidence': current,
        }], consolidations=[], pending=[], limitations='Relatos não comprovam domínio.'), 'test-model'
    app.dependency_overrides[get_comparison_generator] = lambda: generate
    yield calls
    app.dependency_overrides.pop(get_comparison_generator, None)


def test_report_crud_and_version_conflict(client):
    created = client.post('/weekly-reports', json=report())
    assert created.status_code == 201
    saved = created.json()
    assert saved['content'] == 'Estudei SELECT.'
    assert client.post('/weekly-reports', json=report()).status_code == 409
    assert 'content' not in client.get('/weekly-reports').json()[0]
    update = {**report(), 'content': 'Corrigido', 'version': 1}
    path = f"/weekly-reports/{saved['id']}"
    assert client.put(path, json=update).json()['version'] == 2
    assert client.put(path, json=update).status_code == 409
    assert client.get(path).json()['content'] == 'Corrigido'
    assert client.delete(path).status_code == 204
    assert client.get(path).status_code == 404


@pytest.mark.parametrize('changes', [
    {'content': ' '}, {'content': 'x' * 100001}, {'filename': '../report.md'},
    {'filename': 'image.png'}, {'report_date': '2026-99-99'}, {'title': ''},
])
def test_rejects_invalid_reports(client, changes):
    assert client.post('/weekly-reports', json={**report(), **changes}).status_code == 422


def test_comparison_cached_and_invalidated_on_edit(client, generator):
    previous = client.post('/weekly-reports', json=report()).json()
    current = client.post('/weekly-reports', json=report('2026-10-11', 'Pratiquei JOIN.')).json()
    path = f"/weekly-reports/{current['id']}"
    assert client.get(path + '/comparison').json() is None
    for _ in range(2):
        response = client.post(path + '/compare', json={})
        assert response.status_code == 200
        assert response.json()['previous_report_id'] == previous['id']
    assert len(generator) == 1
    assert client.get(path + '/comparison').json()['model'] == 'test-model'
    client.put(path, json={**report('2026-10-11', 'Pratiquei JOIN e GROUP BY.'), 'version': 1})
    assert client.get(path + '/comparison').json() is None
    assert client.post(path + '/compare', json={}).status_code == 200
    assert len(generator) == 2
    client.delete(f"/weekly-reports/{previous['id']}")
    assert client.get(path + '/comparison').status_code == 422


def test_first_report_and_future_comparison_rejected(client, generator):
    first = client.post('/weekly-reports', json=report()).json()
    path = f"/weekly-reports/{first['id']}/compare"
    assert client.post(path, json={}).status_code == 422
    assert client.post(path, json={'previous_report_id': first['id']}).status_code == 422
    assert generator == []


def test_provider_failure_does_not_erase_reports(client, generator):
    client.post('/weekly-reports', json=report())
    current = client.post('/weekly-reports', json=report('2026-10-11')).json()
    def unavailable(*args):
        raise ComparisonUnavailable('Serviço indisponível')
    app.dependency_overrides[get_comparison_generator] = lambda: unavailable
    path = f"/weekly-reports/{current['id']}"
    assert client.post(path + '/compare', json={}).status_code == 502
    assert client.get(path + '/comparison').json() is None
    assert len(client.get('/weekly-reports').json()) == 2


def test_invented_evidence_is_not_saved(client, generator):
    client.post('/weekly-reports', json=report())
    current = client.post('/weekly-reports', json=report('2026-10-11')).json()
    def invented(*args):
        return WeeklyProgress(summary='Inventado', advances=[{
            'title': 'Erro', 'explanation': 'Erro', 'current_evidence': 'Não existe no texto',
        }], consolidations=[], pending=[], limitations='Teste'), 'test'
    app.dependency_overrides[get_comparison_generator] = lambda: invented
    path = f"/weekly-reports/{current['id']}"
    assert client.post(path + '/compare', json={}).status_code == 502
    assert client.get(path + '/comparison').json() is None


def test_report_changed_during_generation_is_not_saved(client, generator):
    client.post('/weekly-reports', json=report())
    current = client.post('/weekly-reports', json=report('2026-10-11')).json()
    path = f"/weekly-reports/{current['id']}"
    original_generator = app.dependency_overrides[get_comparison_generator]()
    def changed(previous, content):
        assert client.put(path, json={**report('2026-10-11', 'Texto corrigido'), 'version': 1}).status_code == 200
        return original_generator(previous, content)
    app.dependency_overrides[get_comparison_generator] = lambda: changed
    assert client.post(path + '/compare', json={}).status_code == 409
    assert client.get(path + '/comparison').json() is None
    assert client.get(path).json()['content'] == 'Texto corrigido'
