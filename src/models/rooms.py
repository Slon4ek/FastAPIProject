import typing
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseModel

if typing.TYPE_CHECKING:
    from src.models import FacilitiesOrm
    from src.models import ImagesOrm
    from src.models import HotelsOrm


class RoomsOrm(BaseModel):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates="rooms", secondary="rooms_facilities"
    )

    images: Mapped[list["ImagesOrm"]] = relationship(back_populates="room")
    hotel: Mapped["HotelsOrm"] = relationship(back_populates="rooms")
