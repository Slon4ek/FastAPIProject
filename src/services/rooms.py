from datetime import date

from src.exceptions import NotFoundError
from src.schemas.facility import RoomFacilitiesAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomEdit, RoomForPatch
from src.services.base import BaseService
from src.utils.db_manager import DBManager


class RoomsService(BaseService):
    db: DBManager

    async def get_hotel_rooms(self, hotel_id: int, date_from: date, date_to: date):
        return await self.db.rooms.get_available_for_date(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(self, hotel_id: int, room_id: int):
        return await self.db.rooms.get_one(
            hotel_id=hotel_id,
            id=room_id,
            with_relations=True,
            relations_name=["facilities", "images"],
        )

    async def create_room(self, hotel_id: int, room_data: RoomAddRequest):
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(_room_data)
        if room_data.facilities_ids:
            facilities_for_room = [
                RoomFacilitiesAdd(room_id=room.id, facility_id=facility_id)
                for facility_id in room_data.facilities_ids
            ]
            await self.db.room_facilities.add_bulk(facilities_for_room)
        await self.db.commit()
        return room

    async def update_room(
        self,
        hotel_id: int,
        room_id: int,
        room_data: RoomAddRequest | RoomEdit,
        for_patch: bool = False,
    ) -> None:
        _room_data_dict = room_data.model_dump(exclude_unset=True)
        if for_patch:
            _room_data = RoomForPatch(
                hotel_id=hotel_id, **room_data.model_dump(exclude_unset=for_patch)
            )
        else:
            _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=for_patch))

        result = await self.db.rooms.edit(
            data=_room_data, hotel_id=hotel_id, id=room_id, exclude_unset=for_patch
        )
        if "facilities_ids" in _room_data_dict:
            await self.db.room_facilities.set_room_facilities(
                room_id=room_id, facilities_ids=room_data.facilities_ids
            )
        if result.rowcount:
            await self.db.commit()
        else:
            await self.db.rollback()
            raise NotFoundError

    async def delete_room(self, hotel_id: int, room_id: int) -> None:
        result = await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        if result.rowcount:
            await self.db.commit()
        else:
            await self.db.rollback()
            raise NotFoundError
