from pydantic import BaseModel, Field, ConfigDict

from src.schemas.images import Image
from src.schemas.rooms import Room


class HotelAdd(BaseModel):
    title: str
    stars: int
    location: str


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HotelWithRelations(Hotel):
    rooms: list[Room]
    images: list[Image]


class HotelPatch(BaseModel):
    title: str | None = Field(None, description="Название отеля")
    stars: int | None = Field(None, description="Количество звезд")
    location: str | None = Field(None, description="Адрес отеля")
