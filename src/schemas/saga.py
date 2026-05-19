from typing import List, Optional

from pydantic import BaseModel, Field


class SagaBookInput(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название книги")


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


class CreateBiographyInput(BaseModel):
    request_id: str = Field(..., description="ID запроса")
    author_id: str = Field(..., description="ID автора")
    author_name: str = Field(..., description="Имя автора")
    biography_text: str = Field(..., description="Текст биографии")
    year_of_birth: int = Field(..., description="Год рождения")
    year_of_death: int = Field(..., description="Год смерти")


class DeleteBiographyInput(BaseModel):
    author_id: str = Field(..., description="ID автора")
    request_id: str = Field(..., description="ID запроса")


class DeleteAuthorInput(BaseModel):
    author_id: str = Field(..., description="ID автора")
    request_id: str = Field(..., description="ID запроса")


class CompensationResult(BaseModel):
    attempted: bool = Field(..., description="Была ли попытка компенсации")
    success: bool = Field(..., description="Успешно ли компенсировано")
    details: Optional[str] = Field(None, description="Описание ошибки")


class CreateAuthorSagaResult(BaseModel):
    author_id: Optional[str] = Field(None, description="ID автора")
    biography_created: bool = Field(..., description="Была ли создана биография")
    compensated_author: CompensationResult = Field(
        ..., description="Результат компенсации автора"
    )
    compensated_biography: CompensationResult = Field(
        ..., description="Результат компенсации биографии"
    )
