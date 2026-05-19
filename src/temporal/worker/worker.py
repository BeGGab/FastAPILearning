import asyncio
import logging

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from src.core.config import Settings
from src.temporal.activities.author_activities import create_author_activity, delete_author_activity
from src.temporal.activities.biography_activities import create_biography_activity, delete_biography_activity

from src.temporal.workflows.create_author_saga_workflow import CreateAuthorSagaWorkflow




class AuthorWorker:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def run_worker(self) -> None:
        logging.basicConfig(level=logging.INFO)

        client = await Client.connect(
            self.settings.temporal_host,
            namespace=self.settings.temporal_namespace,
            data_converter=pydantic_data_converter,
        )

        worker = Worker(
            client=client,
            task_queue=self.settings.temporal_task_queue,
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
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    asyncio.run(AuthorWorker(settings).run_worker())


if __name__ == "__main__":
    main()