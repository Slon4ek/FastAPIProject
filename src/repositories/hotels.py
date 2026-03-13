from sqlalchemy import select, func

from src.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

    async def get_all_by_filter(
            self,
            title,
            location,
            stars,
            limit,
            offset
    ) -> list[Hotel]:
        qwery = select(self.model)
        if stars:
            qwery = qwery.filter_by(stars=stars)
        if title:
            qwery = qwery.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        if location:
            qwery = qwery.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        qwery = (
            qwery
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(qwery)
        # print(qwery.compile(engine, compile_kwargs={"literal_binds": True}))
        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]
