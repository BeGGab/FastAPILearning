import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional

from src.models.user_models import User


class SProfileCreate(BaseModel):
    first_name: str = Field(None, min_length=3, max_length=50, description="Имя")
    last_name: str = Field(None, description="Фамилия")
    phone_number: str = Field(None, description="Номер телефона")
    bio: str = Field(None, description="Биография")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not values or values == "string":
            return values
        if not re.match(r"^\+\d{1,15}$", values):
            raise ValueError(
                'Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр'
            )
        return values
    

class SProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=3, max_length=50, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone_number: Optional[str] = Field(None, description="Номер телефона")
    bio: Optional[str] = Field(None, description="Биография")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not values or values == "string":
            return values
        if not re.match(r"^\+\d{1,15}$", values):
            raise ValueError(
                'Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр'
            )
        return values


class SProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="ID профиля")
    first_name: str
    last_name: str
    phone_number: str
    bio: Optional[str] = None