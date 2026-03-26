import uuid
from datetime import date

from src.repositories.user import UserRepository
from src.schemas.profile import SProfileRead
from src.schemas.user import SUserRead


def _user_read() -> SUserRead:
    return SUserRead(
        id=uuid.uuid4(),
        username="u1",
        email="u1@example.com",
        profile=SProfileRead(
            id=uuid.uuid4(),
            first_name="Ivan",
            last_name="Ivanov",
            phone_number="+79991234567",
            bio="Profile bio",
        ),
        bio_text=None,
        year_of_birth=None,
    )


def test_apply_bio_data_to_user_updates_fields() -> None:
    repo = UserRepository(session=None)
    user_data = _user_read()
    bio_data = {"text": "External bio", "year_of_birth": date(1997, 1, 1)}

    result = repo.apply_bio_data_to_user(user_data, bio_data)

    assert result.bio_text == "External bio"
    assert result.year_of_birth == date(1997, 1, 1)


def test_apply_bio_data_to_user_none_keeps_original() -> None:
    repo = UserRepository(session=None)
    user_data = _user_read()

    result = repo.apply_bio_data_to_user(user_data, None)

    assert result == user_data
