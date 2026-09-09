def test_post_dia_e_tarefa_na_quarentena(client):
    """Cria um dia e uma tarefa na quarentena, confere e remove os registros"""

    payload_dia = {
        "data": "2099-08-25",
        "minutos_estudados": 1500,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal",
        "motivo_erro": "minutos_invalidos"
    }

    resposta_dia = client.post("/erros-quarentena", json=payload_dia)

    assert resposta_dia.status_code == 201
    assert "id" in resposta_dia.json()

    erro_id = resposta_dia.json()["id"]

    payload_tarefa = {
        "erro_quarentena_id": erro_id,
        "descricao": "Estudar SQL",
        "cumprida": 1,
        "motivo_erro": None
    }

    resposta_tarefa = client.post(
        "/tarefas-quarentena",
        json=payload_tarefa
    )

    assert resposta_tarefa.status_code == 201
    assert "id" in resposta_tarefa.json()
