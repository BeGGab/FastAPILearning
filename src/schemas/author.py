import re
import uuid
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)
from typing import Optional, List, Dict

from src.models.author import Author
from src.models.books import Book
from src.exception.client_exception import NotFoundError, ValidationError
from src.schemas.book import SBookCreate, SBookRead


class SAuthorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    books: List[SBookCreate] = Field(
        default_factory=list, description="Список книг автора"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", mode="before")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if v is None or v == "string":
            raise ValidationError(detail=f"Имя не должно быть пустым")
        return v

    @field_validator("name", mode="after")
    @classmethod
    def valid_name(cls, v: str):
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        else:
            raise ValidationError(detail="Имя автора должно быть числом или строкой")

    @field_validator("books", mode="before")
    @classmethod
    def normalize_books(cls, v):
        if v is None:
            return []
        if isinstance(v, Dict):
            return [SBookCreate(**v)]
        if isinstance(v, List):
            normalized: List[SBookCreate] = []
            for item in v:
                if isinstance(item, SBookCreate):
                    normalized.append(item)
                elif isinstance(item, dict):
                    normalized.append(SBookCreate(**item))
                else:
                    raise ValidationError(
                        detail="Элемент списка books должен быть объектом или SBookCreate"
                    )
            return normalized
        raise ValidationError(detail="Поле books должно быть списком")

    def to_orm_models(self) -> tuple[Author, List[Book]]:
        author_data = self.model_dump(exclude={"books"})
        author = Author(**author_data)

        books: List[Book] = [book_schema.to_orm_model() for book_schema in self.books]
        author.books = books
        return author, books


class SAuthorUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Имя автора"
    )
    books: Optional[List[SBookCreate]] = Field(None, description="Список книг автора")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str):
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError(detail="Имя автора должно быть числом или строкой")

    @model_validator(mode="after")
    def validate_update_data(self) -> "SAuthorUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise NotFoundError(detail=f"Нет данных для обновления")
        return self

    def apply_updates(self, author: Author) -> None:
        update_data = self.model_dump(
            exclude_unset=True, exclude_none=True, exclude={"books"}
        )

        for field, value in update_data.items():
            setattr(author, field, value)

        if self.books is not None:
            new_books_map = {b.title: b for b in self.books}
            author.books = [b.to_orm_model() for b in new_books_map.values()]


class SAuthorRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID автора")
    name: str
    books: List[SBookRead]
    biography_text: Optional[str] = Field(None, description="Биография автора")
    year_of_birth: Optional[int] = Field(None, description="Год рождения автора")
    year_of_death: Optional[int] = Field(None, description="Год смерти автора")

    model_config = ConfigDict(from_attributes=True)
