import uuid

from src.repositories.author import AuthorRepository
from src.schemas.author import SAuthorRead
from src.schemas.book import SBookRead


def _author_read() -> SAuthorRead:
    return SAuthorRead(
        id=uuid.uuid4(),
        name="Author",
        books=[SBookRead(id=uuid.uuid4(), title="Book")],
        biography_text=None,
        year_of_birth=None,
        year_of_death=None,
    )


def test_apply_biography_to_author_data_updates_fields() -> None:
    repo = AuthorRepository(session=None)
    author_data = _author_read()
    bio_data = {"text": "Author bio", "year_of_birth": 1970, "year_of_death": 2020}

    result = repo.apply_biography_to_author_data(author_data, bio_data)

    assert result.biography_text == "Author bio"
    assert result.year_of_birth == 1970
    assert result.year_of_death == 2020


def test_apply_biography_to_author_data_none_keeps_original() -> None:
    repo = AuthorRepository(session=None)
    author_data = _author_read()
    result = repo.apply_biography_to_author_data(author_data, None)
    assert result == author_data
