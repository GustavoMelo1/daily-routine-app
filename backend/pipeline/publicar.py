import requests
from ocr import extract

result = extract("exemplo.jpeg")

for dia in result["dias"]:
    payload_dia = {
        "data": dia["data"], 
        "minutos_estudados": dia["minutos_estudados"], 
        "frase_do_dia": dia["frase_do_dia"], 
        "autor_frase": dia["autor_frase"], 
        "tipo": "normal"
        }
    response = requests.post("http://localhost:8000/dias", json=payload_dia)

