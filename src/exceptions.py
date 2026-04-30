from typing import Any

from fastapi import HTTPException


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


class IsAlreadyExistsError(InsertionError):
    detail: str = "Already exists"


class DateEqualError(ProjectException):
    pass


class DateNotEqualError(ProjectException):
    pass


class ProjectHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self) -> None:
        super().__init__(detail=self.detail, status_code=self.status_code)


class HotelNotFoundHTTPException(ProjectHTTPException):
    status_code = 404
    detail = "Hotel not found"


class RoomNotFoundHTTPException(ProjectHTTPException):
    status_code = 404
    detail = "Room not found"
