from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from src.dao.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from src.Student.models import Student, Course, student_course






class StudentDAO(BaseDAO):
    model = Student
