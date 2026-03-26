import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.courses import Course
from src.models.student import Student


def _make_student_with_courses(name: str) -> Student:
    student = Student(name=name)
    student.courses = [
        Course(title="Python"),
        Course(title="Databases"),
    ]
    return student


def test_student_model_persists_with_courses(db_session: Session) -> None:
    student = _make_student_with_courses("Alex")
    db_session.add(student)
    db_session.commit()

    persisted = db_session.scalar(select(Student).where(Student.name == "Alex"))
    assert persisted is not None
    assert isinstance(persisted.id, uuid.UUID)
    assert len(persisted.courses) == 2


def test_student_course_many_to_many_rows_created(db_session: Session) -> None:
    student = _make_student_with_courses("Nina")
    db_session.add(student)
    db_session.commit()

    persisted = db_session.scalar(select(Student).where(Student.name == "Nina"))
    assert persisted is not None
    titles = sorted(course.title for course in persisted.courses)
    assert titles == ["Databases", "Python"]
