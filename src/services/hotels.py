from datetime import date

from src.api.dependencies import PaginationDep
from src.exceptions import NotFoundError
from src.schemas.hotels import Hotel, HotelAdd, HotelPatch
from src.services.base import BaseService
from src.utils.db_manager import DBManager


class HotelsService(BaseService):
    db: DBManager

    async def add_hotel(self, hotel_data: HotelAdd) -> Hotel:
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return hotel

    async def get_hotels(
        self,
        pagination: PaginationDep,
        date_from: date | None = None,
        date_to: date | None = None,
        stars: int | None = None,
        title: str | None = None,
        location: str | None = None,
    ) -> list[Hotel]:
        per_page = pagination.per_page or 5

        if not date_from or not date_to:
            return await self.db.hotels.get_all()

        return await self.db.hotels.get_available_for_date(
            stars=stars,
            title=title,
            location=location,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
            date_from=date_from,
            date_to=date_to,
        )

    async def get_hotel(self, hotel_id: int) -> Hotel:
        return await self.db.hotels.get_one(id=hotel_id)

    async def edit_hotel(
        self, data: HotelAdd | HotelPatch, hotel_id: int, for_patch: bool = False
    ) -> None:
        result = await self.db.hotels.edit(data=data, id=hotel_id, exclude_unset=for_patch)
        if not result.rowcount:
            raise NotFoundError
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int) -> None:
        result = await self.db.hotels.delete(id=hotel_id)
        if not result.rowcount:
            raise NotFoundError
        await self.db.commit()
