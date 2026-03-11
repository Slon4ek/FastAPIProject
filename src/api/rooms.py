from fastapi import APIRouter, Body

from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import RoomAdd, RoomEdit, RoomAddRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_hotel_rooms(
        hotel_id: int
):
    async with async_session_maker() as session:
        rooms = await RoomsRepository(session).get_all_by_filter(hotel_id=hotel_id)
        return {"rooms": rooms}


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
        hotel_id: int,
        room_id: int
):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).get_one_or_none(hotel_id=hotel_id, id=room_id)

        if room is None:
            return {"message": "Room not found"}

        return {"room": room}


@router.post("/{hotel_id}/rooms")
async def create_room(
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
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(_room_data)
        await session.commit()
        return {"message": "Room created", "room": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
        room_data: RoomAddRequest,
        hotel_id: int,
        room_id: int
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(data=_room_data, hotel_id=hotel_id, id=room_id)
        await session.commit()
        return {"message": "Room updated", "room": room_data}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
        hotel_id: int,
        room_id: int
):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(hotel_id=hotel_id, id=room_id)
        await session.commit()
        return {"message": "Room deleted"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_update_room(
        room_data: RoomEdit,
        hotel_id: int,
        room_id: int
):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(data=room_data, hotel_id=hotel_id, id=room_id, for_patch=True)
        await session.commit()
        return {"message": "Room updated", "room": room_data}
