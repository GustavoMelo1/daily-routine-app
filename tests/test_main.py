from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_getdia():
    """Busca um dia que ja existe no banco e confere"""
    resposta = client.get("/dias/2026-07-02")
    assert resposta.status_code == 200

def test_getdia_404():
    """Busca um dia que nunca existiu e confere"""
    resposta = client.get("/dias/2099-01-01")
    assert resposta.status_code == 200

def test_postdia():
    """Cria um dia novo (nao existia) confere, deleta logo em seguida"""
    resposta = client.post("/dias", json={
        "data": "2026-08-01",
        "minutos_estudados": 10,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal"
    })
    assert resposta.status_code == 200

    client.delete("/dias/2026-08-01")

def test_postdia_dup():
    """Tenta criar um dia duplicado e confere se a API recusa"""
    resposta = client.post("/dias", json={
        "data": "2026-07-02",
        "minutos_estudados": 10,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal"
    })
    assert resposta.status_code == 400

def test_deletedia():
    """Cria um dia novo so por criar, deleta ele, e confere"""
    client.post("/dias", json={
        "data": "2026-09-01",
        "minutos_estudados": 10,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal"
    })
    delete = client.delete("/dias/2026-09-01")

    assert delete.status_code == 200

def test_deletedia_404():
    """Tenta deletar uma data que nunca existiu"""
    resposta = client.delete("/dias/2027-10-01")

    assert resposta.status_code == 404

def test_posttarefa():
    """Cria uma tarefa nova, deleta ela usando o ID que a propria API gerou na criação."""
    resposta = client.post("/tarefas", json={
        "dia_id": 1,
        "descricao": "teste",
        "cumprida": 1
    })
    assert resposta.status_code == 200

    client.delete(f"/tarefas/{resposta.json()['id']}")
