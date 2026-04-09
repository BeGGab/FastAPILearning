import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.service.author import AuthorService

from src.core.redis import RedisDep
from src.core.db import get_async_session
from src.client.bio_author_client import AuthorClientDep


router = APIRouter(prefix="/api/v1/authors_books", tags=["author"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_author(
    payload: SAuthorCreate,
    redis: RedisDep,
    author_client: AuthorClientDep,
    session: AsyncSession = Depends(get_async_session),
) -> SAuthorRead:
    return await AuthorService(session, redis).create_author_with_books(
        author_client=author_client,
        author_data=payload,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all(
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> List[SAuthorRead]:
    return await AuthorService(session, redis).find_all_authors()


@router.get("/{author_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def find_author_is_id(
    author_id: uuid.UUID,
    redis: RedisDep,
    author_client: AuthorClientDep,
    session: AsyncSession = Depends(get_async_session),
) -> SAuthorRead:
    return await AuthorService(session, redis).find_one_or_none_by_id(
        author_id=author_id,
        author_client=author_client,
    )


@router.put("/{author_id}", status_code=status.HTTP_201_CREATED)
async def update(
    author_id: uuid.UUID,
    payload: SAuthorUpdate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> SAuthorRead:
    return await AuthorService(session, redis).update_author_with_books(
        author_id=author_id, author_data=payload,
    )


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    author_id: uuid.UUID,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
):
    await AuthorService(session, redis).delete_author(author_id=author_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

