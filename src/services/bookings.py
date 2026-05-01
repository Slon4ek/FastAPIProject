from src.schemas.bookings import BookingAddRequest, BookingAdd, Booking
from src.services.base import BaseService
from src.utils.db_manager import DBManager


class BookingService(BaseService):
    db: DBManager

    async def get_all_bookings(self):
        return await self.db.bookings.get_all()

    async def get_user_bookings(self, user_id: int):
        return await self.db.bookings.get_all_by_filter(user_id=user_id)

    async def create_booking(self, user_id: int, data: BookingAddRequest) -> Booking:
        room = await self.db.rooms.get_one(id=data.room_id)
        _booking_data = BookingAdd(user_id=user_id, price=room.price, **data.model_dump())
        booking = await self.db.bookings.add_booking(data=_booking_data, hotel_id=room.hotel_id)
        await self.db.commit()
        return booking
