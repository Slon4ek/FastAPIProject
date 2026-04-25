from datetime import date
from typing import Any

from sqlalchemy import select, func

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import HotelsDataMapper, HotelsWithRelationsDataMapper
from src.repositories.utils import get_available_rooms
from src.schemas.hotels import Hotel, HotelWithRelations


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelsDataMapper

    async def get_available_for_date(
        self,
        date_from: date,
        date_to: date,
        title: str | None = None,
        location: str | None = None,
        stars: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Hotel]:
        rooms_ids = get_available_rooms(date_from=date_from, date_to=date_to)
        hotels_ids = (
            select(RoomsOrm.hotel_id).select_from(RoomsOrm).filter(RoomsOrm.id.in_(rooms_ids))
        )
        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids))
        if stars:
            query = query.filter_by(stars=stars)
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))

        return [self.mapper().map_to_domain_entity(hotel) for hotel in result.scalars().all()]

    async def get_one(
        self, with_relations=True, relations_name: list[str] | None = None, **filter_by: Any
    ) -> Hotel | HotelWithRelations:
        relations_name = relations_name or ["rooms", "images"]
        if with_relations:
            self.mapper = HotelsWithRelationsDataMapper
        return await super().get_one(with_relations, relations_name, **filter_by)
