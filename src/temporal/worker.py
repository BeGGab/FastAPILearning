import asyncio
import logging

from temporalio.client import Client 
from temporalio.worker import Worker

from src.core.config import Settings
from src.temporal.activities.author_activities import create_author_activity, delete_author_activity
from src.temporal.activities.biography_activities import create_biography_activity, delete_biography_activity

from src.temporal.workflows.create_author_saga_workflow import CreateAuthorSagaWorkflow



async def run_worker() -> None:
    logging.basicConfig(level=logging.INFO)
    settings =Settings()

    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)

    worker = Worker(
        client=client,
        task_queue=settings.temporal_task_queue,
        workflows=[CreateAuthorSagaWorkflow],
        activities=[
            create_author_activity,
            delete_author_activity,
            create_biography_activity,
            delete_biography_activity,
        ],
    )
    await worker.run()


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()