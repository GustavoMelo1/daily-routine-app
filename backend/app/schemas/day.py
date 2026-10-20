from pydantic import BaseModel, Field, field_validator
from datetime import date

class DayCreate(BaseModel): 

    data: str
    minutos_estudados: int = Field(ge=0, le=1440)
    frase_do_dia: str
    autor_frase: str
    tipo: str


class DayPlan(BaseModel):
    data: date
    minutos_estudados: int = Field(default=0, ge=0, le=1440, strict=True)
    frase_do_dia: str = ''
    autor_frase: str = ''
    tipo: str = 'normal'
    tarefas: list[str] = Field(default_factory=list, max_length=200)

    @field_validator('tarefas')
    @classmethod
    def validate_tasks(cls, values):
        if any(not value.strip() or len(value.strip()) > 500 for value in values):
            raise ValueError('Cada tarefa precisa ter entre 1 e 500 caracteres')
        return [value.strip() for value in values]


class DayMinutesUpdate(BaseModel):
    minutos_estudados: int = Field(ge=0, le=1440, strict=True)
