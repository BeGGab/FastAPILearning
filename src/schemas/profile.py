import re
import uuid
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)
from typing import Optional

from src.exception.client_exception import ValidationError, NotFoundError


class SProfileCreate(BaseModel):
    first_name: str = Field(None, min_length=3, max_length=50, description="Имя")
    last_name: str = Field(None, description="Фамилия")
    phone_number: str = Field(..., description="Номер телефона")
    bio: str = Field(None, description="Биография")

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r"^\+7\d{10}$", values):
            raise ValidationError(
                detail=f'Номер телефона должен начинаться с "+7" и содержать 10 цифр.'
            )
        return values


class SProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Имя"
    )
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone_number: Optional[str] = Field(None, description="Номер телефона")
    bio: Optional[str] = Field(None, description="Биография")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "string":
            return value
        if not re.match(r"^\+7\d{10}$", value):
            raise ValidationError(
                detail=f'Номер телефона должен начинаться с "+7" и содержать 10 цифр.'
            )
        return value


class SProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="ID профиля")
    first_name: str
    last_name: str
    phone_number: str
    bio: Optional[str] = None
