import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from typing import List

from src.schemas.author import SAuthorCreate, SAuthorRead, SAuthorUpdate
from src.service.author import AuthorService

from src.core.dependencies import get_author_service

router = APIRouter(prefix="/api/v1/authors_books", tags=["author"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_author(
    payload: SAuthorCreate,
    author_service: AuthorService = Depends(get_author_service),
) -> SAuthorRead:
    return await author_service.create_author_with_books(
        author_data=payload,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def find_all(
    author_service: AuthorService = Depends(get_author_service),
) -> List[SAuthorRead]:
    return await author_service.find_all_authors()


@router.get("/{author_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def find_author_is_id(
    author_id: uuid.UUID,
    author_service: AuthorService = Depends(get_author_service),
) -> SAuthorRead:
    return await author_service.find_one_or_none_by_id(
        author_id=author_id,
    )


@router.put("/{author_id}", status_code=status.HTTP_201_CREATED)
async def update(
    author_id: uuid.UUID,
    payload: SAuthorUpdate,
    author_service: AuthorService = Depends(get_author_service),
) -> SAuthorRead:
    return await author_service.update_author_with_books(
        author_id=author_id, author_data=payload,
    )


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    author_id: uuid.UUID,
    author_service: AuthorService = Depends(get_author_service),
):
    await author_service.delete_author(author_id=author_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

