from datetime import date
from sqlalchemy import select, func

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.utils import get_available_rooms
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

    # async def get_all(
    #         self,
    #         title,
    #         location,
    #         stars,
    #         limit,
    #         offset,
    #         date_from,
    #         date_to
    # ) -> list[Hotel]:
    #     qwery = select(self.model)
    #     if stars:
    #         qwery = qwery.filter_by(stars=stars)
    #     if title:
    #         qwery = qwery.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
    #     if location:
    #         qwery = qwery.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
    #     qwery = (
    #         qwery
    #         .limit(limit)
    #         .offset(offset)
    #     )
    #     result = await self.session.execute(qwery)
    #     # print(qwery.compile(engine, compile_kwargs={"literal_binds": True}))
    #     return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]


    async def get_available_for_date(
            self,
            date_from: date,
            date_to: date,
            title: str,
            location: str,
            stars: int,
            limit: int,
            offset: int,
    ):
        rooms_ids = get_available_rooms(date_from=date_from, date_to=date_to)
        hotels_ids = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids))
        )
        if stars:
            hotels_ids = hotels_ids.filter(HotelsOrm.stars == stars)
        if title:
            hotels_ids = hotels_ids.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        if location:
            hotels_ids = hotels_ids.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        hotels_ids = (
            hotels_ids
            .limit(limit)
            .offset(offset)
        )
        return await self.get_all_by_filter(HotelsOrm.id.in_(hotels_ids))
