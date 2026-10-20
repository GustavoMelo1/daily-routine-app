import pytest


def test_plan_future_day_then_complete_task_and_record_minutes(client):
    response = client.post('/dias/planejamento', json={'data': '2099-10-20', 'tarefas': ['Python', ' SQL ']})
    assert response.status_code == 201
    day = client.get('/dias/2099-10-20').json()
    assert day['minutos_estudados'] == 0
    assert [task['descricao'] for task in day['tarefas']] == ['Python', 'SQL']
    assert all(task['cumprida'] == 0 for task in day['tarefas'])
    assert client.patch(f"/tarefas/{day['tarefas'][0]['id']}", json={'cumprida': 1}).status_code == 200
    assert client.patch('/dias/2099-10-20/minutos', json={'minutos_estudados': 60}).status_code == 200
    updated = client.get('/dias/2099-10-20').json()
    assert updated['minutos_estudados'] == 60
    assert [task['cumprida'] for task in updated['tarefas']] == [1, 0]


def test_duplicate_plan_does_not_add_tasks(client):
    plan = {'data': '2099-10-20', 'tarefas': ['SQL']}
    assert client.post('/dias/planejamento', json=plan).status_code == 201
    assert client.post('/dias/planejamento', json=plan).status_code == 409
    assert len(client.get('/dias/2099-10-20').json()['tarefas']) == 1


@pytest.mark.parametrize('changes', [{'data': '2026-99-99'}, {'tarefas': [' ']}, {'tarefas': ['x' * 501]}, {'minutos_estudados': -1}])
def test_invalid_plan_does_not_create_day(client, changes):
    assert client.post('/dias/planejamento', json={'data': '2099-10-20', **changes}).status_code == 422
    assert client.get('/dias/2099-10-20').status_code == 404


def test_plan_rolls_back_when_task_insert_fails(client, monkeypatch):
    import sqlite3
    from app.services import day_plan
    insert = day_plan.insert_task
    def fail_second(connection, day_id, description, completed):
        if description == 'falha':
            raise sqlite3.IntegrityError('simulated failure')
        return insert(connection, day_id, description, completed)
    monkeypatch.setattr(day_plan, 'insert_task', fail_second)
    assert client.post('/dias/planejamento', json={'data': '2099-10-20', 'tarefas': ['SQL', 'falha']}).status_code == 409
    assert client.get('/dias/2099-10-20').status_code == 404


def test_minutes_validation(client):
    assert client.patch('/dias/2099-10-20/minutos', json={'minutos_estudados': 10}).status_code == 404
    assert client.patch('/dias/2099-10-20/minutos', json={'minutos_estudados': 1500}).status_code == 422
