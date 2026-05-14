from datetime import date
from typing import Optional

from src.exceptions import (
    NotFoundError,
    RelationshipError,
    FacilityNotFoundException,
    HotelNotFoundError,
)
from src.schemas.facility import RoomFacilitiesAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomEdit, RoomForPatch
from src.services.base import BaseService
from src.utils.db_manager import DBManager


class RoomsService(BaseService):
    db: DBManager
    hotel_id: int
    _hotel: Optional = None

    def __init__(self, db: DBManager, hotel_id: int) -> None:
        super().__init__(db)
        self.hotel_id = hotel_id
        self._hotel = None

    async def _ensure_hotel(self):
        if self._hotel is None:
            try:
                self._hotel = await self.db.hotels.get_one(with_relations=False, id=self.hotel_id)
            except NotFoundError:
                raise HotelNotFoundError
        return self._hotel

    async def get_hotel(self):
        return await self._ensure_hotel()

    async def get_hotel_rooms(self, date_from: date, date_to: date):
        """Получить доступные номера отеля на указанные даты."""
        await self._ensure_hotel()  # убедимся, что отель существует
        return await self.db.rooms.get_available_for_date(
            hotel_id=self.hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(self, room_id: int):
        """Получить номер отеля по ID."""
        await self._ensure_hotel()
        return await self.db.rooms.get_one(
            hotel_id=self.hotel_id,
            id=room_id,
            with_relations=True,
            relations_name=["facilities", "images"],
        )

    async def create_room(self, room_data: RoomAddRequest):
        """Создать номер в отеле."""
        await self._ensure_hotel()
        _room_data = RoomAdd(hotel_id=self.hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(_room_data)
        if room_data.facilities_ids:
            facilities_for_room = [
                RoomFacilitiesAdd(room_id=room.id, facility_id=facility_id)
                for facility_id in room_data.facilities_ids
            ]
            try:
                await self.db.room_facilities.add_bulk(facilities_for_room)
            except RelationshipError as e:
                raise FacilityNotFoundException from e
        await self.db.commit()
        return room

    async def update_room(
        self,
        room_id: int,
        room_data: RoomAddRequest | RoomEdit,
        for_patch: bool = False,
    ) -> None:
        """Обновить номер отеля."""
        await self._ensure_hotel()
        _room_data_dict = room_data.model_dump(exclude_unset=True)
        if for_patch:
            _room_data = RoomForPatch(
                hotel_id=self.hotel_id, **room_data.model_dump(exclude_unset=for_patch)
            )
        else:
            _room_data = RoomAdd(
                hotel_id=self.hotel_id, **room_data.model_dump(exclude_unset=for_patch)
            )

        result = await self.db.rooms.edit(
            data=_room_data, hotel_id=self.hotel_id, id=room_id, exclude_unset=for_patch
        )
        if "facilities_ids" in _room_data_dict:
            await self.db.room_facilities.set_room_facilities(
                room_id=room_id, facilities_ids=room_data.facilities_ids
            )
        if not result.rowcount:
            raise NotFoundError
        await self.db.commit()

    async def delete_room(self, room_id: int) -> None:
        """Удалить номер отеля."""
        await self._ensure_hotel()
        result = await self.db.rooms.delete(hotel_id=self.hotel_id, id=room_id)
        if not result.rowcount:
            raise NotFoundError
        await self.db.commit()
