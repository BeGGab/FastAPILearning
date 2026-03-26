import copy
import uuid
from datetime import date

import pytest


@pytest.fixture
def valid_profile_payload() -> dict:
    return {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "phone_number": "+79991234567",
        "bio": "Backend developer",
    }


@pytest.fixture
def valid_user_create_payload(valid_profile_payload: dict) -> dict:
    return {
        "username": "test_user",
        "email": "test@example.com",
        "profile": copy.deepcopy(valid_profile_payload),
    }


@pytest.fixture
def valid_user_update_payload() -> dict:
    return {
        "username": "updated_user",
        "email": "updated@example.com",
    }


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def cached_user_payload(user_id: uuid.UUID) -> dict:
    return {
        "id": str(user_id),
        "username": "cached_user",
        "email": "cached@example.com",
        "profile": {
            "id": str(uuid.uuid4()),
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "phone_number": "+79991234567",
            "bio": "Local profile",
        },
        "bio_text": None,
        "year_of_birth": None,
    }


@pytest.fixture
def bio_user_payload() -> dict:
    return {
        "text": "Bio from external service",
        "year_of_birth": date(1998, 5, 17),
    }
