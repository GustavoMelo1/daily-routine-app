def validar(dia):   
    erros = []
    if not dia.get("data"):
        erros.append("data_ausente")

    return erros