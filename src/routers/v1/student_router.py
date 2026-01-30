import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.enums import Status
from src.schemas.student_schemas import SStudentCreate, SStudentRead, SStudentUpdate
from src.service.student_service import (
    add_student,
    find_all_students,
    find_one_with_id,
    update_student_with_course,
    delete_student,
)

from src.core.db import get_async_session


router = APIRouter(prefix="/api/v1/students_courses", tags=["student"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_student(
    payload: SStudentCreate, session: AsyncSession = Depends(get_async_session)
) -> SStudentRead:
    return await add_student(session=session, student_data=payload)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_students(session: AsyncSession = Depends(get_async_session),) -> List[SStudentRead]:
    return await find_all_students(session=session)


@router.get("/{id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_student_by_id(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SStudentRead:
    return await find_one_with_id(session=session, student_id=id)


@router.put("/{id}", status_code=status.HTTP_201_CREATED)
async def update_student(
    id: uuid.UUID,
    payload: SStudentUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> SStudentRead:
    return await update_student_with_course(
        session=session, student_id=id, student_data=payload
    )


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_students(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    await delete_student(session=session, student_id=id)
    return Status.DELETED
    
