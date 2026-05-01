import typing
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import BaseModel

if typing.TYPE_CHECKING:
    from src.models import RoomsOrm


class FacilitiesOrm(BaseModel):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        back_populates="facilities", secondary="rooms_facilities"
    )


class RoomsFacilitiesOrm(BaseModel):
    __tablename__ = "rooms_facilities"

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        primary_key=True,
    )
    facility_id: Mapped[int] = mapped_column(
        ForeignKey("facilities.id", ondelete="CASCADE"),
        primary_key=True,
    )
