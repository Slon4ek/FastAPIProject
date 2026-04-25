from typing import Any


class ProjectException(Exception):
    detail: str = "Unknown error"

    def __init__(self, *args: Any) -> None:
        super().__init__(self.detail, *args)


class NotFoundError(ProjectException):
    detail: str = "Not found"


class NotAvailableError(ProjectException):
    detail: str = "Not available"


class InsertionError(ProjectException):
    detail: str = "Insertion error"


class DateEqualError(ProjectException):
    pass


class DateNotEqualError(ProjectException):
    pass
