from datetime import datetime

def validar(dia):   
    erros = []
    if not dia.get("data"):
        erros.append("data_ausente")
    else:
        try:
            datetime.strptime(dia["data"], "%Y-%m-%d")
        except ValueError:
            erros.append("data_invalida")

    return erros

