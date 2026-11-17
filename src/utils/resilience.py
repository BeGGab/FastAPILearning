import httpx

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
from src.exception.biography_exception import BiographyServiceError, BiographyServiceUnavailableError
from src.core.config import settings



def skip_log_errors(exc: BaseException) -> ErrorClass | Classification | None:
    if isinstance(exc, BiographyServiceUnavailableError):
        return ErrorClass.TRANSIENT
    if isinstance(exc, BiographyServiceError):
        return ErrorClass.PERMANENT
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

        
policy = AsyncPolicy(
    retry=AsyncRetry(  
        classifier=skip_log_errors,
        strategy=decorrelated_jitter(max_s=5.0),
        max_attempts=settings.max_attempts,
        deadline_s=settings.deadline_s, 
    ),
    circuit_breaker=CircuitBreaker(
        failure_threshold=settings.failure_threshold,  
        window_s=settings.window_s,      
        recovery_timeout_s=settings.recovery_timeout_s,  
        trip_on={  # какие ошибки учитываються при размыкании
            ErrorClass.SERVER_ERROR,
            ErrorClass.CONCURRENCY,
            ErrorClass.TRANSIENT,
        },
    ),
)
