import difflib
from pipeline.dates import normalize_notebook_date
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


def build_import_payload(extracted_data):
    from app.schemas.image_import import ImageImportPublish
    from pipeline.validation import validate_day
    import json
    if not isinstance(extracted_data, dict) or not isinstance(extracted_data.get("dias"), list):
        raise ValueError("OCR não retornou uma lista de dias")
    payload = {"days": [], "quarantine_days": []}
    for original in extracted_data["dias"]:
        if not isinstance(original, dict):
            raise ValueError("OCR retornou um dia que não é um objeto")
        day = dict(original)
        day["data"] = normalize_notebook_date(day.get("data"))
        errors = validate_day(day)
        if errors:
            item = build_quarantine_day_payload(day, errors)
            for key in ("data", "frase_do_dia", "autor_frase"):
                value = item[key]
                if value is not None and not isinstance(value, str):
                    item[key] = json.dumps(value, ensure_ascii=False)
            if type(item["minutos_estudados"]) is not int and item["minutos_estudados"] is not None:
                item["motivo_erro"] += "; minutos originais: " + json.dumps(item["minutos_estudados"], ensure_ascii=False)
                item["minutos_estudados"] = None
            item["tarefas"] = []
            for task in day.get("itens", []) if isinstance(day.get("itens"), list) else []:
                task_payload = build_quarantine_task_payload(task, 0)
                task_payload.pop("erro_quarentena_id")
                description = task_payload["descricao"]
                if description is not None and not isinstance(description, str):
                    task_payload["descricao"] = json.dumps(description, ensure_ascii=False)
                item["tarefas"].append(task_payload)
            payload["quarantine_days"].append(item)
        else:
            day["frase_do_dia"] = day.get("frase_do_dia") or ""
            day["autor_frase"] = day.get("autor_frase") or ""
            item = build_day_payload(day)
            item["tarefas"] = []
            for task in day["itens"]:
                task_payload = build_task_payload(task, 0)
                task_payload.pop("dia_id")
                item["tarefas"].append(task_payload)
            payload["days"].append(item)
    return ImageImportPublish.model_validate(payload).model_dump()
