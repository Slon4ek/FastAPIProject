from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.utils import get_available_rooms
from src.schemas.rooms import Room, RoomsWithRelations


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = RoomsWithRelations

    async def get_available_for_date(
            self,
            date_from: date,
            date_to: date,
            hotel_id: int
    ):
        available_rooms_query = get_available_rooms(
            date_from=date_from,
            date_to=date_to,
            hotel_id=hotel_id
        )
        result = await self.session.execute(available_rooms_query)
        rows = result.fetchall()

        room_ids = [row[0] for row in rows]
        query = (
            select(self.model)
            .options(selectinload(RoomsOrm.facilities))
            .filter(RoomsOrm.id.in_(room_ids))
        )
        result = await self.session.execute(query)
        rooms = [self.schema.model_validate(item, from_attributes=True) for item in result.scalars().all()]

        available_rooms_map = {row[0]: row[1] for row in rows}
        for room in rooms:
            if room.id in available_rooms_map:
                room.quantity = available_rooms_map[room.id]

        return rooms
