import httpx
import json
from typing import Any

from redress import (
    CircuitBreaker,
    Classification,
    ErrorClass,
    AsyncPolicy,
    AsyncRetry
)
from redress.strategies import decorrelated_jitter

from src.exception.client_exception import BadRequestError, NotFoundError, ConflictError, ValidationError
from src.exception.server_exception import ServiceUnavailableError, InternalServerError



def _response_json(response: httpx.Response) -> Any:
    if not response.content:
        raise ConflictError(detail="Пустой ответ от сервиса")
    return json.loads(response.content)


def skip_log_errors(exc: BaseException) -> ErrorClass | Classification | None:
    if isinstance(exc, (ValueError, TypeError, ValidationError)):
        return ErrorClass.PERMANENT
    if isinstance(exc, (ValidationError, BadRequestError, NotFoundError, ConflictError)):
        return ErrorClass.PERMANENT
    if isinstance(exc, (ServiceUnavailableError, InternalServerError)):
        return ErrorClass.TRANSIENT

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code is not None and 400 <= status_code < 500 and status_code not in (408, 429):
            return ErrorClass.PERMANENT
        return ErrorClass.TRANSIENT

    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.RequestError)):
        return ErrorClass.TRANSIENT

    return ErrorClass.UNKNOWN


def _raise_logical_error(response: httpx.Response, operation: str) -> None:
    status_code = response.status_code
    response_preview = response.text[:500]
    
    if status_code == 409:
        raise ConflictError(detail=f"{operation}: конфликт данных")
    if status_code in (408, 429, 503):
        raise ServiceUnavailableError(
            detail=f"{operation}: сервис временно недоступен ({status_code}): {response_preview}"
        )
    if 400 <= status_code < 500:
        raise BadRequestError(detail=f"{operation}: клиентская ошибка ({status_code}): {response_preview}")

policy = AsyncPolicy(
    retry=AsyncRetry(  
        classifier=skip_log_errors,
        strategy=decorrelated_jitter(max_s=5.0),
        max_attempts=5,
        deadline_s=30,
    ),
    circuit_breaker=CircuitBreaker(
        failure_threshold=5,  
        window_s=60.0,      
        recovery_timeout_s=30.0,  
        trip_on={  # какие ошибки учитываються при размыкании
            ErrorClass.SERVER_ERROR,
            ErrorClass.CONCURRENCY,
            ErrorClass.TRANSIENT,
        },
    ),
)
