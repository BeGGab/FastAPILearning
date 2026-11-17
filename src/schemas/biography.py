from pydantic import BaseModel, Field, ConfigDict

from typing import Optional


class SbiographyCreate(BaseModel):
    author_id: Optional[str] = Field(None, description="ID автора")
    bio_text: Optional[str] = Field(None, alias="text", description="Биография автора")
    year_of_birth: Optional[int] = Field(None, description="Год рождения автора")
    year_of_death: Optional[int] = Field(None, description="Год смерти автора")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)



class SAuthorBioResponse(BaseModel):
    biography_text: Optional[str] = Field(
        None, alias="text", description="Биография автора"
    )
    year_of_birth: Optional[int] = Field(None, description="Год рождения автора")
    year_of_death: Optional[int] = Field(None, description="Год смерти автора")

    model_config = ConfigDict(populate_by_name=True)


class CreateBiographyInput(BaseModel):
    request_id: str = Field(..., description="ID запроса")
    author_id: str = Field(..., description="ID автора")
    author_name: str = Field(..., description="Имя автора")
    biography_text: str = Field(..., description="Текст биографии")
    year_of_birth: int = Field(..., description="Год рождения")
    year_of_death: int = Field(..., description="Год смерти")


class DeleteBiographyInput(BaseModel):
    author_id: str = Field(..., description="ID автора")
    request_id: str = Field(..., description="ID запроса")