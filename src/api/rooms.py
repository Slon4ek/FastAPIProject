from datetime import date, timedelta

from fastapi import APIRouter, Body, Query

from src.api.dependencies import DBDep
from src.schemas.facilities import RoomFacilitiesAdd
from src.schemas.rooms import RoomAdd, RoomEdit, RoomAddRequest, RoomForPatch

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    "/{hotel_id}/rooms",
    summary="Получить список номеров отеля",
    description="Получение списка свободных номеров отеля по его id на указанные даты"
)
async def get_hotel_rooms(
        hotel_id: int,
        db: DBDep,
        date_from: date = Query(example=date.today()),
        date_to: date = Query(example=date.today() + timedelta(days=7))
):
    rooms = await db.rooms.get_available_for_date(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
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
    room = await db.rooms.get_one_or_none(
        hotel_id=hotel_id,
        id=room_id,
        with_relations=True,
        relation_name="facilities"
    )

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
                        "quantity": 100,
                        "facilities_ids": [1, 2, 3]
                    }
                },
                "Lux": {
                    "value": {
                        "title": "Люкс",
                        "description": "Люкс 50 кв. м.",
                        "price": 2000,
                        "quantity": 50,
                        "facilities_ids": [1, 2, 3]
                    }
                },
                "Presidential": {
                    "value": {
                        "title": "Президентский номер",
                        "description": "Президентский номер 100 кв. м.",
                        "price": 5000,
                        "quantity": 10,
                        "facilities_ids": [1, 2, 3]
                    }
                }
            }
        )
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)
    facilities_for_room = [
        RoomFacilitiesAdd(room_id=room.id, facility_id=facility_id) for facility_id in room_data.facilities_ids
    ]
    await db.room_facilities.add_bulk(facilities_for_room)
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
    await db.room_facilities.set_room_facilities(room_id=room_id, facilities_ids=room_data.facilities_ids)
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
    _room_data_dict = room_data.model_dump(exclude_unset=True)
    _room_data = RoomForPatch(hotel_id=hotel_id, **_room_data_dict)
    await db.rooms.edit(data=_room_data, hotel_id=hotel_id, id=room_id, for_patch=True)
    if "facilities_ids" in _room_data_dict:
        await db.room_facilities.set_room_facilities(room_id=room_id, facilities_ids=_room_data_dict["facilities_ids"])
    await db.commit()
    return {"message": "Room updated"}
