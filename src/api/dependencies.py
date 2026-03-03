from fastapi import Query, Depends
from typing import Annotated
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="Номер страницы")]
    per_page: Annotated[
        int | None, Query(10, ge=1, le=10, description="Количество отелей на странице")
    ]


PaginationDep = Annotated[PaginationParams, Depends()]
