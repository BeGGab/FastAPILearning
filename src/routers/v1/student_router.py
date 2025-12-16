import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from sqlalchemy.orm import selectinload

from src.core.enums import Status
from src.schemas.student_schemas import SStudentCreate, SStudentRead
from src.service.student_service import (
    add_student,
    find_all_students,
    find_one_with_id,
    update_student_with_course,
    delete_student,
)


from src.core.db import get_async_session


router = APIRouter(tags=["student"])


@router.post("/students")
async def created_student(
    payload: SStudentCreate, session: AsyncSession = Depends(get_async_session)
) -> SStudentRead:
    student = await add_student(session=session, student_data=payload)
    return student


@router.get("/students")
async def get_all_students(
    session: AsyncSession = Depends(get_async_session),
) -> List[SStudentRead]:
    students = await find_all_students(session=session)
    return students


@router.get("/students/{id}")
async def get_student_by_id(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SStudentRead:
    student = await find_one_with_id(session=session, id=id)
    return student


@router.put("/students/{student_id}")
async def update_student(
    student_id: uuid.UUID,
    payload: SStudentCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SStudentRead:
    student = await update_student_with_course(
        session=session, student_id=student_id, student_data=payload
    )
    return student


@router.delete("/students/{id}")
async def delete_students(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    student = await delete_student(session=session, student_id=id)
    return Status.DELETED



