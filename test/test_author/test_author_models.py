import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.author import Author
from src.models.books import Book


def _make_author_with_books(name: str) -> Author:
    author = Author(name=name)
    author.books = [
        Book(title="Domain-Driven Design"),
        Book(title="Clean Architecture"),
    ]
    return author


def test_author_model_persists_with_books(db_session: Session) -> None:
    author = _make_author_with_books("Robert Martin")
    db_session.add(author)
    db_session.commit()

    persisted = db_session.scalar(select(Author).where(Author.name == "Robert Martin"))
    assert persisted is not None
    assert isinstance(persisted.id, uuid.UUID)
    assert len(persisted.books) == 2


def test_author_delete_cascades_books(db_session: Session) -> None:
    author = _make_author_with_books("Martin Fowler")
    db_session.add(author)
    db_session.commit()

    book_ids = [book.id for book in author.books]
    db_session.delete(author)
    db_session.commit()

    deleted_books = db_session.scalars(select(Book).where(Book.id.in_(book_ids))).all()
    assert deleted_books == []
