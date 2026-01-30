from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional


class BaseHTTPException(HTTPException):
    #Базовое Исключение с доп деталями

    def __init__(self,
                 status_code: int,
                 detail: Any = None,
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
            self.detail = {
                "message": self.detail,
                "error_code": self.error_code,
                **self.context
            }
