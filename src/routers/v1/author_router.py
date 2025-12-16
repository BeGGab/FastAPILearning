import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union

from src.core.enums import Status
from src.schemas.author_schemas import SAuthorCreate, SAuthorRead
from src.service.author_service import (create_author_with_books, 
                                        find_one_or_none_by_id, 
                                        find_all_authors, 
                                        update_author_with_books, 
                                        delete_author)

from src.core.db import get_async_session

router = APIRouter(tags=["author"])




@router.post("/authors")
async def create_author(payload: SAuthorCreate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await create_author_with_books(session=session, data=payload)
    return author


@router.get("/authors")
async def find_all(session: AsyncSession = Depends(get_async_session)) -> List[SAuthorRead]:
    authors = await find_all_authors(session=session)
    return authors


@router.get("/authors/{id}")
async def find_author_is_id(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    author = await find_one_or_none_by_id(session=session, id=id)
    return author


@router.put("/authors/{id}")
async def update(id: uuid.UUID, payload: SAuthorCreate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    return await update_author_with_books(session=session, author_id=id, author_data=payload)
    

@router.delete("/authors/{id}")
async def delete(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    author = await delete_author(session=session, author_id=id)
    return Status.DELETED