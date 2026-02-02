import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict

from src.models.books import Book



class SBookCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название книги")

    model_config = ConfigDict(from_attributes=True)

    def to_orm_model(self) -> "Book":
        return Book(**self.model_dump())



class SBookRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID книги")
    title: str

    model_config = ConfigDict(from_attributes=True)