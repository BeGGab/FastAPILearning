import uuid

import pytest

from src.routers.v1 import user as user_router
from src.schemas.profile import SProfileCreate
from src.schemas.profile import SProfileRead
from src.schemas.user import SUserCreate, SUserRead


@pytest.mark.asyncio
async def test_add_user_with_profile_calls_service(monkeypatch) -> None:
    user_id = uuid.uuid4()
    expected = SUserRead(
        id=user_id,
        username="user_one",
        email="u1@example.com",
        profile=SProfileRead(
            id=uuid.uuid4(),
            first_name="Ivan",
            last_name="Ivanov",
            phone_number="+79991234567",
            bio="Bio",
        ),
        bio_text=None,
        year_of_birth=None,
    )

    async def _fake_create(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(user_router, "create_user_with_profile", _fake_create)

    payload = SUserCreate(
        username="user_one",
        email="u1@example.com",
        profile=SProfileCreate(
            first_name="Ivan",
            last_name="Ivanov",
            phone_number="+79991234567",
            bio="Bio",
        ),
    )

    result = await user_router.add_user_with_profile(
        payload=payload,
        redis=object(),
        session=object(),
        user_client=object(),
    )

    assert result.id == user_id
