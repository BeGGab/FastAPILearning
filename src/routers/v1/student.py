import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.enums import Status
from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate

from src.service.student import StudentService

from src.core.db import get_async_session
from src.core.redis import RedisDep

router = APIRouter(prefix="/api/v1/students_courses", tags=["student"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_student(
    payload: SStudentCreate,
    redis: RedisDep, 
    session: AsyncSession = Depends(get_async_session), 
) -> SStudentRead:
    return await StudentService(session, redis).add_student(
        student_data=payload,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_students(
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
) -> List[SStudentRead]:
    return await StudentService(session, redis).find_all_students(skip=0, limit=100)


@router.get("/{student_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_student_by_id(
    student_id: uuid.UUID, 
    redis: RedisDep, 
    session: AsyncSession = Depends(get_async_session),
) -> SStudentRead:
    return await StudentService(session, redis).find_one_with_id(
        student_id=student_id,
    )


@router.put("/{student_id}", status_code=status.HTTP_201_CREATED)
async def update_student(
    student_id: uuid.UUID, 
    payload: SStudentUpdate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_async_session),
) -> SStudentRead:
    return await StudentService(session, redis).update_student_with_course(
        student_id=student_id,
        student_data=payload,
    )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_students(
    student_id: uuid.UUID, 
    redis: RedisDep, 
    session: AsyncSession = Depends(get_async_session)
):
    await StudentService(session, redis).delete_student(student_id=student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
