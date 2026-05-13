from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError

from src.core.config import Settings
from src.temporal.models import CreateAuthorSagaInput, CreateAuthorSagaResult
from src.temporal.workflows.create_author_saga_workflow import CreateAuthorSagaWorkflow


async def run_create_author_saga(
    payload: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
    settings = Settings()
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
    workflow_id = f"create-author-{payload.request_id}"
    try:
        handle = await client.start_workflow(
            CreateAuthorSagaWorkflow.run,
            payload,
            id=workflow_id,
            task_queue=settings.temporal_task_queue,
        )
    except WorkflowAlreadyStartedError:
        handle = client.get_workflow_handle(workflow_id)
    return await handle.result()