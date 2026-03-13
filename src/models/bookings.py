from datetime import date, datetime

from sqlalchemy import ForeignKey, func, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from src.database import BaseModel


class BookingsOrm(BaseModel):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date_from: Mapped[date]
    date_to: Mapped[date]
    price: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    @hybrid_property
    def total_price(self):
        return self.price * (self.date_to - self.date_from).days

    @total_price.expression
    def total_price(cls) -> int:
        return cls.price * func.date_part('day', cls.date_to - cls.date_from)

