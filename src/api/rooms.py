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
)
from src.api.dependencies import DBDep
from src.schemas.rooms import RoomEdit, RoomAddRequest
from src.services.hotels import HotelsService
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
        rooms = await RoomsService(db).get_hotel_rooms(hotel_id, date_from, date_to)
    except DateEqualError:
        raise HTTPException(status_code=400, detail="Дата заезда не может быть равна дате выезда")
    except DateNotEqualError:
        raise HTTPException(status_code=400, detail="Дата выезда не может быть ранее даты заезда")
    return {"rooms": rooms}


@router.get(
    "/{hotel_id}/rooms/{room_id}",
    summary="Получить номер отеля",
    description="Получение номера отеля по его id",
)
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        return await RoomsService(db).get_room(hotel_id, room_id)
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
        hotel = await HotelsService(db).get_hotel(hotel_id)
    except NotFoundError:
        raise HotelNotFoundHTTPException
    room = await RoomsService(db).create_room(hotel.id, room_data)
    return {"message": "Room created", "room": room}


@router.put(
    "/{hotel_id}/rooms/{room_id}",
    summary="Обновить номер отеля",
    description="Обновление номера отеля",
)
async def update_room(db: DBDep, room_data: RoomAddRequest, hotel_id: int, room_id: int):
    try:
        await RoomsService(db).update_room(hotel_id, room_id, room_data)
    except NotFoundError:
        raise RoomNotFoundHTTPException
    return {"message": "Room updated"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частично обновить номер отеля",
    description="Частичное обновление номера отеля",
)
async def partially_update_room(db: DBDep, room_data: RoomEdit, hotel_id: int, room_id: int):
    try:
        await RoomsService(db).update_room(hotel_id, room_id, room_data, True)
    except NotFoundError:
        raise RoomNotFoundHTTPException
    return {"message": "Room updated"}


@router.delete(
    "/{hotel_id}/rooms/{room_id}",
    summary="Удалить номер отеля",
    description="Удаление номера отеля",
)
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    try:
        await RoomsService(db).delete_room(hotel_id, room_id)
    except NotFoundError:
        raise RoomNotFoundHTTPException
    return {"message": "Room deleted"}
