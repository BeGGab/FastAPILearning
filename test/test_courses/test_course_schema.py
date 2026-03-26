import pytest

from src.exception.client_exception import ValidationError
from src.schemas.courses import SCourseCreate


def test_course_create_valid_payload() -> None:
    course = SCourseCreate(title="FastAPI")
    assert course.title == "FastAPI"
    assert course.to_orm_model().title == "FastAPI"


def test_course_create_empty_title_raises() -> None:
    with pytest.raises(ValidationError):
        SCourseCreate(title="   ")
