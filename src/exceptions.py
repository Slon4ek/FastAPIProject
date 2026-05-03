from typing import Any

from fastapi import HTTPException


class ProjectException(Exception):
    detail: str | list[Any] = "Неожиданная ошибка"

    def __init__(self, detail: str, *args):
        self.detail = detail
        super().__init__(self.detail, *args)

class AuthenticationError(ProjectException):
    pass


class NotFoundError(ProjectException):
    pass


class NotAvailableError(ProjectException):
    pass


class IsAlreadyExistsError(ProjectException):
    pass


class UserAlreadyExistsException(IsAlreadyExistsError):
    pass


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


class JWTExpiredError(ProjectException):
    detail = "JWT expire error"


class JWTDecodeError(ProjectException):
    detail = "JWT decode error"


class EmailAlreadyExistsHTTPException(ProjectHTTPException):
    status_code = 409
    detail = "Email already exists"


class UsernameAlreadyExistsHTTPException(ProjectHTTPException):
    status_code = 409
    detail = "Username already exists"