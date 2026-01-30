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
from src.exception.client_exception import NotFoundError, ValidationError
from src.schemas.book_schemas import SBookCreate, SBookRead


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
            raise ValidationError(error="", detail=f"Имя не должно быть пустым")
        return v
    
    @field_validator("name", mode="after")
    @classmethod
    def valid_name(cls, v: str):
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        else:
            raise ValidationError
    

    
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
    def validate_name(cls, value: str):
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError



    @model_validator(mode="after")
    def validate_update_data(self) -> "SAuthorUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise NotFoundError(detail=f"Нет данных для обновления")
        return self

    

    async def apply_updates(self, author: Author) -> None:
        for field, value in self.model_dump(
            exclude_unset=True, 
            exclude_none=True,
            exclude={"books"}
        ).items():
            setattr(author, field, value)
        
        books_to_update = self.books
        if books_to_update is not None:
            author.books.clear()
            
            for book_schema in books_to_update:
                book_data = book_schema.model_dump(exclude_unset=True, exclude_none=True)
                if book_data:  
                    book = Book(**book_data)
                    book.author = author
                    author.books.append(book)


class SAuthorRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID автора")
    name: str
    books: List[SBookRead]

    model_config = ConfigDict(from_attributes=True)
