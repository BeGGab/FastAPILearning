import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from sqlalchemy.orm import selectinload

from src.schemas.student_schemas import SStudentCreate, SStudentRead
from src.service.student_service import StudentDAO

from src.core.db import get_async_session


router = APIRouter(tags=["student"])


@router.post("/students")
async def created_student(
    payload: SStudentCreate, session: AsyncSession = Depends(get_async_session)
) -> SStudentRead:
    student = await StudentDAO.add_student(session=session, student_data=payload.model_dump())
    return student


@router.get("/students")
async def get_all_students(
    session: AsyncSession = Depends(get_async_session),
) -> List[SStudentRead]:
    students = await StudentDAO.find_all_students(session=session)
    return students


@router.get("/students/{id}")
async def get_student_by_id(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SStudentRead:
    student = await StudentDAO.find_one_with_id(session=session, id=id)
    return student


@router.put("/students/{student_id}")
async def update_student(
    student_id: uuid.UUID,
    payload: SStudentCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SStudentRead:
    student = await StudentDAO.update_student_with_course(
        session=session, student_id=student_id, student_data=payload
    )
    return student


@router.delete("/students/{id}")
async def dell_student(
    id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    student = await StudentDAO.delete(session=session, id=id)
    return {"message": f"Студент удален с id: {id} "}
