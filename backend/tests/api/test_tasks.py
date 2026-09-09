def test_posttarefa(client, dicionario_tarefas):
    """Cria uma tarefa nova, deleta ela usando o ID que a propria API gerou na criação"""
    resposta = client.post("/tarefas", json = dicionario_tarefas)
    assert resposta.status_code == 201

    client.delete(f"/tarefas/{resposta.json()['id']}")

def test_deletetarefa(client, dicionario_tarefas):
    """Cria uma tarefa, deleta ela pelo id, e confere se deu certo"""
    resposta = client.post("/tarefas", json = dicionario_tarefas)

    tarefa_id = resposta.json()['id']
    delete = client.delete(f"/tarefas/{tarefa_id}")

    assert delete.status_code == 200

def test_deletetarefa_404(client):
    """Tenta deletar uma tarefa que nunca existiu e confere"""
    resposta = client.delete("/tarefas/99999999")

    assert resposta.status_code == 404

def test_patchtarefa(client, dicionario_tarefas):
    """Cria uma tarefa, atualiza o campo cumprida, e confere se deu certo"""
    resposta = client.post("/tarefas", json = dicionario_tarefas)

    tarefa_id = resposta.json()['id']
    patch = client.patch(f"/tarefas/{tarefa_id}", json = {"cumprida": 0})

    assert patch.status_code == 200

    client.delete(f"/tarefas/{tarefa_id}")

def test_patchtarefa_404(client):
    """Tenta atualizar uma tarefa que nunca existiu e confere"""
    resposta = client.patch("/tarefas/99999999", json = {"cumprida": 1})

    assert resposta.status_code == 404
