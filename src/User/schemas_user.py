import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime







class SProfileCreate(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия")
    phone_number: str = Field(None, description="Номер телефона")
    bio: Optional[str] = Field(None, description="Биография")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r'^\+\d{1,15}$', values):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return values
    

class SProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[uuid.UUID] = Field(... or None, description="ID профиля")
    first_name: str
    last_name: str
    phone_number: str
    bio: Optional[str] = None
    
    
    
class SUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта")
    profile: Optional[SProfileCreate]

class SUserRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID пользователя")
    username: str
    email: EmailStr
    profile: SProfileRead
    

    model_config = ConfigDict(from_attributes=True)
