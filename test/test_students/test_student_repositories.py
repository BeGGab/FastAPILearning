import uuid
from datetime import date

from src.repositories.students import StudentRepository
from src.schemas.courses import SCourseRead
from src.schemas.student import SStudentRead


def _student_read() -> SStudentRead:
    return SStudentRead(
        id=uuid.uuid4(),
        name="Student",
        courses=[SCourseRead(id=uuid.uuid4(), title="Python")],
        email=None,
        phone_number=None,
        bio_text=None,
        year_of_enrollment=None,
        year_of_graduation=None,
    )


def test_apply_bio_data_to_student_updates_fields() -> None:
    repo = StudentRepository(session=None)
    student_data = _student_read()
    bio_data = {
        "email": "student@example.com",
        "phone_number": "+79991234567",
        "text": "Student bio",
        "year_of_enrollment": date(2019, 9, 1),
        "year_of_graduation": date(2023, 6, 30),
    }

    result = repo.apply_bio_data_to_student(student_data, bio_data)

    assert result.email == "student@example.com"
    assert result.phone_number == "+79991234567"
    assert result.bio_text == "Student bio"
    assert result.year_of_enrollment == date(2019, 9, 1)
    assert result.year_of_graduation == date(2023, 6, 30)


def test_apply_bio_data_to_student_none_keeps_original() -> None:
    repo = StudentRepository(session=None)
    student_data = _student_read()
    result = repo.apply_bio_data_to_student(student_data, None)
    assert result == student_data
