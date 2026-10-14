from app.schemas.day import DayCreate
from app.schemas.quarantine import QuarantineDayCreate
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import date

class ImageImportTaskCreate(BaseModel):
    descricao: str = Field(min_length=1)
    cumprida: int = Field(ge=0, le=1, strict=True)

    @field_validator("descricao")
    @classmethod
    def require_description(cls, value):
        if not value.strip():
            raise ValueError("Descrição vazia")
        return value

class ImageImportDayCreate(DayCreate):
    tarefas: list[ImageImportTaskCreate] = Field(min_length=1)

    @field_validator("data")
    @classmethod
    def require_iso_date(cls, value):
        parsed = date.fromisoformat(value)
        if value != parsed.isoformat():
            raise ValueError("Use YYYY-MM-DD")
        return value

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

class ImageImportCreate(BaseModel):
    image_hash: str = Field(
        min_length=64,
        max_length=64,
        pattern="^[0-9a-f]+$",
    )


class ImageImportFailure(BaseModel):
    error_message: str = Field(min_length=1, max_length=2000)
