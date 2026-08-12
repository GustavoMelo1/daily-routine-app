import requests


json_dias = {
    "data" : "2026-08-10",
    "minutos_estudados": 45,
    "frase_do_dia": "Amar e deixar ir " ,
    "autor_frase": "Gustavo Melo",
    "tipo": "Normal"
}

json_tarefas = [
    {"descricao": "studar Python", "cumprida": 1},
]

response = requests.post("http://localhost:8000/dias", json=json_dias)

dia_id  = response.json()['day']