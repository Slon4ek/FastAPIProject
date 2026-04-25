from datetime import date
from sqlalchemy import select

from exceptions import NotAvailableError
from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingsDataMapper
from src.repositories.utils import get_available_rooms
from src.schemas.bookings import BookingAdd, Booking


class BookingRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingsDataMapper

    async def get_booking_with_today_checkin(self) -> list[Booking]:
        qwery = select(self.model).filter(self.model.date_from == date.today())
        result = await self.session.execute(qwery)
        return [self.mapper().map_to_domain_entity(booking) for booking in result.scalars().all()]

    async def add_booking(self, data: BookingAdd, hotel_id: int) -> Booking:
        qwery = get_available_rooms(
            date_from=data.date_from, date_to=data.date_to, hotel_id=hotel_id
        )
        rooms_ids_available_for_book = (await self.session.execute(qwery)).scalars().all()

        if data.room_id not in rooms_ids_available_for_book:
            raise NotAvailableError

        return await self.add(data)
