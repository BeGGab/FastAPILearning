import uuid
from typing import List
from sqlalchemy import select, update, delete, event, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.models import (User, Profile, Author, Book, Student, Course, student_course)
from src.dao.base import BaseDAO




class UserDAO(BaseDAO):
    model = User

    
    @classmethod
    async def create_user_with_profile(cls, session: AsyncSession, user_data: dict) -> User:        
        profile_data = user_data.pop("profile")
        user = User(
            **user_data,
            profile=Profile(**profile_data)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user, ["profile"])
        return user

    @classmethod
    async def find_one_or_none_with_profile(cls, session: AsyncSession, **filter_by) -> User | None:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.profile))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def find_all_with_profiles(cls, session: AsyncSession, **filter_by) -> list[User]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.profile))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())
    
    @classmethod
    async def update_user(cls, session: AsyncSession, user_id: uuid.UUID, **Values) -> User:
        profile_data = Values.pop("profile", None)

        user_update_query = (
            update(cls.model)
            .where(cls.model.id == user_id)
            .values(**Values)
            .execution_options(synchronize_session="fetch")
        )
        if profile_data:
            profile_update_query = (
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(**profile_data)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(profile_update_query)

        await session.execute(user_update_query)
        await session.commit()

        updated_user = await cls.find_one_or_none_with_profile(session=session, id=user_id)
        return updated_user
    
    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: uuid.UUID):
        user = await cls.find_one_or_none_with_profile(session, id=user_id)
        if not user:
            return None
        
        await session.delete(user)
        await session.commit()
        return user





class StudentDAO(BaseDAO):
    model = Student



    @classmethod
    async def add_student(cls, session: AsyncSession, student_data: dict) -> Student:
        course_data = student_data.pop("courses", [])
        student = Student(**student_data)
        if course_data:
            student.courses = [Course(**course) for course in course_data]
        session.add(student)
        await session.commit()
        await session.refresh(student, ["courses"])
        return student
    
    @classmethod
    async def find_all_students(cls, session: AsyncSession, **filter_by) -> List[Student]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.courses))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())
    

    @classmethod
    async def find_one_with_id(cls, session: AsyncSession, id: uuid.UUID) -> Student:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.courses))
            .filter_by(id=id)
        )
        result = await session.execute(query)
        return result.unique().scalar()
    

    @classmethod
    async def update_student_with_course(cls, session: AsyncSession, student_id: uuid.UUID, **values) -> Student:
        course_data = values.pop("courses", None or [])

        student = await session.get(Student, student_id, options=(selectinload(Student.courses),))
        if not student:
            raise ValueError(f"Студент с id {student_id} не найден")

        student.name = values.get("name", student.name)

        student.courses.clear()
        if course_data:
            student.courses.extend([Course(**course) for course in course_data])

        await session.commit()
        await session.refresh(student, attribute_names=["courses"])
        return student
    



class AuthorDAO(BaseDAO):
    model = Author
    
    @classmethod
    async def create_author_with_books(cls, session: AsyncSession, author_data: dict) -> Author:
        books_data = author_data.pop("books")
        author = Author(**author_data, books=[Book(**book) for book in books_data])
        session.add(author)
        await session.commit()
        await session.refresh(author, ["books"])
        return author
    
    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, **filter_by) -> Author:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.books))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return result.unique().scalar()
    
    @classmethod
    async def find_all_authors(cls, session: AsyncSession, **filter_by) -> list[Author]:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.books))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())