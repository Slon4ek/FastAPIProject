import typing
from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseModel

if typing.TYPE_CHECKING:
    from src.models import RoomsOrm
    from src.models import HotelsOrm


class ImagesOrm(BaseModel):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    image_dir_path: Mapped[str] = mapped_column(String(255))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True)
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    room: Mapped["RoomsOrm"] = relationship(back_populates="images")
    hotel: Mapped["HotelsOrm"] = relationship(back_populates="images")
