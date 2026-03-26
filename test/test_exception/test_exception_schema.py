from src.schemas.exception import ErrorDetail, ErrorResponse


def test_error_response_schema_builds() -> None:
    detail = ErrorDetail(message="Invalid field", error_code="validation_error", field="email")
    response = ErrorResponse(
        message="Validation failed",
        error_code="validation_error",
        status_code=422,
        detail=[detail],
        context={"source": "test"},
    )
    assert response.error_code == "validation_error"
    assert response.detail[0].field == "email"
