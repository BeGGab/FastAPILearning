


class BiographyServiceError(Exception):
    """def __init__(
        self,
        detail: str = "Ошибка при работе с сервисом биографии",
        error_code: str = "biography_service_error",
        **context,
    ):"""


class BiographyNotFoundError(BiographyServiceError):
    def __init__(self, author_id) -> None:
        self.author_id = author_id
        super().__init__(f"Биография автора с id: {author_id} не найдена")


class BiographyAlreadyExistsError(BiographyServiceError):
    def __init__(self, author_id) -> None:
        self.author_id = author_id
        super().__init__(f"Биография автора с id: {author_id} уже существует")


class BiographyServiceUnavailableError(BiographyServiceError):
    "Временная ошибка (таймаут, 429, 5хх) - повтор имеет смысд"
    

class BiographyBadResponseError(BiographyServiceError):
    "Неожиданный ответ от сервиса - повтор не поможет"