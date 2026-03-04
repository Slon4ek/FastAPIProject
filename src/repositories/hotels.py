from sqlalchemy import select, func

from src.models.hotels import HotelsModel
from src.repositories.base import BaseRepository

class HotelsRepository(BaseRepository):
    model = HotelsModel

    async def get_all(
            self,
            title,
            location,
            stars,
            limit,
            offset
    ):
        qwery = select(self.model)
        if stars:
            qwery = qwery.filter_by(stars=stars)
        if title:
            qwery = qwery.filter(func.lower(HotelsModel.title).contains(title.strip().lower()))
        if location:
            qwery = qwery.filter(func.lower(HotelsModel.location).contains(location.strip().lower()))
        qwery = (
            qwery
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(qwery)
        # print(qwery.compile(engine, compile_kwargs={"literal_binds": True}))
        return result.scalars().all()