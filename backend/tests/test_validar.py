from pipeline.validar import validar


def test_dia_valido_nao_retorna_erros():
    dia = {
        "data": "2026-08-25",
        "minutos_estudados": 60,
        "itens": [
            {"texto": "Estudar SQL", "status": "feito"}
        ]
    }

    resultado = validar(dia)

    assert resultado == []

def test_dia_invalido_retorna_erros():
    dia = {
        "data": "2026-99-99",
        "minutos_estudados": 1500,
        "itens": [
            {"texto": "   ", "status": "incerto"}
        ]
    }

    resultado = validar(dia)

    assert resultado == [
        "data_invalida",
        "minutos_invalidos",
        "tarefa_sem_descricao",
        "status_tarefa_invalido"
    ]
