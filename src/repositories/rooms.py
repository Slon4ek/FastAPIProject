from sqlalchemy import select

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    name = "Room"
    table_name = "rooms"
    schema = Room

    async def get_all(self, hotel_id: int):
        query = select(self.model).filter_by(hotel_id=hotel_id)
        result = await self.session.execute(query)
        return [room for room in result.scalars().all()]

