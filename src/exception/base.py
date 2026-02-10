from fastapi import HTTPException
from typing import List, Dict, Any, Optional, Union
from src.schemas.exception import ErrorDetail, ErrorResponse





class BaseHTTPException(HTTPException):
    #Базовое Исключение с доп деталями

    def __init__(self,
                 status_code: int,
                 detail: Union[str, ErrorResponse],
                 headers: Optional[Dict[str, Any]] = None,
                 error_code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.context = context or {}

        self.format_detail()

    def format_detail(self) -> None:
        # Формируем детали в структурированный вид
        if isinstance(self.detail, str):
            self.detail = ErrorResponse(
                message=self.detail,
                error_code=self.error_code,
                status_code=self.status_code,
                detail=[],
                context=self.context,
            )