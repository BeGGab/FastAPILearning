from temporalio.client import Client
from temporalio.common import WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import WorkflowAlreadyStartedError

from src.core.config import settings 
from src.schemas.author import CreateAuthorSagaInput, CreateAuthorSagaResult
from src.worker.workflows import CreateAuthorWorkflow



class AuthorSagaStarter:
    def __init__(self, client: Client):
        self.client = client


    async def create_author(self, inp: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        workflow_id = f"create-author-{inp.request_id}"
        try:
            handle = await self.client.start_workflow(
                CreateAuthorWorkflow.run,
                inp,
                id=workflow_id,
                task_queue=settings.temporal_task_queue,id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
                id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            )
        except WorkflowAlreadyStartedError:
            handle = self.client.get_workflow_handle_for(CreateAuthorWorkflow.run, workflow_id)
        return await handle.result()