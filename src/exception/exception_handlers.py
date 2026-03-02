import logging
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import UJSONResponse

from src.exception.base import BaseHTTPException


logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseHTTPException)
    async def http_exception_handler(
        request: Request, exc: BaseHTTPException
    ) -> UJSONResponse:
        # оброботчик кастомных исключений
        if exc.status_code != status.HTTP_404_NOT_FOUND:
            logger.warning(
                f"Ошибка {exc.status_code}: {exc.detail}",
                extra={
                    "error_code": exc.error_code,
                    "path": request.url.path,
                    "method": request.method,
                    **exc.context,
                },
            )
        # Преобразуем Pydantic модель в словарь, чтобы datetime и другие типы корректно сериализовались
        content = jsonable_encoder(exc.detail)
        return UJSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> UJSONResponse:
        # обработчик ошибок валидации запросов

        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": " -> ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        logger.info(
            f"Ошибка валидации запроса: {errors}", extra={"path": request.url.path}
        )

        return UJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "message": "Ошибка валидации запроса",
                "error_code": "validation_error",
                "validation_errors": errors,
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> UJSONResponse:
        # обработка ошибки 404
        logger.info(f"ошибка 404: {request.url.path}", extra={"method": request.method})

        return UJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": f"Страница {request.url.path} не найдена",
                "error_code": "Router_not_found",
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> UJSONResponse:
        # обработчик остальных исключений

        logger.error(
            f"Необработанная ошибка: {str(exc)}",
            exc_info=True,
            extra={"path": request.url.path, "method": request.method},
        )

        is_production = False
        error_detail = str(exc) if not is_production else "Внутренняя ошибка сервера"

        return UJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Внутренняя ошибка сервера",
                "error_code": "internal_server_error",
                "detail": error_detail if not is_production else None,
            },
        )
