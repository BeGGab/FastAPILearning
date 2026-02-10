from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime 


class ErrorDetail(BaseModel):
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: Optional[str] = Field(None, description="Код ошибки")
    field: Optional[str] = Field(None, description="Поле, в котором произошла ошибка валидации")
    context: Optional[dict] = Field(None, description="Дополнительный контекст ошибки")


class ErrorResponse(BaseModel):
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: str = Field(..., description="Код ошибки")

    timestamp: datetime = Field(default_factory=datetime.now, description="Время возникновения ошибки")
    status_code: int = Field(..., description="HTTP статус код ошибки")
    detail: List[ErrorDetail] = Field(..., description="Детали ошибки")
    context: Dict[str, Any] = Field(..., description="Дополнительный контекст ошибки")
