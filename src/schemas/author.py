import uuid
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)
from typing import Optional, List, Dict, Any

from src.models.author import Author
from src.models.books import Book
from src.exception.client_exception import NotFoundError, ValidationError
from src.schemas.book import SBookCreate, SBookRead, SagaBookInput
from src.schemas.biography import SAuthorBioResponse


class SAuthorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    books: List[SBookCreate] = Field(
        default_factory=list, description="Список книг автора"
    )
    biography_text: Optional[str] = Field(
        None, description="Текст биографии (сервис биографий)"
    )
    year_of_birth: Optional[int] = Field(
        None, description="Год рождения (сервис биографий)"
    )
    year_of_death: Optional[int] = Field(
        None, description="Год смерти (сервис биографий)"
    )

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def biography_all_or_nothing(self) -> "SAuthorCreate":
        bio = (self.biography_text, self.year_of_birth, self.year_of_death)
        if any(x is not None for x in bio) and not all(x is not None for x in bio):
            raise ValidationError(
                detail="Укажите все поля биографии (biography_text, year_of_birth, year_of_death) "
                "или не передавайте их"
            )
        return self

    @field_validator("name", mode="before")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if v is None or v == "string":
            raise ValidationError(detail="Имя не должно быть пустым")
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
        author_data = self.model_dump(
            exclude={"books", "biography_text", "year_of_birth", "year_of_death"}
        )
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
            raise NotFoundError(detail="Нет данных для обновления")
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
    
    @classmethod
    def from_orm(cls, author: Author) -> "SAuthorRead":
        return cls.model_validate(author, from_attributes=True)

    @classmethod
    def from_orm_many(cls, authors: List[Author]) -> List["SAuthorRead"]:
        return [cls.from_orm(author) for author in authors]

    @classmethod
    def from_cache(cls, data: Dict[str, Any]) -> "SAuthorRead":
        return cls.model_validate(data)

    @classmethod
    def from_cache_many(cls, data: List[Dict[str, Any]]) -> List["SAuthorRead"]:
        return [cls.from_cache(item) for item in data]

    def to_cache(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def to_cache_many(cls, authors: List["SAuthorRead"]) -> List[Dict[str, Any]]:
        return [author.to_cache() for author in authors]


    def to_bio_response(self, bio_data: Optional["SAuthorBioResponse"]) -> "SAuthorRead":
        if not bio_data:
            return self
        return self.model_copy(
            update={
                "biography_text": bio_data.biography_text,
                "year_of_birth": bio_data.year_of_birth,
                "year_of_death": bio_data.year_of_death,
            }
        )


    


class CreateAuthorSagaInput(BaseModel):
    request_id: str = Field(..., description="ID запроса")
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    books: List[SagaBookInput] = Field(
        default_factory=list, description="Список книг автора"
    )
    biography_text: Optional[str] = Field(
        None, description="Текст биографии (сервис биографий)"
    )
    year_of_birth: Optional[int] = Field(
        None, description="Год рождения (сервис биографий)"
    )
    year_of_death: Optional[int] = Field(
        None, description="Год смерти (сервис биографий)"
    )

    @property
    def has_biography(self) -> bool:
        return None not in (self.biography_text, self.year_of_birth, self.year_of_death)

    def to_author_create(self) -> SAuthorCreate:
        return SAuthorCreate(
            name=self.name,
            books=[SBookCreate(title=b.title) for b in self.books],
            biography_text=self.biography_text,
            year_of_birth=self.year_of_birth,
            year_of_death=self.year_of_death,
        )



class DeleteAuthorInput(BaseModel):
    author_id: str = Field(..., description="ID автора")
    request_id: str = Field(..., description="ID запроса")


class CompensationResult(BaseModel):
    attempted: bool = Field(..., description="Была ли попытка компенсации")
    success: bool = Field(..., description="Успешно ли компенсировано")
    details: Optional[str] = Field(None, description="Описание ошибки")


class CompensationSummary(BaseModel):
    author: CompensationResult
    biography: CompensationResult

    @property
    def all_success(self) -> bool:
        return self.author.success and self.biography.success

class CreateAuthorSagaResult(BaseModel):
    author_id: str 
    biography_created: bool = Field(..., description="Была ли создана биография")