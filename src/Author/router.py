import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union
from src.author.schemas import SAuthorCreate, SAuthorRead
from src.author.session import AuthorDAO
from src.author.models import Author, Book
from src.db import get_async_session

router = APIRouter(prefix="/author", tags=["author"])



@router.get("/find_all")
async def find_all_authors(session: AsyncSession = Depends(get_async_session)) -> List[SAuthorRead]:
    authors = await AuthorDAO.find_all(session=session)
    return authors


@router.get("/{id}")
async def find_author_is_id(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await AuthorDAO.find_one_or_none_by_id(session=session, id=id)
    return author


@router.post("/created_author", status_code=status.HTTP_201_CREATED)
async def create_author(authoradd: SAuthorCreate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await AuthorDAO.create_author_with_books(session=session, author_data=authoradd.model_dump())
    return author


@router.delete("/dell/{id}")
async def delete_author(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)) -> Dict[str, str]:
    await AuthorDAO.delete(session=session, id=id)
    return {"message": f"Автор с id {id} успешно удален"}