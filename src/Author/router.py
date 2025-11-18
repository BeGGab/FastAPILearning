import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union
from src.dao.schemas import SAuthorCreate, SAuthorRead
from src.dao.service import AuthorDAO

from src.db import get_async_session

router = APIRouter(tags=["author"])



@router.get("/authors")
async def find_all_authors(session: AsyncSession = Depends(get_async_session)) -> List[SAuthorRead]:
    authors = await AuthorDAO.find_all(session=session)
    return authors


@router.get("/authors/{id}")
async def find_author_is_id(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await AuthorDAO.find_one_or_none_by_id(session=session, id=id)
    return author


@router.post("/authors")
async def create_author(authoradd: SAuthorCreate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await AuthorDAO.create_author_with_books(session=session, author_data=authoradd.model_dump())
    return author


@router.delete("/authors/{id}")
async def delete_author(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)) -> Dict[str, str]:
    await AuthorDAO.delete(session=session, id=id)
    return {f'message': 'Автор успешно удален {id}'}