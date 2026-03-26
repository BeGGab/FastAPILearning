import uuid

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from src.core.db import Base
from src.models.profile import Profile
from src.models.user import User


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def _make_user_with_profile(username: str, email: str, phone: str) -> User:
    user = User(username=username, email=email)
    user.profile = Profile(
        first_name="Ivan",
        last_name="Ivanov",
        phone_number=phone,
        bio="Bio text",
    )
    return user


def test_user_model_persists_with_profile_relation(db_session: Session) -> None:
    user = _make_user_with_profile(
        username="user_one",
        email="user_one@example.com",
        phone="+79991230001",
    )

    db_session.add(user)
    db_session.commit()

    persisted = db_session.scalar(select(User).where(User.username == "user_one"))
    assert persisted is not None
    assert isinstance(persisted.id, uuid.UUID)
    assert persisted.profile is not None
    assert persisted.profile.phone_number == "+79991230001"


def test_user_model_unique_username_constraint(db_session: Session) -> None:
    user_1 = _make_user_with_profile(
        username="same_username",
        email="first@example.com",
        phone="+79991230002",
    )
    user_2 = _make_user_with_profile(
        username="same_username",
        email="second@example.com",
        phone="+79991230003",
    )

    db_session.add(user_1)
    db_session.commit()

    db_session.add(user_2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_model_delete_cascades_profile(db_session: Session) -> None:
    user = _make_user_with_profile(
        username="user_to_delete",
        email="delete@example.com",
        phone="+79991230004",
    )
    db_session.add(user)
    db_session.commit()

    profile_id = user.profile.id
    db_session.delete(user)
    db_session.commit()

    deleted_profile = db_session.scalar(select(Profile).where(Profile.id == profile_id))
    assert deleted_profile is None
