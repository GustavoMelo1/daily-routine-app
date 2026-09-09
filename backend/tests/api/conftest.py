import pytest

@pytest.fixture
def dicionario_dias():
    """Retorna um dicionario padrao com os campos de um dia, sem a data"""
    return {
        "minutos_estudados": 10,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal"}

@pytest.fixture
def dia_id(client, dicionario_dias):
    """Cria um dia no banco temporario e retorna seu id"""
    payload = {**dicionario_dias, "data": "2026-08-02"}
    resposta = client.post("/dias", json=payload)
    assert resposta.status_code == 201
    return resposta.json()["dia"]

@pytest.fixture
def dicionario_tarefas(dia_id):
    """Retorna um dicionario padrao com os campos de uma tarefa"""
    return {
        "dia_id": dia_id,
        "descricao": "teste",
        "cumprida": 1}
