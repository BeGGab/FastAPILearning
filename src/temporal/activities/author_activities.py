import logging
import uuid
from temporalio import activity

from src.core.db import async_session_maker
from src.repositories.author import AuthorRepository
from src.schemas.author import SAuthorCreate
from src.schemas.book import SBookCreate
from src.temporal.models import CreateAuthorSagaInput, DeleteAuthorInput
from src.temporal.saga_redis import (
    default_saga_ttl_s,
    saga_get_json,
    saga_mark_done,
    saga_release,
    saga_try_lock,
)

logger = logging.getLogger(__name__)

_SAGA_KIND_AUTHOR = "author"


@activity.defn(name="create_author_activity")
async def create_author_activity(payload: CreateAuthorSagaInput) -> str:
    ttl_s = default_saga_ttl_s()
    rid = payload.request_id

    state = await saga_get_json(_SAGA_KIND_AUTHOR, rid)
    if state and state.get("status") == "done":
        aid = state.get("author_id")
        if aid:
            logger.info(
                "create_author_activity: идемпотентный кэш hit request_id=%s author_id=%s",
                rid,
                aid,
            )
            return aid

    acquired = await saga_try_lock(_SAGA_KIND_AUTHOR, rid, ttl_s)
    if not acquired:
        state = await saga_get_json(_SAGA_KIND_AUTHOR, rid)
        if state and state.get("status") == "done" and state.get("author_id"):
            return state["author_id"]
        raise RuntimeError(
            f"saga author lock busy для request_id={rid}; повторить activity"
        )

    books = [SBookCreate(title=b.title) for b in payload.books]

    author_data = SAuthorCreate(
        name=payload.name,
        books=books,
        biography_text=payload.biography_text,
        year_of_birth=payload.year_of_birth,
        year_of_death=payload.year_of_death,
    )

    try:
        async with async_session_maker() as session:
            repository = AuthorRepository(session)
            author, _books = await repository.created(author_data=author_data)
            session.add(author)
            await session.flush()
            await session.refresh(author, ["books"])
            author_id = str(author.id)
            await session.commit()
    except Exception:
        await saga_release(_SAGA_KIND_AUTHOR, rid)
        raise

    await saga_mark_done(_SAGA_KIND_AUTHOR, rid, author_id, ttl_s)
    return author_id


@activity.defn(name="delete_author_activity")
async def delete_author_activity(inp: DeleteAuthorInput) -> None:
    await saga_release(_SAGA_KIND_AUTHOR, inp.request_id)

    async with async_session_maker() as session:
        repository = AuthorRepository(session)
        author = await repository.get_id(id=uuid.UUID(inp.author_id))
        if not author:
            return
        await session.delete(author)
        await session.commit()
