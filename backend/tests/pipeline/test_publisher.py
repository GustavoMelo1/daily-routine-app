import pytest
from requests.exceptions import HTTPError
from unittest.mock import Mock
from pipeline.publisher import publish_days

def test_publicar_dia_valido(monkeypatch):
    """Publica um dia valido e confere as rotas normais chamadas"""
    chamadas_post = []

    def fake_get(url):
        resposta = Mock()
        resposta.status_code = 404
        return resposta

    monkeypatch.setattr("pipeline.publisher.requests.get",fake_get)   

    def fake_post(url, json):
        chamadas_post.append((url, json))
        resposta = Mock()
        resposta.status_code = 201
        resposta.json.return_value = {"dia": 1}
        return resposta

    monkeypatch.setattr("pipeline.publisher.requests.post",fake_post)

    resultado = {
        "dias": [
            {
                "data": "2026-08-26",
                "minutos_estudados": 60,
                "frase_do_dia": "Teste",
                "autor_frase": "Autor",
                "itens": [
                    {"texto": "Estudar SQL", "status": "feito"}
                ]
            }
        ]
    }
    publish_days(resultado)
    assert len(chamadas_post) == 2
    assert chamadas_post[0][0] == "http://localhost:8000/dias"
    assert chamadas_post[1][0] == "http://localhost:8000/tarefas"

def test_publicar_dia_invalido(monkeypatch):
    """Envia um dia invalido somente para as rotas de quarentena"""
    chamadas_post = []

    def fake_get(url):
        raise AssertionError("Dia invalido nao deve consultar a rota normal")

    monkeypatch.setattr("pipeline.publisher.requests.get",fake_get)   

    def fake_post(url, json):
        chamadas_post.append((url, json))
        resposta = Mock()
        resposta.status_code = 201
        resposta.json.return_value = {"id": 1}
        return resposta

    monkeypatch.setattr("pipeline.publisher.requests.post",fake_post)

    resultado = {
        "dias": [
            {
                "data": "2026-99-99",
                "minutos_estudados": 1500,
                "frase_do_dia": "Teste",
                "autor_frase": "Autor",
                "itens": [
                    {"texto": "   ", "status": "incerto"}
                ]
            }
        ]
    }
    publish_days(resultado)
    assert len(chamadas_post) == 2
    assert chamadas_post[0][0] == "http://localhost:8000/erros-quarentena"
    assert chamadas_post[1][0] == "http://localhost:8000/tarefas-quarentena"

def test_publish_days_stops_on_lookup_error(monkeypatch):
    response = Mock()
    response.status_code = 500
    response.raise_for_status.side_effect = HTTPError("API unavailable")
    fake_get = Mock(return_value=response)
    fake_post = Mock()

    monkeypatch.setattr("pipeline.publisher.requests.get", fake_get)
    monkeypatch.setattr("pipeline.publisher.requests.post", fake_post)

    extracted_data = {
        "dias": [{
            "data": "2026-08-26",
            "minutos_estudados": 60,
            "frase_do_dia": "Teste",
            "autor_frase": "Autor",
            "itens": [{"texto": "Estudar SQL", "status": "feito"}],
        }]
    }

    with pytest.raises(HTTPError, match="API unavailable"):
        publish_days(extracted_data)

    fake_post.assert_not_called()

def test_publish_days_stops_on_day_creation_error(monkeypatch):
    lookup_response = Mock()
    lookup_response.status_code = 404
    fake_get = Mock(return_value=lookup_response)

    creation_response = Mock()
    creation_response.status_code = 500
    creation_response.raise_for_status.side_effect = HTTPError("API unavailable")
    fake_post = Mock(return_value=creation_response)

    monkeypatch.setattr("pipeline.publisher.requests.get", fake_get)
    monkeypatch.setattr("pipeline.publisher.requests.post", fake_post)

    extracted_data = {
        "dias": [{
            "data": "2026-08-26",
            "minutos_estudados": 60,
            "frase_do_dia": "Teste",
            "autor_frase": "Autor",
            "itens": [{"texto": "Estudar SQL", "status": "feito"}],
        }]
    }

    with pytest.raises(HTTPError, match="API unavailable"):
        publish_days(extracted_data)

    fake_post.assert_called_once()
    assert fake_post.call_args.args[0] == "http://localhost:8000/dias"

def test_publish_days_stops_on_task_creation_error(monkeypatch):
    lookup_response = Mock()
    lookup_response.status_code = 404
    fake_get = Mock(return_value=lookup_response)
    creation_response = Mock()
    creation_response.status_code = 201
    creation_response.json.return_value = {"dia": 1}

    task_response = Mock()
    task_response.status_code = 500
    task_response.raise_for_status.side_effect = HTTPError("API unavailable")

    fake_post = Mock(side_effect=[creation_response, task_response])

    monkeypatch.setattr("pipeline.publisher.requests.get", fake_get)
    monkeypatch.setattr("pipeline.publisher.requests.post", fake_post)

    extracted_data = {
        "dias": [{
            "data": "2026-08-26",
            "minutos_estudados": 60,
            "frase_do_dia": "Teste",
            "autor_frase": "Autor",
            "itens": [{"texto": "Estudar SQL", "status": "feito"},
                      {"texto": "Estudar SQL", "status": "feito"},
                      {"texto": "Ler livro", "status": "aberto"}],
        }]
    }

    with pytest.raises(HTTPError, match="API unavailable"):
        publish_days(extracted_data)

    assert fake_post.call_count == 2
    assert fake_post.call_args_list[0].args[0] == "http://localhost:8000/dias"
    assert fake_post.call_args_list[1].args[0] == "http://localhost:8000/tarefas"

