import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.author import Author
from src.models.books import Book


def test_book_model_persists_with_author_fk(db_session: Session) -> None:
    author = Author(name="Erich Gamma")
    db_session.add(author)
    db_session.flush()

    book = Book(title="Design Patterns", author_id=author.id)
    db_session.add(book)
    db_session.commit()

    persisted = db_session.scalar(select(Book).where(Book.title == "Design Patterns"))
    assert persisted is not None
    assert isinstance(persisted.id, uuid.UUID)
    assert persisted.author_id == author.id


def test_book_model_requires_author_fk(db_session: Session) -> None:
    book = Book(title="No Author Book", author_id=uuid.uuid4())
    db_session.add(book)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
