from pydantic import BaseModel

class TaskCreate(BaseModel):
    dia_id: int
    descricao: str
    cumprida: int

class TaskUpdate(BaseModel):
    cumprida: int
