from fastapi import APIRouter, Body

from src.api.dependencies import DBDep
from src.schemas.rooms import RoomAdd, RoomEdit, RoomAddRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    "/{hotel_id}/rooms",
    summary="Получить список номеров отеля",
    description="Получение списка номеров отеля по его id"
)
async def get_hotel_rooms(
        hotel_id: int,
        db: DBDep
):
    rooms = await db.rooms.get_all_by_filter(hotel_id=hotel_id)
    return {"rooms": rooms}


@router.get(
    "/{hotel_id}/rooms/{room_id}",
    summary="Получить номер отеля",
    description="Получение номера отеля по его id"
)
async def get_room(
        hotel_id: int,
        room_id: int,
        db: DBDep
):
    room = await db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)

    if room is None:
        return {"message": "Room not found"}

    return {"room": room}


@router.post(
    "/{hotel_id}/rooms",
    summary="Создать номер отеля",
    description="Создание номера отеля"
)
async def create_room(
        db: DBDep,
        hotel_id: int,
        room_data: RoomAddRequest = Body(
            openapi_examples={
                "Standart": {
                    "value": {
                        "title": "Стандартный номер",
                        "description": "Стандартный номер 25 кв. м.",
                        "price": 1000,
                        "quantity": 100
                    }
                },
                "Lux": {
                    "value": {
                        "title": "Люкс",
                        "description": "Люкс 50 кв. м.",
                        "price": 2000,
                        "quantity": 50
                    }
                },
                "Presidential": {
                    "value": {
                        "title": "Президентский номер",
                        "description": "Президентский номер 100 кв. м.",
                        "price": 5000,
                        "quantity": 10
                    }
                }
            }
        )
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)
    await db.commit()
    return {"message": "Room created", "room": room}


@router.put(
    "/{hotel_id}/rooms/{room_id}",
    summary="Обновить номер отеля",
    description="Обновление номера отеля"
)
async def update_room(
        db: DBDep,
        room_data: RoomAddRequest,
        hotel_id: int,
        room_id: int
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(data=_room_data, hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {"message": "Room updated", "room": room_data}


@router.delete(
    "/{hotel_id}/rooms/{room_id}",
    summary="Удалить номер отеля",
    description="Удаление номера отеля"
)
async def delete_room(
        db: DBDep,
        hotel_id: int,
        room_id: int
):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {"message": "Room deleted"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частично обновить номер отеля",
    description="Частичное обновление номера отеля"
)
async def partially_update_room(
        db: DBDep,
        room_data: RoomEdit,
        hotel_id: int,
        room_id: int
):
    await db.rooms.edit(data=room_data, hotel_id=hotel_id, id=room_id, for_patch=True)
    await db.commit()
    return {"message": "Room updated"}
