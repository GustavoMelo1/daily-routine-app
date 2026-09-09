import difflib
import requests
from pipeline.vocabulary import repetitive_tasks
from pipeline.validation import validate_day

def normalize_date(raw_date):
    if isinstance (raw_date, str):
        return raw_date.replace("/", "-")
    return raw_date

def publish_days(extracted_data):
    for day in extracted_data["dias"]:
        raw_date = day.get("data")
        normalized_date = normalize_date(raw_date)
        day["data"] = normalized_date
        validation_errors = validate_day(day)
        if validation_errors:
            error_reason = ", ".join(validation_errors)
            quarantine_day_payload = {
                "data": day.get("data"),
                "minutos_estudados": day.get("minutos_estudados"),
                "frase_do_dia": day.get("frase_do_dia"),
                "autor_frase": day.get("autor_frase"),
                "tipo": "normal",
                "motivo_erro": error_reason
            }
            quarantine_day_response = requests.post("http://localhost:8000/erros-quarentena", json=quarantine_day_payload)
            if quarantine_day_response.status_code == 400:
                continue
            quarantine_day_response.raise_for_status()
            quarantine_day_id = quarantine_day_response.json()['id']

            tasks = day.get("itens")
            if isinstance(tasks, list):
                for item in tasks:
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

                    quarantine_task_response = requests.post(
                        "http://localhost:8000/tarefas-quarentena",
                        json=quarantine_task_payload
                    )
                    quarantine_task_response.raise_for_status()

            continue

        existing_day_response = requests.get(f"http://localhost:8000/dias/{normalized_date}")
        if existing_day_response.status_code == 200:
            continue

        day_payload = {
            "data": normalized_date,
            "minutos_estudados": day["minutos_estudados"],
            "frase_do_dia": day["frase_do_dia"],
            "autor_frase": day["autor_frase"],
            "tipo": "normal"
            }
        day_response = requests.post("http://localhost:8000/dias", json=day_payload)
        day_id = day_response.json()['dia']

        for item in day["itens"]:
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
            requests.post("http://localhost:8000/tarefas", json=task_payload)