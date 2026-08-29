from pydantic import BaseModel

class QuarantineTaskCreate(BaseModel):
    erro_quarentena_id: int
    descricao: str | None = None
    cumprida: int | None = None
    motivo_erro: str | None = None

class QuarantineDayCreate(BaseModel):
    data: str | None = None
    minutos_estudados: int | None = None
    frase_do_dia: str | None = None
    autor_frase: str | None = None
    tipo: str | None = None
    motivo_erro: str 
