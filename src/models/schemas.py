import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime




class SAutorAdd(BaseModel):
    id: Optional[uuid.UUID] = Field(None, description="ID автора")
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    bio: Optional[str] = Field(None, max_length=1000, description="Биография автора")

class SBookAdd(BaseModel):
    id: Optional[uuid.UUID] = Field(None, description="ID книги")
    title: Optional[str] = Field(None, min_length=5, max_length=100, description="Название книги")
    description: Optional[str] = Field(None, max_length=1000, description="Описание книги")
    publication_year: Optional[int] = Field(None, description="Год публикации")
    

class SDepartmentAdd(BaseModel):
    id: Optional[uuid.UUID] = Field(None, description="ID отдела")
    name: Optional[str] = Field(None, min_length=3, max_length=50, description="Название отдела")
    description: Optional[str] = Field(None, max_length=1000, description="Описание отдела")




class SProfileAdd(BaseModel):
    id: uuid.UUID = Field(None, description="ID пользователя")
    full_name: str = Field(..., min_length=3, max_length=50, description="Полное имя пользователя")
    bio: str = Field(..., max_length=1000, description="Биография пользователя")


class SUserAdd(BaseModel):
    id: uuid.UUID = Field(None, description="ID пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    phone_number: str = Field(..., description="Номер телефона пользователя")
    profile: Optional[SProfileAdd] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError("Номер телефона должен начинаться с '+' и содержать только цифры")
        return value


class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="ID пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    phone_number: str = Field(..., description="Номер телефона пользователя")
    profile: Optional[SProfileAdd] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError("Номер телефона должен начинаться с '+' и содержать только цифры")
        return value
