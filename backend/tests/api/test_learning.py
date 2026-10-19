import pytest


def create(client, title, parent_id=None):
    response = client.post('/learning-nodes', json={'title': title, 'parent_id': parent_id})
    assert response.status_code == 201
    return response.json()


def test_nested_checklist_persists_independent_marks(client):
    area = create(client, 'Engenharia de dados')
    python = create(client, 'Python', area['id'])
    functions = create(client, 'Funções', python['id'])
    assert client.put(f"/learning-nodes/{python['id']}", json={'title': 'Python 3', 'completed': True}).status_code == 200
    nodes = {node['id']: node for node in client.get('/learning-nodes').json()}
    assert nodes[python['id']]['title'] == 'Python 3'
    assert nodes[python['id']]['completed'] is True
    assert nodes[functions['id']]['completed'] is False
    assert nodes[functions['id']]['parent_id'] == python['id']


def test_deletes_only_selected_branch(client):
    root = create(client, 'Dados')
    child = create(client, 'Python', root['id'])
    create(client, 'Funções', child['id'])
    other = create(client, 'SQL', root['id'])
    assert client.delete(f"/learning-nodes/{child['id']}").status_code == 204
    assert {node['id'] for node in client.get('/learning-nodes').json()} == {root['id'], other['id']}


@pytest.mark.parametrize('payload', [{'title': ' '}, {'title': 'x' * 161}, {'title': 'Python', 'parent_id': -1}])
def test_rejects_invalid_topic(client, payload):
    assert client.post('/learning-nodes', json=payload).status_code == 422


def test_missing_parent_and_item(client):
    assert client.post('/learning-nodes', json={'title': 'Python', 'parent_id': 999}).status_code == 404
    assert client.delete('/learning-nodes/999').status_code == 404
    assert client.put('/learning-nodes/999', json={'title': 'Python', 'completed': False}).status_code == 404


def test_parent_cannot_be_changed_to_create_cycle(client):
    root = create(client, 'Dados')
    assert client.put(f"/learning-nodes/{root['id']}", json={'title': 'Dados', 'completed': False, 'parent_id': root['id']}).status_code == 422


def test_depth_limit(client):
    parent = None
    for _ in range(32):
        parent = create(client, 'Tópico', parent)['id']
    assert client.post('/learning-nodes', json={'title': 'Mais um', 'parent_id': parent}).status_code == 422
