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


class SAuthorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    books: List[SBookCreate] = Field(
        default_factory=list, description="Список книг автора"
    )

    def prepare_author_db_data(self) -> dict:
        author_data = self.model_dump(exclude={"books"})
        author_data["books"] = [Book(**books.model_dump()) for books in self.books]
        return author_data


class SAuthorRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID автора")
    name: str
    books: List[SBookRead]

    model_config = ConfigDict(from_attributes=True)
