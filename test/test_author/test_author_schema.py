import pytest

from src.exception.client_exception import NotFoundError, ValidationError
from src.schemas.author import SAuthorCreate, SAuthorUpdate


def test_author_create_valid_payload() -> None:
    payload = {
        "name": "Author Name",
        "books": [{"title": "Book Title"}],
    }
    author = SAuthorCreate(**payload)
    assert author.name == "Author Name"
    assert len(author.books) == 1


def test_author_create_invalid_name_raises() -> None:
    with pytest.raises(ValidationError):
        SAuthorCreate(name="string", books=[])


def test_author_update_without_fields_raises() -> None:
    with pytest.raises(NotFoundError):
        SAuthorUpdate()
