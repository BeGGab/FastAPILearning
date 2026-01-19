import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict

from src.models.author_models import Book


class SBookCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название книги")


class SBookRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID книги")
    title: str

    model_config = ConfigDict(from_attributes=True)