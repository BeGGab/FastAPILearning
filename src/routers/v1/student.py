import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.enums import Status
from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate
from src.service.student import (
    add_student,
    find_all_students,
    find_one_with_id,
    update_student_with_course,
    delete_student,
)
from src.client.bio_student_client import StudentServiceClient, get_student_client

from src.core.db import get_async_session
from src.core.dependencies import RedisDep

router = APIRouter(prefix="/api/v1/students_courses", tags=["student"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_student(
    payload: SStudentCreate,
    redis: RedisDep, 
    session: AsyncSession = Depends(get_async_session), 
    student_client: StudentServiceClient = Depends(get_student_client)
) -> SStudentRead:
    return await add_student(
        session=session,
        redis=redis,
        student_data=payload,
        student_client=student_client,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_students(
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
) -> List[SStudentRead]:
    return await find_all_students(session, redis, skip=0, limit=100)


@router.get("/{student_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_student_by_id(
    student_id: uuid.UUID, redis: RedisDep, session: AsyncSession = Depends(get_async_session), student_client: StudentServiceClient = Depends(get_student_client)
) -> SStudentRead:
    return await find_one_with_id(
        session=session,
        redis=redis,
        student_id=student_id,
        student_client=student_client,
    )


@router.put("/{student_id}", status_code=status.HTTP_201_CREATED)
async def update_student(
    student_id: uuid.UUID, 
    payload: SStudentUpdate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> SStudentRead:
    return await update_student_with_course(
        session,
        redis,
        student_id,
        payload,
    )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_students(
    student_id: uuid.UUID, 
    redis: RedisDep, 
    session: AsyncSession = Depends(get_async_session)
):
    await delete_student(session=session, redis=redis, student_id=student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
