import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any

from src.models.courses_model import Course


class SCourseCreate(BaseModel):
    title: str = Field(..., min_length=1)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Название курса не может быть пустым")
        return value


class SCourseRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID курса")
    title: str

    model_config = ConfigDict(from_attributes=True)