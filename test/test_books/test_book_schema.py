from src.schemas.book import SBookCreate


def test_book_create_to_orm_model() -> None:
    book = SBookCreate(title="Test Book")
    orm_book = book.to_orm_model()
    assert orm_book.title == "Test Book"
