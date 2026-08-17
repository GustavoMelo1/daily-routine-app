from fastapi.testclient import TestClient
from src.main import app
import pytest


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def dicionario_dias():
    """Retorna um dicionario padrao com os campos de um dia, sem a data"""
    return {
        "minutos_estudados": 10,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal"}

@pytest.fixture
def dicionario_tarefas():
    """Retorna um dicionario padrao com os campos de uma tarefa"""
    return {
        "dia_id": 1,
        "descricao": "teste",
        "cumprida": 1}

def test_getdia(client, dicionario_dias):
    """Cria um dia, busca ele pela data e confere, depois deleta"""
    dicionario = {**dicionario_dias, "data": "2026-08-03"}
    client.post("/dias", json=dicionario)

    resposta = client.get("/dias/2026-08-03")
    assert resposta.status_code == 200

    client.delete("/dias/2026-08-03")

def test_getdia_404(client):
    """Busca um dia que nunca existiu e confere"""
    resposta = client.get("/dias/2099-01-01")
    assert resposta.status_code == 404

def test_postdia(client, dicionario_dias):
    """Cria um dia novo que nao existe confere, deleta logo em seguida"""
    dicionario = {**dicionario_dias, "data": "2026-08-01"}  
    resposta = client.post("/dias", json = dicionario)
    assert resposta.status_code == 201

    client.delete("/dias/2026-08-01")

def test_postdia_dup(client, dicionario_dias):
    """Tenta criar um dia duplicado e confere se a API recusa"""
    dicionario = {**dicionario_dias, "data": "2026-07-02"}
    resposta = client.post("/dias", json = dicionario)
    assert resposta.status_code == 400

def test_deletedia(client, dicionario_dias):
    """Cria um dia novo so por criar, deleta ele, e confere"""
    dicionario = {**dicionario_dias, "data": "2026-08-01"}
    client.post("/dias", json = dicionario)
    delete = client.delete("/dias/2026-08-01")

    assert delete.status_code == 200

def test_deletedia_404(client):
    """Tenta deletar uma data que nunca existiu"""
    resposta = client.delete("/dias/2027-10-01")

    assert resposta.status_code == 404

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
