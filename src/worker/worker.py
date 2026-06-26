import asyncio
import logging
from typing import List

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker
from temporalio import activity

from src.schemas.author import CreateAuthorSagaInput, CreateAuthorSagaResult, CompensationResult, DeleteAuthorInput
from src.schemas.biography import CreateBiographyInput, DeleteBiographyInput
from src.worker.author import create_author, delete_author
from src.worker.biography import create_biography, delete_biography

from src.core.config import settings

logger = logging.getLogger(__name__)

def build_activities(author_worker: "AuthorWorker") -> List:
    @activity.defn(name="create_author_saga_activity")
    async def create_autor_saga_activity(payload: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        return await author_worker.run_create_author_saga(payload)
    return [create_autor_saga_activity]


class AuthorWorker:

    @staticmethod
    async def _has_bio(payload: CreateAuthorSagaInput) -> bool:
        return (
            payload.biography_text is not None
            and payload.year_of_birth is not None
            and payload.year_of_death is not None
        )


    async def run_create_author_saga(self, payload: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        author_id: str | None = None
        biography_created = False
        has_bio = await self._has_bio(payload)

        compensated_author = CompensationResult(
            attempted=False, success=False, details=None
        )
        compensated_biography = CompensationResult(
            attempted=False, success=False, details=None
        )

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
                compensated_author, compensated_biography = await self._compensate(
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


    async def _compensate(
        self,
        author_id: str,
        request_id: str,
        biography_created: bool,
    ) -> tuple[CompensationResult, CompensationResult]:
        compensated_author = CompensationResult(
            attempted=True, success=False, details=None
        )
        compensated_biography = CompensationResult(
            attempted=True, success=False, details=None
        )

        if biography_created:
            try:
                await delete_biography(
                    DeleteBiographyInput(
                        author_id=author_id,
                        request_id=request_id,
                    )
                )
                compensated_biography = CompensationResult(
                    attempted=True, success=True, details=None
                )
            except Exception as e:
                compensated_biography = CompensationResult(
                    attempted=True, success=False, details=str(e)
                )

        try:
            await delete_author(
                DeleteAuthorInput(
                    author_id=author_id,
                    request_id=request_id,
                )
            )
            compensated_author = CompensationResult(
                attempted=True, success=True, details=None
            )
        except Exception as e:
            compensated_author = CompensationResult(
                attempted=True, success=False, details=str(e)
            )

        return compensated_author, compensated_biography



    async def run_worker(self) -> None:
        client = await Client.connect(
            settings.temporal_host,
            namespace=settings.temporal_namespace,
            data_converter=pydantic_data_converter,
        )

        worker = Worker(
            client=client,
            task_queue=settings.temporal_task_queue,
            activities=build_activities(self)
        )
        await worker.run()

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(AuthorWorker().run_worker())

if __name__ == "__main__":
    main()