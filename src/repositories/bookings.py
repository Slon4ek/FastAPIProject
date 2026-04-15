from datetime import date

from sqlalchemy import select

from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingsDataMapper


class BookingRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingsDataMapper

    async def get_booking_with_today_checkin(self) -> list[BookingsOrm]:
        qwery = (
            select(self.model)
            .filter(self.model.date_from == date.today())
        )
        result = await self.session.execute(qwery)
        return [self.mapper().map_to_domain_entity(booking) for booking in result.scalars().all()]
