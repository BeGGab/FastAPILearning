import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union
from src.Author.schemas_author import SAuthorCreate, SAuthorRead
from src.Author.session_author import AuthorDAO
from src.Author.models import Author, Book
from src.db import get_async_session

arouter = APIRouter()

@arouter.get('/healthcheck')
async def healthcheck() -> dict[str, str]:
    return {"ststus": "ok"}


@arouter.post("/author", status_code=status.HTTP_201_CREATED)
async def create_author(authoradd: SAuthorCreate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await AuthorDAO.create_author_with_books(session=session, author_data=authoradd.model_dump())
    return author


@arouter.get("/author/{id}")
async def find_author_is_id(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await AuthorDAO.find_one_or_none_by_id(session=session, id=id)
    return author


@arouter.get("/author")
async def find_all_authors(session: AsyncSession, limit: int = 10, offset: int = 0) -> List[SAuthorRead]:
    authors = await AuthorDAO.find_all(session=session, limit=limit, offset=offset)
    return authors


@arouter.delete("/author/{id}")
async def delete_author(session: AsyncSession, id: Union[uuid.UUID]) -> None:
    await AuthorDAO.delete(session=session, id=id)
    return f"Автор с id {id} успешно удален"