import asyncio
import logging 

import httpx
from temporalio import activity
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from src.client.bio_author_client import BiographyServiceClient
from src.core.config import settings
from src.schemas.author import CreateAuthorSagaInput, CreateAuthorSagaResult
from src.worker.author_saga import CreateAuthorSaga
from src.worker.workflows import CreateAuthorWorkflow



class SagaActivities:
    def __init__(self, saga: CreateAuthorSaga):
        self.saga = saga

    
    @activity.defn(name="create_author_saga")
    async def create_author_saga(self, inp: CreateAuthorSagaInput) -> CreateAuthorSagaResult:
        return await self.saga.run(inp)



async def run_worker() -> None:
    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
        data_converter=pydantic_data_converter,
    )
    async with httpx.AsyncClient(
        base_url=settings.biography_service_url, timeout=settings.timeout
    ) as http:
        activities = SagaActivities(CreateAuthorSaga(BiographyServiceClient(http)))
        worker = Worker(
            client,
            task_queue=settings.temporal_task_queue,
            workflows=[CreateAuthorWorkflow],
            activities=[activities.create_author_saga],
        )
        await worker.run()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())

if __name__ == "__main__":
    main()