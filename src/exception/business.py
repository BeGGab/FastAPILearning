from src.exception.client_exception import (
    NotFoundError,
    ConflictError,
    )

from typing import Any


class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: Any = None, detail: str = None, **kwargs):
        detail = detail or f"Пользователь с ID: {user_id} не найден"
        super().__init__(detail=detail,
                         error_code="user_not_found",
                         context={"resource": "Пользователь", "resource_id": user_id},
                         **kwargs)


class UserConflictError(ConflictError):
    def __init__(self, detail: str = "Такой Пользователь уже существует", **kwargs):
        super().__init__(detail=detail, error_code="user_conflict", **kwargs)


class StudentNotFoundError(NotFoundError):
    def __init__(self, student_id: Any = None, detail: str = None, **kwargs):
        detail = detail or f"Студент с ID: {student_id} не найден"
        super().__init__(detail=detail,
                         error_code="student_not_found",
                         context={"resource": "Студент", "resource_id": student_id},
                         **kwargs)


class StudentConflictError(ConflictError):
    def __init__(self, detail: str = "Такой Студент уже существует", **kwargs):
        super().__init__(detail=detail, error_code="student_conflict", **kwargs)


class AuthorNotFoundError(NotFoundError):
    def __init__(self, author_id: Any = None, detail: str = None, **kwargs):
        detail = detail or f"Автор с ID: {author_id} не найден"
        super().__init__(detail=detail,
                         error_code="author_not_found",
                         context={"resource": "Автор", "resource_id": author_id},
                         **kwargs)


class AuthorConflictError(ConflictError):
    def __init__(self, detail: str = "Такой Автор уже существует", **kwargs):
        super().__init__(detail=detail, error_code="author_conflict", **kwargs)


class CourseNotFoundError(NotFoundError):
    def __init__(self, course_id: Any = None, detail: str = None, **kwargs):
        detail = detail or f"Курс с ID: {course_id} не найден"
        super().__init__(detail=detail,
                         error_code="course_not_found",
                         context={"resource": "Курс", "resource_id": course_id}, **kwargs)


class CourseConflictError(ConflictError):
    def __init__(self, detail: str = "Такой Курс уже существует", **kwargs):
        super().__init__(detail=detail, error_code="course_conflict", **kwargs)


class BookNotFoundError(NotFoundError):
    def __init__(self, detail: str = "Книга не найдена", **kwargs):
        super().__init__(detail=detail, error_code="book_not_found", **kwargs)


class BookConflictError(ConflictError):
    def __init__(self, detail: str = "Такая Книга уже существует", **kwargs):
        super().__init__(detail=detail, error_code="book_conflict", **kwargs)


class ProfileNotFoundError(NotFoundError):
    def __init__(self, profile_id: Any = None, detail: str = None, **kwargs):
        detail = detail or f"Профиль с ID: {profile_id} не найден"
        super().__init__(detail=detail,
                         error_code="profile_not_found",
                         context={"resource": "Профиль", "resource_id": profile_id},
                         **kwargs)


class ProfileConflictError(ConflictError):
    def __init__(self, detail: str = "Такой Профиль уже существует", **kwargs):
        super().__init__(detail=detail, error_code="profile_conflict", **kwargs)
