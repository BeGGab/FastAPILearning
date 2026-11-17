from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


with workflow.unsafe.imports_passed_through():
    from src.schemas.author import CreateAuthorSagaInput, CreateAuthorSagaResult



@workflow.defn
class CreateAuthorWorkflow:
    @workflow.run
    async def run(self, inp: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        return await workflow.execute_activity(
            "create_author_saga",
            inp,
            result_type=CreateAuthorSagaResult,
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )