from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class BookingAddRequest(BaseModel):
    date_from: date
    date_to: date
    room_id: int

    @field_validator("date_from")
    @classmethod
    def validate_date_from(cls, v: Any) -> Any:
        if v < date.today():
            raise ValueError("Date must be in the future")
        return v

    @field_validator("date_to")
    @classmethod
    def validate_date_to(cls, v: Any) -> Any:
        if v < date.today():
            raise ValueError("Date must be in the future")
        return v


class BookingAdd(BaseModel):
    user_id: int
    price: int
    date_from: date
    date_to: date
    room_id: int


class Booking(BookingAdd):
    id: int
    total_price: int | None = None

    model_config = ConfigDict(from_attributes=True)
