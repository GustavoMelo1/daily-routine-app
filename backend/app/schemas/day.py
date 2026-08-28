from pydantic import BaseModel

class DayCreate(BaseModel): 

    data: str
    minutos_estudados: int
    frase_do_dia: str
    autor_frase: str
    tipo: str