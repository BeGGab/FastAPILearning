import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.service.author import (
    create_author_with_books,
    find_one_or_none_by_id,
    find_all_authors,
    update_author_with_books,
    delete_author,
)
from src.core.dependencies import RedisDep
from src.core.db import get_async_session
from src.client.bio_author_client import AuthorServiceClient, get_author_client


router = APIRouter(prefix="/api/v1/authors_books", tags=["author"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_author(
    payload: SAuthorCreate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
    author_client: AuthorServiceClient = Depends(get_author_client),
) -> SAuthorRead:
    return await create_author_with_books(
        session,
        payload,
        redis,
        author_client,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all(
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> List[SAuthorRead]:
    return await find_all_authors(session=session, redis=redis)


@router.get("/{author_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def find_author_is_id(
    author_id: uuid.UUID,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
    author_client: AuthorServiceClient = Depends(get_author_client),
) -> SAuthorRead:
    return await find_one_or_none_by_id(session, author_id, redis, author_client)


@router.put("/{author_id}", status_code=status.HTTP_201_CREATED)
async def update(
    author_id: uuid.UUID,
    payload: SAuthorUpdate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> SAuthorRead:
    return await update_author_with_books(
        session=session, author_id=author_id, author_data=payload, redis=redis
    )


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    author_id: uuid.UUID,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_author(session=session, author_id=author_id, redis=redis)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
