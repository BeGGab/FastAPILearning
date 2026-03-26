import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.courses import Course
from src.models.student import Student


def test_course_model_persists(db_session: Session) -> None:
    course = Course(title="Algorithms")
    db_session.add(course)
    db_session.commit()

    persisted = db_session.scalar(select(Course).where(Course.title == "Algorithms"))
    assert persisted is not None
    assert isinstance(persisted.id, uuid.UUID)


def test_course_model_links_students_many_to_many(db_session: Session) -> None:
    student = Student(name="Maria")
    course = Course(title="System Design")
    student.courses.append(course)

    db_session.add(student)
    db_session.commit()

    persisted_course = db_session.scalar(select(Course).where(Course.title == "System Design"))
    assert persisted_course is not None
    assert len(persisted_course.students) == 1
    assert persisted_course.students[0].name == "Maria"
