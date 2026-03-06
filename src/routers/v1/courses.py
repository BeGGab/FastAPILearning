import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.courses import SCourseCreate, SCourseRead
from src.service.courses import (
    create_new_courses,
    find_all_courses,
    find_existing_courses,
    update_courses,
    delete_courses,
)

from src.core.db import get_async_session


router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_courses(
    session: AsyncSession = Depends(get_async_session),
) -> List[SCourseRead]:
    return await find_all_courses(session=session)


@router.get("/{id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_course_by_id(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SCourseRead:
    return await find_existing_courses(session=session, course_titles=[id])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_courses(
    payload: List[SCourseCreate], session: AsyncSession = Depends(get_async_session)
) -> List[SCourseRead]:
    return await create_new_courses(session=session, new_course_data=payload)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    session: AsyncSession = Depends(get_async_session), name: str = None
):
    await delete_courses(session=session, name=name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
