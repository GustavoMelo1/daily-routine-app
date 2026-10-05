from app.schemas.day import DayCreate
from app.schemas.quarantine import QuarantineDayCreate
from pydantic import BaseModel, Field, model_validator

class ImageImportTaskCreate(BaseModel):
    descricao: str
    cumprida: int = Field(ge=0, le=1)

class ImageImportDayCreate(DayCreate):
    tarefas: list[ImageImportTaskCreate] = Field(min_length=1)

class ImageImportQuarantineTaskCreate(BaseModel):
    descricao: str | None = None
    cumprida: int | None = None
    motivo_erro: str | None = None

class ImageImportQuarantineDayCreate(QuarantineDayCreate):
    tarefas: list[ImageImportQuarantineTaskCreate] = Field(default_factory=list)

class ImageImportPublish(BaseModel):
    days: list[ImageImportDayCreate] = Field(default_factory=list)
    quarantine_days: list[ImageImportQuarantineDayCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_records(self):
        if not self.days and not self.quarantine_days:
            raise ValueError("A importação precisa conter ao menos um registro")
        return self