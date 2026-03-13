from fastapi import Query, Depends, HTTPException, Request
from typing import Annotated
from pydantic import BaseModel

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="Номер страницы")]
    per_page: Annotated[
        int | None, Query(None, ge=1, le=10, description="Количество отелей на странице")
    ]


PaginationDep = Annotated[PaginationParams, Depends()]

def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token", None)

    if not access_token:
        raise HTTPException(status_code=401, detail="Не предоставлен токен доступа")

    return access_token

def get_current_user(token: str = Depends(get_token)) -> int:
    pyload = AuthService().decode_access_token(token)
    return pyload["user_id"]

UserIdDep = Annotated[int, Depends(get_current_user)]


async def get_db_manager():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db_manager)]