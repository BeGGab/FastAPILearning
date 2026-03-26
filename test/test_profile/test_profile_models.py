import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.profile import Profile
from src.models.user import User


def _make_user_with_profile(
    username: str,
    email: str,
    phone_number: str,
) -> User:
    user = User(username=username, email=email)
    user.profile = Profile(
        first_name="Petr",
        last_name="Petrov",
        phone_number=phone_number,
        bio="Bio",
    )
    return user


def test_profile_model_persists_and_links_to_user(db_session: Session) -> None:
    user = _make_user_with_profile(
        username="profile_owner",
        email="profile_owner@example.com",
        phone_number="+79991231111",
    )
    db_session.add(user)
    db_session.commit()

    persisted = db_session.scalar(select(Profile).where(Profile.phone_number == "+79991231111"))
    assert persisted is not None
    assert isinstance(persisted.id, uuid.UUID)
    assert persisted.user is not None
    assert persisted.user.username == "profile_owner"


def test_profile_phone_is_unique(db_session: Session) -> None:
    user_1 = _make_user_with_profile(
        username="u_profile_1",
        email="u_profile_1@example.com",
        phone_number="+79991232222",
    )
    user_2 = _make_user_with_profile(
        username="u_profile_2",
        email="u_profile_2@example.com",
        phone_number="+79991232222",
    )

    db_session.add(user_1)
    db_session.commit()

    db_session.add(user_2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
