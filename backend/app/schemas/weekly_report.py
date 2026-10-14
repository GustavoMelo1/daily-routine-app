from datetime import date
from pydantic import BaseModel, Field, field_validator


class WeeklyReportCreate(BaseModel):
    report_date: date
    title: str = Field(min_length=1, max_length=160)
    filename: str = Field(min_length=4, max_length=255)
    content: str = Field(min_length=1, max_length=100_000)

    @field_validator('title', 'content')
    @classmethod
    def require_text(cls, value):
        if not value.strip() or '\x00' in value:
            raise ValueError('Texto vazio ou inválido')
        return value

    @field_validator('filename')
    @classmethod
    def require_markdown(cls, value):
        if not value.lower().endswith('.md') or any(char in value for char in ('/', '\\', '\x00')):
            raise ValueError('Informe apenas o nome de um arquivo .md')
        return value


class WeeklyReportUpdate(WeeklyReportCreate):
    version: int = Field(ge=1)


class ComparisonRequest(BaseModel):
    previous_report_id: int | None = Field(default=None, gt=0)


class ProgressEvidence(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=1, max_length=2000)
    previous_evidence: str | None = Field(default=None, max_length=2000)
    current_evidence: str = Field(min_length=1, max_length=2000)


class WeeklyProgress(BaseModel):
    summary: str = Field(min_length=1, max_length=4000)
    advances: list[ProgressEvidence] = Field(max_length=10)
    consolidations: list[ProgressEvidence] = Field(max_length=10)
    pending: list[ProgressEvidence] = Field(max_length=10)
    limitations: str = Field(min_length=1, max_length=2000)
