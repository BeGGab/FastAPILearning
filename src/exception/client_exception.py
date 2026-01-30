from src.exception.base import BaseHTTPException
from fastapi import status
from typing import List, Dict, Any




class BadRequestError(BaseHTTPException):
     # 400 Bad Request

     def __init__(self,
                  detail: str = "Неверный запрос",
                  error_code: str = "bad_request",
                  **context):
          super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=detail,
                           error_code=error_code,
                           context=context)
          
class NotFoundError(BaseHTTPException):
     # 404 Not Found

     def __init__(self,
                  detail: str = "Ресурс не найден",
                  error_code: str = "not_found",
                  **context):
          super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                           detail=detail,
                           error_code=error_code,
                           context=context)
          

class ConflictError(BaseHTTPException):
     # 409 Conflict

     def __init__(self,
                  detail: str = "Ресурс уже существует",
                  error_code: str = "conflict",
                  **context):
          super().__init__(status_code=status.HTTP_409_CONFLICT,
                           detail=detail,
                           error_code=error_code,
                           context=context)
          

class ValidationError(BadRequestError):
     # 422 Validation Error (для Pydantic)
     def __init__(self,
                  error: List[Dict[str, Any]],
                  detail: str = "Ошибка валидации",
                  error_code: str = "validation_error",
                  **context):
           super().__init__(detail=detail,
                            error_code=error_code,
                            context=context)