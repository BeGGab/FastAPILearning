import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.dao.models import Course, Book





class SProfileCreate(BaseModel):
    first_name: str = Field(None, min_length=3, max_length=50, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone_number: Optional[str] = Field(None, description="Номер телефона")
    bio: Optional[str] = Field(None, description="Биография")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r'^\+\d{1,15}$', values):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return values
    

class SProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="ID профиля")
    first_name: str
    last_name: str
    phone_number: str
    bio: Optional[str] = None
    
    
    
class SUserCreate(BaseModel):
    username: str = Field(None, min_length=3, max_length=20, description="Имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Электронная почта")
    profile: Optional[SProfileCreate]

class SUserRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID пользователя")
    username: str
    email: EmailStr
    profile: SProfileRead
    

    model_config = ConfigDict(from_attributes=True)




class SBookCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название книги")
    


class SBookRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID книги")
    title: str

    model_config = ConfigDict(from_attributes=True)


class SAuthorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Имя автора")
    books: List[SBookCreate] = Field(default_factory=list, description="Список книг автора")


    def prepare_author_db_data(self) -> dict:
        author_data = self.model_dump(exclude={"books"})
        author_data["books"] = [Book(**books.model_dump()) for books in self.books]
        return author_data
    

class SAuthorRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID автора")
    name: str
    books: List[SBookRead]

    model_config = ConfigDict(from_attributes=True)




class SCourseCreate(BaseModel):
    title: str = Field(..., min_length=1)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Название курса не может быть пустым")
        return value
    


class SCourseRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID курса")
    title: str

    model_config = ConfigDict(from_attributes=True)


class SStudentCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Имя студента")
    courses: List[SCourseCreate] = Field(default_factory=list, description="Список курсов студента")



    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        if value and len(value.strip()) < 2:
            raise ValueError("Имя студента должно содержать хотя бы 2 символа")
        return value
    

    def prepare_db_data(self) -> dict:
        student_data = self.model_dump(exclude={"courses"})
        student_data["courses"] = [Course(**course.model_dump()) for course in self.courses]
        return student_data

    
class SStudentRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID студента")
    name: str
    courses: List[SCourseRead]

    model_config = ConfigDict(from_attributes=True)
