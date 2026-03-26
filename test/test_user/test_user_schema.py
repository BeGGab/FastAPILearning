import pytest

from src.exception.client_exception import NotFoundError, ValidationError
from src.schemas.user import SUserCreate, SUserUpdate


def test_user_create_valid_payload(valid_user_create_payload: dict) -> None:
    user = SUserCreate(**valid_user_create_payload)

    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.profile is not None
    assert user.profile.phone_number == "+79991234567"


def test_user_create_with_string_placeholder_username_raises() -> None:
    with pytest.raises(ValidationError):
        SUserCreate(
            username="string",
            email="test@example.com",
            profile={
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "phone_number": "+79991234567",
                "bio": "Bio",
            },
        )


def test_user_create_with_invalid_profile_phone_raises(
    valid_user_create_payload: dict,
) -> None:
    valid_user_create_payload["profile"]["phone_number"] = "89991234567"

    with pytest.raises(ValidationError):
        SUserCreate(**valid_user_create_payload)


def test_user_update_converts_int_username_to_string() -> None:
    user_update = SUserUpdate(username=123)

    assert user_update.username == "123"


def test_user_update_without_fields_raises_not_found_error() -> None:
    with pytest.raises(NotFoundError):
        SUserUpdate()
