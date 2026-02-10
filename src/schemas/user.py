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

from src.models.user import User
from src.models.profile import Profile
from src.schemas.profile import (SProfileCreate, SProfileUpdate, SProfileRead)
from src.exception.client_exception import ValidationError, NotFoundError


class SUserCreate(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=20, description="Имя пользователя"
    )
    email: Optional[EmailStr] = Field(..., description="Электронная почта")
    profile: Optional[SProfileCreate] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or v == "string":
            raise ValidationError(detail=f"Электронная почта не должна быть пустой")
        return v

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, v: str):
        if not v or v == "string":
            raise ValidationError(detail=f"Username пользователя не должно быть пустым")
        return v

    def to_orm_models(self) -> tuple[User, Optional[Profile]]:
        user = User(**self.model_dump(exclude={"profile"}))
        profile = None
        if self.profile:
            profile = Profile(**self.profile.model_dump())
            profile.user = user
        return user, profile


class SUserUpdate(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=20, description="Имя пользователя"
    )
    email: Optional[EmailStr] = Field(None, description="Электронная почта")
    profile: Optional[SProfileUpdate] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: str):
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError

    @model_validator(mode="after")
    def validate_update_data(self) -> "SUserUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise NotFoundError("Нет данных для обновления")
        return self

    def apply_to_user(self, user: User) -> None:
        for field, value in self.model_dump(
            exclude_unset=True, exclude_none=True, exclude={"profile"}
        ).items():
            setattr(user, field, value)
            
        if self.profile:
            update_data = self.profile.model_dump(exclude_unset=True)
            if user.profile is None:
                user.profile = Profile(**update_data)
            else:
                for field, value in update_data.items():
                    setattr(user.profile, field, value)


class SUserRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID пользователя")
    username: str
    email: EmailStr
    profile: SProfileRead

    model_config = ConfigDict(from_attributes=True)
