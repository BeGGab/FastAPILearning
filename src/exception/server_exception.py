from src.exception.base import BaseHTTPException
from fastapi import status
from typing import List, Dict, Any


class InternalServerError(BaseHTTPException):
    # 500 Internal Server Error

    def __init__(self,
                 detail: str = "Внутренняя ошибка сервера",
                 error_code: str = "internal_server_error",
                 **context):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=detail,
                         error_code=error_code,
                         context=context)
        

class ServiceUnavailableError(BaseHTTPException):
    # 503 Service Unavailable
    def __init__(self,
                 detail: str = "Сервис недоступен",
                 error_code: str = "service_unavailable",
                 **context):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                         detail=detail,
                         error_code=error_code,
                         context=context)