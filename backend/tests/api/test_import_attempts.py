def begin(client):
    record = client.post('/image-imports', json={'image_hash': 'c' * 64}).json()
    token = client.post(f"/image-imports/{record['id']}/start").json()['attempt_token']
    return f"/image-imports/{record['id']}", {'X-Import-Token': token}


def payload():
    return {'days': [{'data': '2026-10-01', 'minutos_estudados': 60,
                     'frase_do_dia': '', 'autor_frase': '', 'tipo': 'normal',
                     'tarefas': [{'descricao': 'SQL', 'cumprida': 1}]}]}


def test_publish_is_idempotent_and_requires_owner(client):
    path, headers = begin(client)
    assert client.post(path + '/publish', json=payload(), headers={'X-Import-Token': 'wrong'}).status_code == 409
    assert client.get('/dias/2026-10-01').status_code == 404
    for _ in range(2):
        assert client.post(path + '/publish', json=payload(), headers=headers).status_code == 200
    assert len(client.get('/dias/2026-10-01').json()['tarefas']) == 1


def test_retry_preserves_checkpoint_and_invalidates_old_owner(client):
    path, old = begin(client)
    assert client.put(path + '/payload', json=payload(), headers=old).status_code == 200
    assert client.post(path + '/retry').status_code == 409
    assert client.post(path + '/fail', json={'error_message': 'offline'}, headers=old).status_code == 200
    assert client.post(path + '/retry').status_code == 200
    token = client.post(path + '/start').json()['attempt_token']
    assert token != old['X-Import-Token']
    assert client.get(path + '/payload').json()['payload']['days'] == payload()['days']
    assert client.post(path + '/publish', json=payload(), headers=old).status_code == 409
    assert client.post(path + '/publish', json=payload(), headers={'X-Import-Token': token}).status_code == 200


def test_conflict_rolls_back_entire_publication(client):
    path, headers = begin(client)
    data = payload()
    data['days'].append(data['days'][0].copy())
    assert client.post(path + '/publish', json=data, headers=headers).status_code == 409
    assert client.get('/dias/2026-10-01').status_code == 404


def test_abandoned_attempt_can_be_reclaimed(client):
    from app.main import app
    from app.database.connection import get_database_connection
    path, old = begin(client)
    connections = app.dependency_overrides[get_database_connection]()
    connection = next(connections)
    try:
        connection.execute("UPDATE image_imports SET updated_at=datetime('now','-2 hours')")
        connection.commit()
    finally:
        connections.close()
    assert client.post(path + '/retry').status_code == 200
    token = client.post(path + '/start').json()['attempt_token']
    assert token != old['X-Import-Token']
    assert client.post(path + '/fail', headers=old, json={'error_message': 'late'}).status_code == 409
