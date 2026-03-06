import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any


from src.exception.client_exception import ValidationError
from src.models.courses import Course


class SCourseCreate(BaseModel):
    """Схема для создания одного курса."""

    title: str = Field(..., min_length=1, description="Название курса")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("title", mode="before")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValidationError(detail=f"Название курса не может быть пустым")
        return value

    def to_orm_model(self) -> Course:
        return Course(**self.model_dump())


class SCourseRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID курса")
    title: str

    model_config = ConfigDict(from_attributes=True)
