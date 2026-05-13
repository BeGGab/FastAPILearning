from datetime import timedelta
from temporalio import workflow

from src.temporal.models import (
    CreateAuthorSagaInput,
    CreateAuthorSagaResult,
    CompensationResult,
    CreateBiographyInput,
    DeleteBiographyInput,
    DeleteAuthorInput,
)




@workflow.defn
class CreateAuthorSagaWorkflow:
    @workflow.run
    async def run(self, payload: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        author_id: str | None = None
        biography_created = False

        compensated_author = CompensationResult(attempted=False, success=False, details=None)
        compensated_biography = CompensationResult(attempted=False, success=False, details=None)

        has_bio = (
            payload.biography_text is not None
            and payload.year_of_birth is not None
            and payload.year_of_death is not None
        )

        try:
            author_id = await workflow.execute_activity(
                "create_author_activity",
                payload,
                start_to_close_timeout=timedelta(seconds=15)
            )

            if has_bio:
                bio_input = CreateBiographyInput(
                    request_id=payload.request_id,
                    author_id=author_id,
                    author_name=payload.name,
                    biography_text=payload.biography_text,
                    year_of_birth=payload.year_of_birth,
                    year_of_death=payload.year_of_death,
                )
                await workflow.execute_activity(
                    "create_biography_activity",
                    bio_input,
                    start_to_close_timeout=timedelta(seconds=15)
                )
                biography_created = True

            return CreateAuthorSagaResult(
                author_id=author_id,
                biography_created=biography_created,
                compensated_author=compensated_author,
                compensated_biography=compensated_biography,
            )

        except Exception as e:
            if author_id and has_bio:
                try:
                    await workflow.execute_activity(
                        "delete_biography_activity",
                        DeleteBiographyInput(
                            author_id=author_id,
                            request_id=payload.request_id,
                        ),
                        start_to_close_timeout=timedelta(seconds=15)
                    )
                    compensated_biography = CompensationResult(attempted=True, success=True, details="Biography deleted")

                except Exception as bio_exc:
                    compensated_biography = CompensationResult(attempted=True, success=False, details=f"Failed to delete biography: {bio_exc}")

            if author_id:
                try:
                    await workflow.execute_activity(
                        "delete_author_activity",
                        DeleteAuthorInput(
                            author_id=author_id,
                            request_id=payload.request_id,
                        ),
                        start_to_close_timeout=timedelta(seconds=15)
                    )
                    compensated_author = CompensationResult(attempted=True, success=True, details="Author deleted")

                except Exception as author_exc:
                    compensated_author = CompensationResult(attempted=True, success=False, details=f"Failed to delete author: {author_exc}")

            raise RuntimeError(
                f"Saga failed. author_id={author_id},"
                f"bio_comp={compensated_biography}, author_comp={compensated_author}, error={e}"
            )