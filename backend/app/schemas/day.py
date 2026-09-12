from pydantic import BaseModel, Field

class DayCreate(BaseModel): 

    data: str
    minutos_estudados: int = Field(ge=0, le=1440)
    frase_do_dia: str
    autor_frase: str
    tipo: str