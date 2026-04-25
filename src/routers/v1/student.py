import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.schemas.student import SStudentCreate, SStudentRead, SStudentUpdate

from src.service.student import StudentService

from src.core.dependencies import get_student_service

router = APIRouter(prefix="/api/v1/students_courses", tags=["student"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def created_student(
    payload: SStudentCreate,
    student_service: StudentService = Depends(get_student_service),
) -> SStudentRead:
    return await student_service.add_student(
        student_data=payload,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_students(
    student_service: StudentService = Depends(get_student_service),
    skip: int = 0,
    limit: int = 100,
) -> List[SStudentRead]:
    return await student_service.find_all_students(skip=skip, limit=limit)


@router.get("/{student_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def get_student_by_id(
    student_id: uuid.UUID, 
    student_service: StudentService = Depends(get_student_service)
) -> SStudentRead:
    return await student_service.find_one_with_id(
        student_id=student_id,
    )


@router.put("/{student_id}", status_code=status.HTTP_201_CREATED)
async def update_student(
    student_id: uuid.UUID, 
    payload: SStudentUpdate,
    student_service: StudentService = Depends(get_student_service),
) -> SStudentRead:
    return await student_service.update_student_with_course(
        student_id=student_id,
        student_data=payload,
    )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_students(
    student_id: uuid.UUID, 
    student_service: StudentService = Depends(get_student_service),
):
    await student_service.delete_student(student_id=student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
