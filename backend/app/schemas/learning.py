from pydantic import BaseModel, Field, ConfigDict, field_validator


class LearningCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=160)
    parent_id: int | None = Field(default=None, gt=0)

    @field_validator('title')
    @classmethod
    def clean_title(cls, value):
        if not value.strip():
            raise ValueError('Informe o nome do tópico')
        return value.strip()


class LearningUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=160)
    completed: bool = Field(strict=True)
    @field_validator('title')
    @classmethod
    def clean_title(cls, value):
        if not value.strip():
            raise ValueError('Informe o nome do tópico')
        return value.strip()
