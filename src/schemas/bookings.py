from datetime import date

from pydantic import BaseModel, ConfigDict

from src.models.bookings import BookingsOrm


class BookingAddRequest(BaseModel):
    date_from: date
    date_to: date
    room_id: int
    hotel_id: int

class BookingAdd(BaseModel):
    user_id: int
    price: int
    date_from: date
    date_to: date
    room_id: int

class Booking(BookingAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)
