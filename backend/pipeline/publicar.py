import difflib
import requests
from ocr import extract
from vocabulary import repetitive_tasks
from validar import validar

result = extract("exemplo.jpeg")

for dia in result["dias"]:
    transform = dia["data"]
    formatted = transform.replace("/", "-")
    dia["data"] = formatted
    erros = validar(dia)
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
