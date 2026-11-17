import logging 
import uuid

from src.client.bio_author_client import BiographyServiceClient
from src.exception.biography_exception import BiographyAlreadyExistsError
from src.schemas.author import CreateAuthorSagaInput
from src.schemas.biography import SbiographyCreate

logger = logging.getLogger(__name__)


async def create_biography_step(
    client: BiographyServiceClient,
    author_id: str,
    inp: CreateAuthorSagaInput,
) -> None:
    try:
        await client.create_biography_for_author(
            bio_data=SbiographyCreate(
                author_id=author_id,
                bio_text=inp.biography_text,
                year_of_birth=inp.year_of_birth,
                year_of_death=inp.year_of_death,
            )
        )
    except BiographyAlreadyExistsError:
        logger.info("Биография автора %s уже существует - повтор шага, считаем успехом", author_id)

async def delete_biography_step(client: BiographyServiceClient, author_id: str) -> None:
    await client.delete_biography(uuid.UUID(author_id))