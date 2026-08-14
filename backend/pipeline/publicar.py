import requests
from ocr import extract

result = extract("exemplo.jpeg")

for dia in result["dias"]:
    checagem = requests.get(f"http://localhost:8000/dias/{dia['data']}")
    if checagem.status_code == 200:
        continue

    payload_dia = {
        "data": dia["data"], 
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
        payload_tarefas = {
            "dia_id": get_id,
            "descricao": itens["texto"],
            "cumprida": cumprida
        }
        requests.post("http://localhost:8000/tarefas", json=payload_tarefas)