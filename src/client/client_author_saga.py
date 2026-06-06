from datetime import timedelta

from temporalio.client import Client
from temporalio.common import ActivityIDConflictPolicy, ActivityIDReusePolicy
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ActivityAlreadyStartedError

from src.core.config import Settings
from src.schemas.saga import CreateAuthorSagaInput, CreateAuthorSagaResult

settings = Settings()


async def run_create_author_saga(
    payload: CreateAuthorSagaInput,
) -> CreateAuthorSagaResult:
    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
        data_converter=pydantic_data_converter,
    )

    activity_id = f"create-author-{payload.request_id}"
    activity_kwargs = {
        "id": activity_id,
        "task_queue": settings.temporal_task_queue,
        "result_type": CreateAuthorSagaResult,
        "start_to_close_timeout": timedelta(seconds=60),
        "id_conflict_policy": ActivityIDConflictPolicy.USE_EXISTING,
        "id_reuse_policy": ActivityIDReusePolicy.ALLOW_DUPLICATE,
    }

    try:
        return await client.execute_activity(
            "create_author_saga_activity",
            payload,
            **activity_kwargs,
        )
    except ActivityAlreadyStartedError as exc:
        handle = client.get_activity_handle(
            activity_id,
            run_id=exc.run_id,
            result_type=CreateAuthorSagaResult,
        )
        return await handle.result()
