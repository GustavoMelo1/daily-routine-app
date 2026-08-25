import difflib
import requests
from ocr import extract
from vocabulary import repetitive_tasks
from validar import validar

result = extract("exemplo.jpeg")

for dia in result["dias"]:
    transform = dia.get("data")
    if isinstance(transform, str):
        formatted = transform.replace("/", "-")
    else:
        formatted = transform
    dia["data"] = formatted
    erros = validar(dia)
    if erros:
        motivo_erro = ", ".join(erros)
        payload_erro = {
            "data": dia.get("data"),
            "minutos_estudados": dia.get("minutos_estudados"),
            "frase_do_dia": dia.get("frase_do_dia"),
            "autor_frase": dia.get("autor_frase"),
            "tipo": "normal",
            "motivo_erro": motivo_erro
        }
        response_erro = requests.post("http://localhost:8000/erros-quarentena", json=payload_erro)
        if response_erro.status_code == 400:
            continue
        response_erro.raise_for_status()
        erro_id = response_erro.json()['id']

        tarefas = dia.get("itens")
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

    checagem = requests.get(f"http://localhost:8000/dias/{formatted}")
    if checagem.status_code == 200:
        continue

    payload_dia = {
        "data": formatted, 
        "minutos_estudados": dia["minutos_estudados"], 
        "frase_do_dia": dia["frase_do_dia"], 
        "autor_frase": dia["autor_frase"], 
        "tipo": "normal"
        }
    response = requests.post("http://localhost:8000/dias", json=payload_dia) 
    get_id = response.json()['dia']

    for itens in dia["itens"]:
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
