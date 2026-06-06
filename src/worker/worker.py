import asyncio
import logging

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from src.core.config import Settings
from src.activities.saga_activities import create_author_saga_activity

settings = Settings()


class AuthorWorker:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def run_worker(self) -> None:
        logging.basicConfig(level=logging.INFO)

        client = await Client.connect(
            settings.temporal_host,
            namespace=settings.temporal_namespace,
            data_converter=pydantic_data_converter,
        )

        worker = Worker(
            client=client,
            task_queue=settings.temporal_task_queue,
            activities=[
                create_author_saga_activity
            ],
        )
        await worker.run()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    asyncio.run(AuthorWorker(settings).run_worker())


if __name__ == "__main__":
    main()