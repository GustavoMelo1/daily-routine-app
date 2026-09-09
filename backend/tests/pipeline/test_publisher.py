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
