from datetime import datetime

def validar(dia):   
    erros = []
    if not dia.get("data"):
        erros.append("data_ausente")
    else:
        try:
            datetime.strptime(dia["data"], "%Y-%m-%d")
        except ValueError:
            erros.append("data_invalida")

    minutos = dia.get("minutos_estudados")
    if minutos is None:
        erros.append("minutos_ausentes")

    elif not isinstance(minutos, int) or minutos < 0 or minutos > 1440:
        erros.append("minutos_invalidos")

    tarefas = dia.get("itens")
    if not isinstance(tarefas, list) or not tarefas:
        erros.append("tarefas_ausentes")

    else:
        for itens in tarefas:
            if not isinstance(itens, dict):
                erros.append("tarefa_invalida")
                continue
            search_value = itens.get("texto")
            if not isinstance(search_value, str) or not search_value.strip():
                erros.append("tarefa_sem_descricao")

            search_status = itens.get("status")
            status_validos = ["feito", "nao_feito", "aberto"]
            if search_status not in status_validos:
                erros.append("status_tarefa_invalido")

    return erros