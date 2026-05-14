from datetime import date, timedelta
from fastapi import APIRouter, Query, Body
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import Example
from fastapi_cache.decorator import cache

from src.exceptions import (
    DateEqualError,
    DateNotEqualError,
    NotFoundError,
    HotelNotFoundHTTPException,
    DateInPastError,
    EmptyDataException,
)
from src.schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep, DBDep
from src.services.hotels import HotelsService

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    summary="Получить список отелей",
    description="Получить список отелей со свободными номерами на указанные даты",
)
@cache(expire=360)
async def get_hotels(
    db: DBDep,
    pagination: PaginationDep,
    date_from: date | None = Query(None, description="Дата заезда", example=date.today()),
    date_to: date | None = Query(
        None, description="Дата выезда", example=date.today() + timedelta(days=7)
    ),
    stars: int | None = Query(None, description="Количество звезд", ge=1, le=5),
    title: str | None = Query(None, description="Название отеля", min_length=1),
    location: str | None = Query(None, description="Адрес отеля", min_length=1),
):
    try:
        return await HotelsService(db).get_hotels(
            pagination=pagination,
            date_from=date_from,
            date_to=date_to,
            stars=stars,
            title=title,
            location=location,
        )
    except DateEqualError:
        raise HTTPException(status_code=400, detail="Дата заезда не может быть равна дате выезда")
    except DateNotEqualError:
        raise HTTPException(status_code=400, detail="Дата выезда не может быть ранее даты заезда")
    except DateInPastError:
        raise HTTPException(status_code=400, detail="Прошедшие даты указывать нельзя.")


@router.get("/{hotel_id}", summary="Получить отель по id")
async def get_hotel(hotel_id: int, db: DBDep):
    try:
        hotel = await HotelsService(db).get_hotel(hotel_id)
    except NotFoundError:
        raise HotelNotFoundHTTPException
    return hotel


@router.delete("/{hotel_id}", summary="Удалить отель")
async def delete_hotel(hotel_id: int, db: DBDep):
    try:
        await HotelsService(db).delete_hotel(hotel_id)
        return {"message": "Отель успешно удален"}
    except NotFoundError:
        raise HotelNotFoundHTTPException


@router.post("", summary="Добавить отель")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "Hilton Hotel": Example(
                value={"title": "Hilton", "stars": 5, "location": "г. Сочи, ул. Моря, д. 1"},
            ),
            "Four Seasons Hotel": Example(
                value={
                    "title": "Four Seasons",
                    "stars": 4,
                    "location": "г. Москва, ул. Ленина, д. 1",
                }
            ),
        }
    ),
):
    new_hotel = await HotelsService(db).add_hotel(hotel_data)
    return {"Status": "Ok", "data": new_hotel}


@router.put("/{hotel_id}", summary="Полное обновление данных об отеле")
async def update_hotel(hotel_id: int, hotel_data: HotelAdd, db: DBDep):
    try:
        await HotelsService(db).edit_hotel(hotel_data, hotel_id)
        return {"message": "Отель успешно обновлен"}
    except NotFoundError:
        raise HotelNotFoundHTTPException


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле")
async def partial_update_hotel(hotel_id: int, hotel_data: HotelPatch, db: DBDep):
    try:
        await HotelsService(db).edit_hotel(hotel_data, hotel_id, for_patch=True)
        return {"message": "Отель успешно обновлен"}
    except NotFoundError:
        raise HotelNotFoundHTTPException
    except EmptyDataException:
        raise HTTPException(status_code=400, detail="Нет ни одного поля для изменения")
