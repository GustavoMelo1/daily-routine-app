from datetime import datetime

def validar(day):
    errors = []
    if not day.get("data"):
        errors.append("data_ausente")
    else:
        try:
            datetime.strptime(day["data"], "%Y-%m-%d")
        except ValueError:
            errors.append("data_invalida")

    studied_minutes = day.get("minutos_estudados")
    if studied_minutes is None:
        errors.append("minutos_ausentes")

    elif not isinstance(studied_minutes, int) or studied_minutes < 0 or studied_minutes > 1440:
        errors.append("minutos_invalidos")

    tasks = day.get("itens")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tarefas_ausentes")

    else:
        for item in tasks:
            if not isinstance(item, dict):
                errors.append("tarefa_invalida")
                continue
            description = item.get("texto")
            if not isinstance(description, str) or not description.strip():
                errors.append("tarefa_sem_descricao")

            status = item.get("status")
            valid_statuses = ["feito", "nao_feito", "aberto"]
            if status not in valid_statuses:
                errors.append("status_tarefa_invalido")

    return errors
