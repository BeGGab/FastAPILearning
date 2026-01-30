import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator, model_validator
from typing import Optional

from src.models.user_models import User
from src.models.profile_models import Profile



class SProfileCreate(BaseModel):
    first_name: str = Field(None, min_length=3, max_length=50, description="Имя")
    last_name: str = Field(None, description="Фамилия")
    phone_number: str = Field(..., description="Номер телефона")
    bio: str = Field(None, description="Биография")

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r"^\+\d{1,11}$", values):
            raise ValueError(
                'Поле не должно бють пустым и Номер телефона должен начинаться с "+" и содержать от 1 до 11 цифр'
            )
        return values

    
    

class SProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=3, max_length=50, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone_number: Optional[str] = Field(..., description="Номер телефона")
    bio: Optional[str] = Field(None, description="Биография")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "string":
            return value  
        if not re.match(r"^\+\d{1,11}$", value):
            raise ValueError(
                'Номер телефона должен начинаться с "+" и содержать от 1 до 11 цифр')
        return value
    



class SProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="ID профиля")
    first_name: str
    last_name: str
    phone_number: str
    bio: Optional[str] = None