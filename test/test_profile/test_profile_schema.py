import pytest

from src.exception.client_exception import ValidationError
from src.schemas.profile import SProfileCreate, SProfileUpdate


def test_profile_create_valid_phone() -> None:
    profile = SProfileCreate(
        first_name="Ivan",
        last_name="Ivanov",
        phone_number="+79991234567",
        bio="Bio",
    )
    assert profile.phone_number == "+79991234567"


def test_profile_create_invalid_phone_raises() -> None:
    with pytest.raises(ValidationError):
        SProfileCreate(
            first_name="Ivan",
            last_name="Ivanov",
            phone_number="89991234567",
            bio="Bio",
        )


def test_profile_update_accepts_none_phone() -> None:
    profile = SProfileUpdate(phone_number=None)
    assert profile.phone_number is None
