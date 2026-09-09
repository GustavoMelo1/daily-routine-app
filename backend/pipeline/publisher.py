import difflib
import requests
from pipeline.vocabulary import repetitive_tasks
from pipeline.validation import validate_day


def publish_days(extracted_data):
    for day in extracted_data["dias"]:
        raw_date = day.get("data")
        if isinstance(raw_date, str):
            normalized_date = raw_date.replace("/", "-")
        else:
            normalized_date = raw_date
        day["data"] = normalized_date
        erros = validate_day(day)
        if erros:
            motivo_erro = ", ".join(erros)
            payload_erro = {
                "data": day.get("data"),
                "minutos_estudados": day.get("minutos_estudados"),
                "frase_do_dia": day.get("frase_do_dia"),
                "autor_frase": day.get("autor_frase"),
                "tipo": "normal",
                "motivo_erro": motivo_erro
            }
            response_erro = requests.post("http://localhost:8000/erros-quarentena", json=payload_erro)
            if response_erro.status_code == 400:
                continue
            response_erro.raise_for_status()
            erro_id = response_erro.json()['id']

            tarefas = day.get("itens")
            if isinstance(tarefas, list):
                for item in tarefas:
                    if not isinstance(item, dict):
                        payload_tarefa_erro = {
                            "erro_quarentena_id": erro_id,
                            "descricao": None,
                            "cumprida": None,
                            "motivo_erro": "tarefa_invalida"
                        }
                    else:
                        descricao = item.get("texto")
                        status = item.get("status")

                        if status == "feito":
                            cumprida = 1
                        elif status in ["nao_feito", "aberto"]:
                            cumprida = 0
                        else:
                            cumprida = None

                        erros_tarefa = []
                        if not isinstance(descricao, str) or not descricao.strip():
                            erros_tarefa.append("tarefa_sem_descricao")
                        if status not in ["feito", "nao_feito", "aberto"]:
                            erros_tarefa.append("status_tarefa_invalido")

                        payload_tarefa_erro = {
                            "erro_quarentena_id": erro_id,
                            "descricao": descricao,
                            "cumprida": cumprida,
                            "motivo_erro": ", ".join(erros_tarefa) or None
                        }

                    response_tarefa_erro = requests.post(
                        "http://localhost:8000/tarefas-quarentena",
                        json=payload_tarefa_erro
                    )
                    response_tarefa_erro.raise_for_status()

            continue

        checagem = requests.get(f"http://localhost:8000/dias/{normalized_date}")
        if checagem.status_code == 200:
            continue

        payload_dia= {
            "data": normalized_date,
            "minutos_estudados": day["minutos_estudados"],
            "frase_do_dia": day["frase_do_dia"],
            "autor_frase": day["autor_frase"],
            "tipo": "normal"
            }
        response = requests.post("http://localhost:8000/dias", json=payload_dia)
        get_id = response.json()['dia']

        for itens in day["itens"]:
            if itens["status"] == "feito":
                cumprida = 1
            else:
                cumprida = 0
            conference = difflib.get_close_matches(itens["texto"], repetitive_tasks)
            if conference:
                descricao = conference[0]
            else:
                descricao = itens["texto"]

            payload_tarefas = {
                "dia_id": get_id,
                "descricao": descricao,
                "cumprida": cumprida
            }
            requests.post("http://localhost:8000/tarefas", json=payload_tarefas)