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

    minutos = dia.get("minutos_estudados")

    if minutos is None:
        erros.append("minutos_ausentes")

    elif not isinstance(minutos, int) or minutos < 0 or minutos > 1440:
        erros.append("minutos_invalidos")

    return erros

