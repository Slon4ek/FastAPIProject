from datetime import date, timedelta

from fastapi import APIRouter, Body, Query, HTTPException
from fastapi.openapi.models import Example
from fastapi_cache.decorator import cache

from src.exceptions import (
    DateEqualError,
    DateNotEqualError,
    NotFoundError,
    RoomNotFoundHTTPException,
    HotelNotFoundHTTPException,
    DateInPastError,
    EmptyDataException,
    FacilityNotFoundException,
    HotelNotFoundError,
)
from src.api.dependencies import DBDep
from src.schemas.rooms import RoomEdit, RoomAddRequest
from src.services.rooms import RoomsService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    "/{hotel_id}/rooms",
    summary="Получить список номеров отеля",
    description="Получение списка свободных номеров отеля по его id на указанные даты",
)
@cache(expire=360)
async def get_hotel_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example=date.today()),
    date_to: date = Query(example=date.today() + timedelta(days=7)),
):
    try:
        rooms = await RoomsService(db, hotel_id).get_hotel_rooms(date_from, date_to)
    except DateEqualError:
        raise HTTPException(status_code=400, detail="Дата заезда не может быть равна дате выезда")
    except DateNotEqualError:
        raise HTTPException(status_code=400, detail="Дата выезда не может быть ранее даты заезда")
    except DateInPastError:
        raise HTTPException(status_code=400, detail="Прошедшие даты указывать нельзя.")
    except HotelNotFoundError:
        raise HotelNotFoundHTTPException
    return {"rooms": rooms}


@router.get(
    "/{hotel_id}/rooms/{room_id}",
    summary="Получить номер отеля",
    description="Получение номера отеля по его id",
)
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        return await RoomsService(db, hotel_id).get_room(room_id)
    except HotelNotFoundError:
        raise HotelNotFoundHTTPException
    except NotFoundError:
        raise RoomNotFoundHTTPException


@router.post(
    "/{hotel_id}/rooms", summary="Создать номер отеля", description="Создание номера отеля"
)
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "Standard": Example(
                value={
                    "title": "Стандартный номер",
                    "description": "Стандартный номер 25 кв. м.",
                    "price": 1000,
                    "quantity": 100,
                    "facilities_ids": [1, 2, 3],
                }
            ),
            "Lux": Example(
                value={
                    "title": "Люкс",
                    "description": "Люкс 50 кв. м.",
                    "price": 2000,
                    "quantity": 50,
                    "facilities_ids": [1, 2, 3],
                }
            ),
            "Presidential": Example(
                value={
                    "title": "Президентский номер",
                    "description": "Президентский номер 100 кв. м.",
                    "price": 5000,
                    "quantity": 10,
                    "facilities_ids": [1, 2, 3],
                }
            ),
        }
    ),
):
    try:
        room = await RoomsService(db, hotel_id).create_room(room_data)
    except FacilityNotFoundException:
        raise HTTPException(status_code=404, detail="Удобства не найдены")
    except HotelNotFoundError:
        raise HotelNotFoundHTTPException
    return {"message": "Room created", "room": room}


@router.put(
    "/{hotel_id}/rooms/{room_id}",
    summary="Обновить номер отеля",
    description="Обновление номера отеля",
)
async def update_room(db: DBDep, room_data: RoomAddRequest, hotel_id: int, room_id: int):
    try:
        await RoomsService(db, hotel_id).update_room(room_id, room_data)
    except HotelNotFoundError:
        raise HotelNotFoundHTTPException
    except NotFoundError:
        raise RoomNotFoundHTTPException
    except FacilityNotFoundException:
        raise HTTPException(status_code=404, detail="Удобства не найдены")
    return {"message": "Room updated"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частично обновить номер отеля",
    description="Частичное обновление номера отеля",
)
async def partially_update_room(db: DBDep, room_data: RoomEdit, hotel_id: int, room_id: int):
    try:
        await RoomsService(db, hotel_id).update_room(room_id, room_data, True)
        return {"message": "Room updated"}
    except HotelNotFoundError:
        raise HotelNotFoundHTTPException
    except NotFoundError:
        raise RoomNotFoundHTTPException
    except EmptyDataException:
        raise HTTPException(status_code=400, detail="Нет ни одного поля для изменения")
    except FacilityNotFoundException:
        raise HTTPException(status_code=404, detail="Удобства не найдены")


@router.delete(
    "/{hotel_id}/rooms/{room_id}",
    summary="Удалить номер отеля",
    description="Удаление номера отеля",
)
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    try:
        await RoomsService(db, hotel_id).delete_room(room_id)
    except HotelNotFoundError:
        raise HotelNotFoundHTTPException
    except NotFoundError:
        raise RoomNotFoundHTTPException
    return {"message": "Room deleted"}
