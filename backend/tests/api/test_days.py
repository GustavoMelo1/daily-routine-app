import pytest


def test_getdia(client, dicionario_dias):
    """Cria um dia, busca ele pela data e confere, depois deleta"""
    dicionario = {**dicionario_dias, "data": "2026-08-03"}
    client.post("/dias", json=dicionario)

    resposta = client.get("/dias/2026-08-03")
    assert resposta.status_code == 200

    client.delete("/dias/2026-08-03")

def test_list_days_by_month(client, dicionario_dias):
    payload = {**dicionario_dias, "data": "2026-08-04"}
    resposta_criacao = client.post("/dias", json=payload)
    assert resposta_criacao.status_code == 201
    resposta = client.get("/dias", params={"ano": 2026, "mes": 8})
    assert resposta.status_code == 200
    assert any(
        item["data"] == "2026-08-04"
        for item in resposta.json()
    )

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

    primeira_resposta = client.post("/dias", json = dicionario)
    resposta = client.post("/dias", json = dicionario)

    assert primeira_resposta.status_code == 201
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


@pytest.mark.parametrize("minutes", [0, 1440])
def test_create_day_accepts_minute_boundaries(client, dicionario_dias, minutes):
    payload = {
        **dicionario_dias,
        "data": "2026-08-05",
        "minutos_estudados": minutes,
    }

    response = client.post("/dias", json=payload)

    assert response.status_code == 201


@pytest.mark.parametrize("minutes", [-1, 1441])
def test_create_day_rejects_out_of_range_minutes(client, dicionario_dias, minutes):
    payload = {
        **dicionario_dias,
        "data": "2026-08-05",
        "minutos_estudados": minutes,
    }

    response = client.post("/dias", json=payload)

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", "minutos_estudados"]
        for error in response.json()["detail"]
    )
    assert client.get("/dias/2026-08-05").status_code == 404
