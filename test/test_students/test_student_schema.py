import pytest

from src.exception.client_exception import NotFoundError, ValidationError
from src.schemas.student import SStudentCreate, SStudentUpdate


def test_student_create_valid_payload() -> None:
    payload = {
        "name": "Student Name",
        "courses": [{"title": "Python"}],
    }
    student = SStudentCreate(**payload)
    assert student.name == "Student Name"
    assert len(student.courses) == 1


def test_student_create_invalid_name_raises() -> None:
    with pytest.raises(ValidationError):
        SStudentCreate(name="string", courses=[])


def test_student_update_without_fields_raises() -> None:
    with pytest.raises(NotFoundError):
        SStudentUpdate()
