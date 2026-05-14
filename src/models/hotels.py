import typing
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from src.database import BaseModel

if typing.TYPE_CHECKING:
    from src.models import RoomsOrm
    from src.models import ImagesOrm


class HotelsOrm(BaseModel):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    stars: Mapped[int]
    location: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    rooms: Mapped[list["RoomsOrm"]] = relationship(back_populates="hotel")
    images: Mapped[list["ImagesOrm"]] = relationship(back_populates="hotel")
