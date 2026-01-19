

class ProjectError(Exception):
    default_message = "Что-то пошло не так"

    def __init__(self, message: str | None = None, details: dict = None) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ProjectError):
    default_message = "Запись не найдена"


class ValidationError(ProjectError):
    default_message = "Ошибка валидации данных"

    def __init__(self, message: str = None, field: str = None, value: any = None) -> None:
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(message, details)



        