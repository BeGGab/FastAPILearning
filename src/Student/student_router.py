import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Union
from src.Student.schemas_student import SStudentCreate, SStudentRead, SCourseCreate, SCourseRead
from src.Student.session_student import StudentDAO
from src.Student.models import Student, Course, student_course
from src.db import get_async_session


srouter = APIRouter()

@srouter.get('/healthcheck')
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}