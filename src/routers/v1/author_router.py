import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union

from src.core.enums import Status
from src.schemas.author_schemas import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.service.author_service import (create_author_with_books, 
                                        find_one_or_none_by_id, 
                                        find_all_authors, 
                                        update_author_with_books, 
                                        delete_author)

from src.core.db import get_async_session

router = APIRouter(
    prefix="/api/v1/authors_books",
    tags=["author"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_author(payload: SAuthorCreate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    return await create_author_with_books(session=session, data=payload)


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all(session: AsyncSession = Depends(get_async_session)) -> List[SAuthorRead]:
    return await find_all_authors(session=session)
    


@router.get("/{id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def find_author_is_id(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    return await find_one_or_none_by_id(session=session, id=id)



@router.put("/{id}", status_code=status.HTTP_201_CREATED)
async def update(id: uuid.UUID, payload: SAuthorUpdate, session: AsyncSession = Depends(get_async_session)) -> SAuthorRead:
    return await update_author_with_books(session=session, author_id=id, author_data=payload)
    

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    await delete_author(session=session, author_id=id)
    return Status.DELETED