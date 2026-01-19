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
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.author_models import Author
from src.models.books_models import Book
from src.schemas.book_schemas import SBookCreate, SBookRead


class SAuthorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    books: List[SBookCreate] = Field(
        default_factory=list, description="Список книг автора"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        else:
            raise ValueError("Имя должно быть строкой или числом")

    @model_validator(mode="after")
    def set_defaut_name(self):
        if self.name is None or self.name == "string":
            self.name = f"Author_{str(uuid.uuid4())[:8]}"
        return self

    @model_validator(mode="after")
    def validate_books(self) -> "SAuthorCreate":
        if self.books is None:
            return self
        return self

    def to_orm_models(self) -> tuple[Author, List[Book]]:
        author_data = self.model_dump(exclude="books")
        author = Author(**author_data)

        books = []
        if self.books:
            for book_schema in self.books:
                books_data = book_schema.model_dump()
                book = Book(**books_data)
                book.author = author
                books.append(book)

        return author, books


class SAuthorUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Имя автора"
    )
    books: Optional[List[SBookCreate]] = Field(None, description="Список книг автора")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValueError("Имя должно быть строкой или числом")

    @model_validator(mode="after")
    def set_defaut_name(self):
        if self.name is None or self.name == "string":
            self.name = f"Author_{str(uuid.uuid4())[:8]}"
        return self

    @model_validator(mode="after")
    def validate_update_data(self) -> "SAuthorUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise ValueError("Нет данных для обновления")
        return self

    @model_validator(mode="after")
    def validate_books(self) -> "SAuthorUpdate":
        if self.books is None:
            return self
        return self

    async def apply_updates(self, author: Author, session: AsyncSession) -> None:
        for field, value in self.model_dump(
            exclude_unset=True, exclude_none=True, exclude={"books"}
        ).items():
            setattr(author, field, value)

        if self.books is not None:
            # Clear existing books and add new ones
            for existing_book in author.books[:]:  # Iterate over a copy
                await session.delete(existing_book)
            author.books = [
                Book(**book_schema.model_dump(), author=author)
                for book_schema in self.books]


class SAuthorRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID автора")
    name: str
    books: List[SBookRead]

    model_config = ConfigDict(from_attributes=True)
