import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional

from src.models.user_models import User
from src.schemas.profile_schemas import SProfileCreate, SProfileRead, SProfileUpdate


class SUserCreate(BaseModel):
    username: str = Field(None, min_length=3, max_length=20, description="Имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Электронная почта")
    profile: Optional[SProfileCreate]

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if not value or value == "string":
            return f"User_{str(uuid.uuid4())[:8]}"
        return value

    

class SUserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=20, description="Имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Электронная почта")
    profile: Optional[SProfileUpdate]

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if value is not None and (not value.strip() or value == "string"):
            return f"User_{str(uuid.uuid4())[:8]}"
        return value

    


class SUserRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID пользователя")
    username: str
    email: EmailStr
    profile: SProfileRead

    model_config = ConfigDict(from_attributes=True)
