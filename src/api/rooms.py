from fastapi import APIRouter

from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import RoomAdd, RoomEdit

router = APIRouter(prefix="/hotels", tags=["Номера"])

@router.get("/{hotel_id}/rooms")
async def get_hotel_rooms(
        hotel_id: int
):
    async with async_session_maker() as session:
        rooms = await RoomsRepository(session).get_all(hotel_id)
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
        room_data: RoomAdd
):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(room_data)
        await session.commit()
        return {"message": "Room created", "room": room}

@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
        hotel_data: RoomEdit,
        hotel_id: int,
        room_id: int
):

    async with async_session_maker() as session:
        await RoomsRepository(session).edit(data=hotel_data, hotel_id=hotel_id, id=room_id)
        await session.commit()
        return {"message": "Room updated", "room": hotel_data}

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
        hotel_data: RoomEdit,
        hotel_id: int,
        room_id: int
):

    async with async_session_maker() as session:
        await RoomsRepository(session).edit(data=hotel_data, hotel_id=hotel_id, id=room_id, for_patch=True)
        await session.commit()
        return {"message": "Room updated", "room": hotel_data}