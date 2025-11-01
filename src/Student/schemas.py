import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime




class SCourseCreate(BaseModel):
    title: str = Field(..., min_length=1)


class SCourseRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID курса")
    title: str
    #students: List[SUserRead]

    model_config = ConfigDict(from_attributes=True)


class SStudentCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Имя студента")
    courses: List[SCourseCreate] = Field(default_factory=list, description="Список курсов студента")

    
class SStudentRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID студента")
    name: str
    courses: List[SCourseRead]

    model_config = ConfigDict(from_attributes=True)