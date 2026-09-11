import difflib
from pipeline.vocabulary import repetitive_tasks

def build_quarantine_day_payload(day, validation_errors):
    error_reason = ", ".join(validation_errors)
    quarantine_day_payload = {
            "data": day.get("data"),
            "minutos_estudados": day.get("minutos_estudados"),
            "frase_do_dia": day.get("frase_do_dia"),
            "autor_frase": day.get("autor_frase"),
            "tipo": "normal",
            "motivo_erro": error_reason
            }
    return quarantine_day_payload

def build_quarantine_task_payload(item, quarantine_day_id):
    if not isinstance(item, dict):
        quarantine_task_payload = {
            "erro_quarentena_id": quarantine_day_id,
            "descricao": None,
            "cumprida": None,
            "motivo_erro": "tarefa_invalida"
        }
    else:
        description = item.get("texto")
        status = item.get("status")

        if status == "feito":
            completed = 1
        elif status in ["nao_feito", "aberto"]:
            completed = 0
        else:
            completed = None

        task_errors = []
        if not isinstance(description, str) or not description.strip():
            task_errors.append("tarefa_sem_descricao")
        if status not in ["feito", "nao_feito", "aberto"]:
            task_errors.append("status_tarefa_invalido")

        quarantine_task_payload = {
            "erro_quarentena_id": quarantine_day_id,
            "descricao": description,
            "cumprida": completed,
            "motivo_erro": ", ".join(task_errors) or None
        }
    return quarantine_task_payload

def build_day_payload(day):
    day_payload = {
        "data": day["data"],
        "minutos_estudados": day["minutos_estudados"],
        "frase_do_dia": day["frase_do_dia"],
        "autor_frase": day["autor_frase"],
        "tipo": "normal"
        }
    return day_payload

def build_task_payload(item, day_id):
    if item["status"] == "feito":
        completed = 1
    else:
        completed = 0
    matches = difflib.get_close_matches(item["texto"], repetitive_tasks)
    if matches:
        description = matches[0]
    else:
        description = item["texto"]
    
    task_payload = {
        "dia_id": day_id,
        "descricao": description,
        "cumprida": completed
    }
    return task_payload
        