from datetime import date

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.utils import get_available_rooms
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

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
        rooms = await self.get_all_by_filter(RoomsOrm.id.in_(room_ids))

        available_rooms_map = {row[0]: row[1] for row in rows}
        for room in rooms:
            if room.id in available_rooms_map:
                room.quantity = available_rooms_map[room.id]

        return rooms

