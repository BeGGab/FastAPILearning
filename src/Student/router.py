import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union
from sqlalchemy.orm import selectinload

from src.student.models import Student, Course
from src.student.schemas import SStudentCreate, SStudentRead, SCourseCreate, SCourseRead
from src.student.session import StudentDAO

from src.db import get_async_session


router = APIRouter(prefix="/student", tags=["student"])










@router.post("/add_student", status_code=status.HTTP_201_CREATED)
async def created_student(payload: SStudentCreate, session: AsyncSession = Depends(get_async_session)) -> SStudentRead:
    student = await StudentDAO.add_student(session=session, student_data=payload.model_dump())
    return student

@router.get("/respons_all")
async def get_all_students(session: AsyncSession = Depends(get_async_session)) -> List[SStudentRead]:
    students = await StudentDAO.find_all_students(session=session)
    return students


@router.get("/{id}")
async def get_student_by_id(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)) -> SStudentRead:
    student = await StudentDAO.find_one_with_id(session=session, id=id)
    return student


'''@router.put("/update/{id}")
async def update_student(id: Union[uuid.UUID],payload: SStudentCreate, session: AsyncSession = Depends(get_async_session)) -> SStudentRead:
    student = await StudentDAO.update_student_with_course(session=session, student_id=id, payload=payload.model_dump())
    return student'''


@router.put("/students/{student_id}", response_model=SStudentRead)
async def update_student(student_id: Union[uuid.UUID], payload: SStudentCreate, session: AsyncSession = Depends(get_async_session)) -> Student:
    student = await session.get(Student, student_id, options=(selectinload(Student.courses),))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = payload.name
   
    student.courses.clear()
    for c in payload.courses:
        student.courses.append(Course(title=c.title))

    await session.commit()
    await session.refresh(student)
    await session.refresh(student, attribute_names=["courses"])
    return student


@router.delete("/dell/{id}")
async def dell_student(id: Union[uuid.UUID], session: AsyncSession = Depends(get_async_session)):
    await StudentDAO.delete(session=session, id=id)
    return {f"message": "Студент с id {id} успешно удален"}

