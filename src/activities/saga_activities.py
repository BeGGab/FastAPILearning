import logging
from enum import Enum
from temporalio import activity


from src.schemas.saga import (
    CompensationResult,
    CreateAuthorSagaInput,
    CreateAuthorSagaResult,
    CreateBiographyInput,
    DeleteAuthorInput,
    DeleteBiographyInput,
)

from src.activities.author_activities import create_author, delete_author
from src.activities.biography_activities import create_biography, delete_biography

logger = logging.getLogger(__name__)


class SagaActivityResult(Enum):
    CREATE_AUTHOR = "create_author"
    CREATE_BIOGRAPHY = "create_biography"



def _has_bio(payload: CreateAuthorSagaInput) -> bool:
    return (
        payload.biography_text is not None
        and payload.year_of_birth is not None
        and payload.year_of_death is not None
    )



@activity.defn(name="create_author_saga_activity")
async def create_author_saga_activity(payload: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
    author_id: str | None = None
    biography_created = False
    has_bio = _has_bio(payload)

    compensated_author = CompensationResult(attempted=False, success=False, details=None)
    compensated_biography = CompensationResult(attempted=False, success=False, details=None)

    try:
        author_id = await create_author(payload)

    except Exception as e:
        logger.error("Ошибка саги создания автора: %s", e)
        raise RuntimeError(f"Ошибка создания автора: {e}") from e

    
    if has_bio:
        try:
            bio_input = CreateBiographyInput(
                request_id=payload.request_id,
                author_id=author_id,
                author_name=payload.name,
                biography_text=payload.biography_text,
                year_of_birth=payload.year_of_birth,
                year_of_death=payload.year_of_death,
            )
            await create_biography(bio_input)
            biography_created = True
        except Exception as e:
            compensated_author, compensated_biography = await _compensate(
                author_id=author_id,
                request_id=payload.request_id,
                biography_created=False,
            )
            raise RuntimeError(
                f"Ошибка Саги {payload.request_id}"
                f"author_id={author_id}"
                f"bio_comp={compensated_biography}"
                f"author_comp={compensated_author}"
                f"error={e}"
            ) from e

    return CreateAuthorSagaResult(
        author_id=author_id,
        biography_created=biography_created,
        compensated_author=compensated_author,
        compensated_biography=compensated_biography,
    )


async def _compensate(author_id: str, request_id: str, biography_created: bool) -> tuple[CompensationResult, CompensationResult]:
    compensated_author = CompensationResult(attempted=True, success=False, details=None)
    compensated_biography = CompensationResult(attempted=True, success=False, details=None)

    if biography_created:
        try:
            await delete_biography(DeleteBiographyInput(
                author_id=author_id,
                request_id=request_id,
            ))
            compensated_biography = CompensationResult(attempted=True, success=True, details=None)
        except Exception as e:
            compensated_biography = CompensationResult(attempted=True, success=False, details=str(e))

    try:
        await delete_author(DeleteAuthorInput(
            author_id=author_id,
            request_id=request_id,
        ))
        compensated_author = CompensationResult(attempted=True, success=True, details=None)
    except Exception as e:
        compensated_author = CompensationResult(attempted=True, success=False, details=str(e))

    return compensated_author, compensated_biography

